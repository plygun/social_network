"""App-level configuration for api_v1, sourced from environment."""
from decouple import config

HUNTER_API_KEY = config('HUNTER_API_KEY', default='')
CLEARBIT_API_KEY = config('CLEARBIT_API_KEY', default='')
