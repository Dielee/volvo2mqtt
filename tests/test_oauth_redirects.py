import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import oauth


class RedirectSafetyTests(unittest.TestCase):
    def test_volvo_http_resume_is_fetched_only_over_https(self):
        session = Mock()
        first = Mock(
            url="https://auth.volvocars.com/otp",
            headers={
                "location": (
                    "http://volvoid.eu.volvocars.com/as/transaction/"
                    "resume/as/authorization.ping"
                )
            },
        )
        session.get.return_value = Mock(
            url=(
                "https://volvoid.eu.volvocars.com/as/transaction/"
                "resume/as/authorization.ping"
            ),
            headers={"location": oauth.REDIRECT_URI + "?code=abc&state=xyz"},
        )

        callback = oauth.follow_redirects_to_callback(session, first)

        self.assertEqual(
            callback,
            oauth.REDIRECT_URI + "?code=abc&state=xyz",
        )
        session.get.assert_called_once_with(
            "https://volvoid.eu.volvocars.com/as/transaction/"
            "resume/as/authorization.ping",
            timeout=30,
            allow_redirects=False,
        )

    def test_http_upgrade_is_limited_to_volvo_resume_endpoint(self):
        urls = [
            "http://attacker.invalid/as/t/resume/as/authorization.ping",
            "http://volvoid.eu.volvocars.com.attacker.invalid/as/t/resume/as/authorization.ping",
            "http://auth.volvocars.com/as/t/resume/as/authorization.ping",
            "http://volvoid.eu.volvocars.com:8080/as/t/resume/as/authorization.ping",
            "http://user@volvoid.eu.volvocars.com/as/t/resume/as/authorization.ping",
            "http://volvoid.eu.volvocars.com/other",
        ]
        for url in urls:
            with self.subTest(url=url):
                upgraded = oauth.upgrade_identity_redirect(url)
                self.assertEqual(upgraded, url)
                with self.assertRaises(oauth.OAuthError):
                    oauth.validate_identity_url(upgraded)

    def test_credentials_follow_only_validated_get_redirect(self):
        session = Mock()
        session.post.return_value = Mock(
            status_code=302,
            url="https://auth.volvocars.com/login",
            headers={"location": "/otp"},
        )
        session.get.return_value = Mock(
            status_code=200,
            text=(
                '{"pageId":"login-otp-email",'
                '"loginAction":"https://auth.volvocars.com/check?a=1&amp;b=2"}'
            ),
        )

        action = oauth.submit_credentials(
            session,
            "https://auth.volvocars.com/login",
            "user",
            "pass",
        )

        self.assertEqual(action, "https://auth.volvocars.com/check?a=1&b=2")
        self.assertIs(session.post.call_args.kwargs["allow_redirects"], False)
        session.get.assert_called_once_with(
            "https://auth.volvocars.com/otp",
            timeout=30,
            allow_redirects=False,
        )

    def test_credentials_are_not_forwarded_to_foreign_redirect(self):
        session = Mock()
        session.post.return_value = Mock(
            status_code=302,
            url="https://auth.volvocars.com/login",
            headers={"location": "https://attacker.invalid/capture"},
        )

        with self.assertRaises(oauth.OAuthError):
            oauth.submit_credentials(
                session,
                "https://auth.volvocars.com/login",
                "user",
                "pass",
            )

        session.get.assert_not_called()
        self.assertEqual(session.post.call_count, 1)
        self.assertIs(session.post.call_args.kwargs["allow_redirects"], False)

    def test_credentials_are_never_replayed_after_307_or_308(self):
        for status in (307, 308):
            with self.subTest(status=status):
                session = Mock()
                session.post.return_value = Mock(
                    status_code=status,
                    url="https://auth.volvocars.com/login",
                    headers={"location": "https://auth.volvocars.com/other"},
                )

                with self.assertRaises(oauth.OAuthError):
                    oauth.submit_credentials(
                        session,
                        "https://auth.volvocars.com/login",
                        "user",
                        "pass",
                    )

                session.get.assert_not_called()
                self.assertEqual(session.post.call_count, 1)
                self.assertIs(
                    session.post.call_args.kwargs["allow_redirects"],
                    False,
                )

    @patch("oauth.requests.post")
    def test_tokens_are_not_forwarded_on_redirect(self, post):
        post.return_value = Mock(status_code=307)
        post.return_value.json.side_effect = ValueError("not JSON")

        with self.assertRaises(oauth.OAuthError):
            oauth.refresh("refresh", "agent")
        self.assertIs(post.call_args.kwargs["allow_redirects"], False)

        session = Mock()
        session.post.return_value = post.return_value
        with self.assertRaises(oauth.OAuthError):
            oauth.exchange_code(
                session,
                oauth.REDIRECT_URI + "?code=abc&state=xyz",
                "verifier",
                "xyz",
            )
        self.assertIs(session.post.call_args.kwargs["allow_redirects"], False)


if __name__ == "__main__":
    unittest.main()
