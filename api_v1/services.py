from pip import logger

import clearbit
from email_hunter import EmailHunterClient

from .settings import EMAIL_HUNTER_KEY, CLEARBIT_KEY

# initializing 3rd party clients
clearbit.key = CLEARBIT_KEY
email_hunter_client = EmailHunterClient(EMAIL_HUNTER_KEY)


def get_user_extra_info(email):
    """
    This function should expand user's profile by info provided from clearbit.com
    Registration available only for US citizens.
    Getting sign up error "For security reasons, we need to confirm your phone number."
    """
    data = {}
    # response = clearbit.Enrichment.find(email=email, stream=True)

    # making stub intentionally
    response = {}

    if 'person' in response:
        data = {
            'first_name': response['person']['name']['givenName'],
            'last_name': response['person']['name']['familyName']
        }

    return data


def verify_user_email(email) -> bool:
    """
    Checks email address for existence
    :param email: Email for existence verification in "Email Hunter" service
    :return: Boolean
    """
    exists = False

    try:
        # Check if a given email address is deliverable and has been found on the internet.
        # I've chosen this method because there was no explicit requirements about verification in
        # task description.
        exists = _user_email_deliverable(email)

        # Checks for existence in Email Hunter database.
        # Don't think this is what we need.
        # exists = _user_email_exists(email)
    except Exception as e:
        logger.error(f"Email verification with Email Hunter service failed. {e.args[-1]}")

    return exists


def _user_email_exists(email) -> bool:
    """
    Check for existence in Email Hunter database
    :param email: Email
    :return: Boolean
    """
    return email_hunter_client.exist(email)[0]


def _user_email_deliverable(email) -> bool:
    """
    Check is email address deliverable
    :param email: Email
    :return: Boolean
    """
    exists = False
    response = email_hunter_client.verify(email)
    response = dict(response)

    if response.get('smtp_server') and response.get('smtp_check'):
        exists = True

    return exists



