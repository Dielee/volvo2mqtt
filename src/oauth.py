import base64
import hashlib
from html import unescape
import json
import re
import secrets
from urllib.parse import parse_qs, urljoin, urlparse

import requests

CLIENT_ID = "mo2qy9h_10"
REDIRECT_URI = "vca://www.volvocars.com/l/vca/oauth/callback"
AUTH_URL = "https://volvoid.eu.volvocars.com/as/authorization.oauth2"
TOKEN_URL = "https://volvoid.eu.volvocars.com/as/token.oauth2"
SCOPES = (
    "openid email profile "
    "care_by_volvo:financial_information:invoice:read "
    "care_by_volvo:financial_information:payment_method "
    "care_by_volvo:subscription:read customer:attributes "
    "customer:attributes:write order:attributes vehicle:attributes "
    "tsp_customer_api:all conve:brake_status conve:climatization_start_stop "
    "conve:command_accessibility conve:commands conve:diagnostics_engine_status "
    "conve:diagnostics_workshop conve:doors_status conve:engine_status "
    "conve:environment conve:fuel_status conve:honk_flash conve:lock "
    "conve:lock_status conve:navigation conve:odometer_status "
    "conve:trip_statistics conve:tyre_status conve:unlock "
    "conve:vehicle_relation conve:warnings conve:windows_status "
    "energy:battery_charge_level energy:charging_connection_status "
    "energy:charging_system_status energy:electric_range "
    "energy:estimated_charging_time energy:recharge_status"
)


class OAuthError(Exception):
    def __init__(self, message, status_code=None, error_code=None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code

    def requires_login(self):
        return self.error_code in ("invalid_grant", "invalid_client")


def create_pkce_pair():
    verifier = secrets.token_urlsafe(64)[:86]
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode("ascii")).digest()
    ).rstrip(b"=").decode("ascii")
    return verifier, challenge


def extract_context_string(html, key):
    match = re.search(
        r'"' + re.escape(key) + r'"\s*:\s*"((?:\\.|[^"\\])*)"',
        html,
    )
    if not match:
        return None
    return json.loads('"' + match.group(1) + '"')


def extract_login_action(html):
    action = extract_context_string(html, "loginAction")
    if not action:
        raise OAuthError("Volvo sign-in page did not contain a login action")
    return unescape(action)


def extract_page_id(html):
    return extract_context_string(html, "pageId")


def authorization_params(challenge, state):
    return {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "acr_values": "urn:volvoid:aal:bronze:2sv",
    }


def start_login(auth_session, user_agent):
    verifier, challenge = create_pkce_pair()
    state = secrets.token_urlsafe(32)
    auth_session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/json",
    })
    response = auth_session.get(
        AUTH_URL,
        params=authorization_params(challenge, state),
        timeout=30,
    )
    response.raise_for_status()
    return verifier, state, extract_login_action(response.text)


def submit_credentials(auth_session, action, username, password):
    validate_identity_url(action)
    response = auth_session.post(
        action,
        data={
            "username": username,
            "password": password,
            "rememberMe": "on",
            "credentialId": "",
            "login": "Sign in",
        },
        timeout=30,
        allow_redirects=False,
    )
    response = follow_identity_redirects(auth_session, response)
    response.raise_for_status()
    page_id = extract_page_id(response.text)
    if page_id != "login-otp-email":
        raise OAuthError("Volvo sign-in did not advance to email verification")
    return extract_login_action(response.text)


def follow_identity_redirects(auth_session, response, max_redirects=10):
    for _ in range(max_redirects + 1):
        if not 300 <= response.status_code < 400:
            return response
        if response.status_code not in (301, 302, 303):
            raise OAuthError("Refusing to replay credentials during Volvo sign-in")
        location = response.headers.get("location")
        if not location:
            raise OAuthError("Volvo sign-in redirect did not contain a location")
        location = urljoin(response.url, location)
        location = upgrade_identity_redirect(location)
        validate_identity_url(location)
        response = auth_session.get(location, timeout=30, allow_redirects=False)
    raise OAuthError("Too many redirects while submitting Volvo credentials")


def submit_otp(auth_session, action, otp):
    validate_identity_url(action)
    response = auth_session.post(
        action,
        data={"otp": otp, "login": "Verify"},
        timeout=30,
        allow_redirects=False,
    )
    return follow_redirects_to_callback(auth_session, response)


def follow_redirects_to_callback(auth_session, response, max_redirects=10):
    for _ in range(max_redirects + 1):
        location = response.headers.get("location")
        if not location:
            raise OAuthError("Volvo sign-in did not return an authorization callback")
        location = urljoin(response.url, location)
        location = upgrade_identity_redirect(location)
        if is_callback_url(location):
            return location
        validate_identity_url(location)
        response = auth_session.get(location, timeout=30, allow_redirects=False)
    raise OAuthError("Too many redirects while completing Volvo sign-in")


def upgrade_identity_redirect(url):
    """Upgrade Volvo's HTTP resume redirect without making an HTTP request."""
    parsed = urlparse(url)
    if (
        parsed.scheme == "http"
        and parsed.hostname == "volvoid.eu.volvocars.com"
        and parsed.port in (None, 80)
        and parsed.username is None
        and parsed.password is None
        and parsed.path.startswith("/as/")
        and parsed.path.endswith("/resume/as/authorization.ping")
    ):
        return parsed._replace(scheme="https", netloc=parsed.hostname).geturl()
    return url


def is_callback_url(url):
    parsed = urlparse(url)
    expected = urlparse(REDIRECT_URI)
    return (
        parsed.scheme == expected.scheme
        and parsed.netloc == expected.netloc
        and parsed.path == expected.path
    )


def validate_identity_url(url):
    parsed = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (
        hostname == "volvocars.com" or hostname.endswith(".volvocars.com")
    ):
        raise OAuthError("Unexpected Volvo identity URL")


def extract_authorization_code(callback_url, expected_state):
    parsed = urlparse(callback_url)
    if not is_callback_url(callback_url):
        raise OAuthError("Unexpected Volvo authorization callback URL")
    values = parse_qs(parsed.query)
    if values.get("error"):
        raise OAuthError(values.get("error_description", values["error"])[0])
    code = values.get("code", [None])[0]
    if not code:
        raise OAuthError("Volvo authorization callback did not contain a code")
    state = values.get("state", [None])[0]
    if not state or not secrets.compare_digest(state, expected_state):
        raise OAuthError("Volvo authorization callback state did not match")
    return code


def exchange_code(auth_session, callback_url, verifier, state):
    response = auth_session.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": extract_authorization_code(callback_url, state),
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
        },
        headers={"Accept": "application/json"},
        timeout=30,
        allow_redirects=False,
    )
    if response.status_code != 200:
        raise _oauth_error(response, "Authorization code exchange failed")
    return response.json()


def refresh(refresh_token, user_agent):
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "client_id": CLIENT_ID,
            "refresh_token": refresh_token,
        },
        headers={"Accept": "application/json", "User-Agent": user_agent},
        timeout=30,
        allow_redirects=False,
    )
    if response.status_code != 200:
        raise _oauth_error(response, "Refreshing credentials failed")
    return response.json()


def _oauth_error(response, fallback):
    try:
        payload = response.json()
    except ValueError:
        return OAuthError("%s (%s)" % (fallback, response.status_code), response.status_code)
    message = payload.get("error_description") or payload.get("message") or fallback
    return OAuthError(message, response.status_code, payload.get("error"))
