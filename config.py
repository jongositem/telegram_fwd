import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for the Telegram forwarding bot"""

    # Telegram API credentials
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    PHONE_NUMBER = os.getenv('PHONE_NUMBER')

    # Contacts
    CONTACT_A = os.getenv('CONTACT_A')
    CONTACT_B = os.getenv('CONTACT_B')

    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required = ['API_ID', 'API_HASH', 'PHONE_NUMBER', 'CONTACT_A', 'CONTACT_B']
        missing = [field for field in required if not getattr(cls, field)]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        return True
