"""Thin wrappers around third-party email-intelligence APIs."""
import logging

import requests

from .settings import HUNTER_API_KEY

logger = logging.getLogger(__name__)

HUNTER_VERIFIER_URL = 'https://api.hunter.io/v2/email-verifier'


def get_user_extra_info(email: str) -> dict:
    """Enrich a user profile via Clearbit. Disabled — kept as integration stub."""
    # Clearbit signup is gated to US citizens with phone verification, so the
    # live call is not wired in. Return empty to keep callers safe.
    return {}


def verify_user_email(email: str) -> bool:
    """Return True when the email is deliverable per Hunter.io.

    Falls open (returns True) when no API key is configured or the call fails —
    a registration-time check shouldn't block signup on a third-party outage.
    """
    if not HUNTER_API_KEY:
        return True

    try:
        response = requests.get(
            HUNTER_VERIFIER_URL,
            params={'email': email, 'api_key': HUNTER_API_KEY},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json().get('data', {})
        return data.get('status') == 'valid' or data.get('result') == 'deliverable'
    except requests.RequestException as exc:
        logger.warning("Hunter.io verification failed for %s: %s", email, exc)
        return True
