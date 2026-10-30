import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import oauth


class OAuthTests(unittest.TestCase):
    def test_authorization_uses_current_mobile_client_and_pkce(self):
        params = oauth.authorization_params("challenge", "state123")

        self.assertEqual(params["client_id"], "mo2qy9h_10")
        self.assertEqual(params["redirect_uri"], oauth.REDIRECT_URI)
        self.assertEqual(params["code_challenge"], "challenge")
        self.assertEqual(params["code_challenge_method"], "S256")
        self.assertEqual(params["state"], "state123")
        self.assertNotIn("response_mode", params)

    def test_pkce_pair_matches_s256_challenge(self):
        verifier, challenge = oauth.create_pkce_pair()

        import base64
        import hashlib

        expected = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        self.assertEqual(challenge, expected)
        self.assertGreaterEqual(len(verifier), 43)

    def test_extracts_escaped_login_action_and_page_id(self):
        html = r'''<script>const kcContext = {
            "pageId": "login-otp-email",
            "url": {"loginAction": "https:\/\/auth.volvocars.com\/next?a=1&amp;b=2"}
        };</script>'''

        self.assertEqual(oauth.extract_page_id(html), "login-otp-email")
        self.assertEqual(
            oauth.extract_login_action(html),
            "https://auth.volvocars.com/next?a=1&b=2",
        )

    def test_extracts_code_from_mobile_callback(self):
        callback = oauth.REDIRECT_URI + "?code=abc123&state=state123"
        self.assertEqual(oauth.extract_authorization_code(callback, "state123"), "abc123")

    def test_rejects_non_mobile_callback(self):
        with self.assertRaises(oauth.OAuthError):
            oauth.extract_authorization_code(
                "https://example.com/?code=abc123&state=state123",
                "state123",
            )

    def test_rejects_wrong_callback_host_or_state(self):
        with self.assertRaises(oauth.OAuthError):
            oauth.extract_authorization_code(
                "vca://attacker.invalid/l/vca/oauth/callback?code=abc123&state=state123",
                "state123",
            )
        with self.assertRaises(oauth.OAuthError):
            oauth.extract_authorization_code(
                oauth.REDIRECT_URI + "?code=abc123&state=wrong",
                "state123",
            )

    def test_rejects_untrusted_credential_and_redirect_urls(self):
        session = Mock()
        with self.assertRaises(oauth.OAuthError):
            oauth.submit_credentials(session, "https://attacker.example/login", "user", "pass")
        with self.assertRaises(oauth.OAuthError):
            oauth.submit_otp(session, "http://volvoid.eu.volvocars.com/otp", "123456")

        response = Mock(
            url="https://volvoid.eu.volvocars.com/step",
            headers={"location": "https://attacker.example/redirect"},
        )
        with self.assertRaises(oauth.OAuthError):
            oauth.follow_redirects_to_callback(session, response)

    def test_follows_http_redirects_until_mobile_callback(self):
        session = Mock()
        first = Mock(
            url="https://auth.volvocars.com/step",
            headers={"location": "https://volvoid.eu.volvocars.com/callback"},
        )
        second = Mock(
            url="https://volvoid.eu.volvocars.com/callback",
            headers={"location": oauth.REDIRECT_URI + "?code=abc123&state=state123"},
        )
        session.get.return_value = second

        callback = oauth.follow_redirects_to_callback(session, first)

        self.assertEqual(callback, oauth.REDIRECT_URI + "?code=abc123&state=state123")
        session.get.assert_called_once_with(
            "https://volvoid.eu.volvocars.com/callback",
            timeout=30,
            allow_redirects=False,
        )

    def test_code_exchange_includes_public_client_id(self):
        session = Mock()
        session.post.return_value.status_code = 200
        session.post.return_value.json.return_value = {"access_token": "access"}

        result = oauth.exchange_code(
            session,
            oauth.REDIRECT_URI + "?code=abc123&state=state123",
            "verifier",
            "state123",
        )

        self.assertEqual(result["access_token"], "access")
        _, kwargs = session.post.call_args
        self.assertEqual(kwargs["data"]["client_id"], oauth.CLIENT_ID)
        self.assertEqual(kwargs["data"]["code"], "abc123")
        self.assertEqual(kwargs["data"]["code_verifier"], "verifier")

    def test_refresh_error_distinguishes_invalid_grant_from_transient_failure(self):
        invalid = Mock(status_code=400)
        invalid.json.return_value = {
            "error": "invalid_grant",
            "error_description": "Grant revoked",
        }
        error = oauth._oauth_error(invalid, "fallback")
        self.assertTrue(error.requires_login())

        transient = Mock(status_code=503)
        transient.json.return_value = {"error": "temporarily_unavailable"}
        error = oauth._oauth_error(transient, "fallback")
        self.assertFalse(error.requires_login())

    @patch("oauth.requests.post")
    def test_refresh_uses_public_client_without_legacy_basic_auth(self, post):
        post.return_value.status_code = 200
        post.return_value.json.return_value = {"access_token": "access"}

        result = oauth.refresh("refresh", "vca-android/7.2.0")

        self.assertEqual(result["access_token"], "access")
        _, kwargs = post.call_args
        self.assertEqual(
            kwargs["data"],
            {
                "grant_type": "refresh_token",
                "client_id": oauth.CLIENT_ID,
                "refresh_token": "refresh",
            },
        )
        self.assertNotIn("authorization", {k.lower(): v for k, v in kwargs["headers"].items()})


if __name__ == "__main__":
    unittest.main()
