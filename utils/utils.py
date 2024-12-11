from google.oauth2 import service_account
import json
import base64

async def get_credentials_from_env() -> service_account.Credentials:
    """
    Gets credentials from env vars
    """
    info: dict = json.loads(base64.b64decode(config.GCP_SERVICE_ACCOUNT))
    return service_account.Credentials.from_service_account_info(info)