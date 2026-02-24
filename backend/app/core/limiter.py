from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize Rate Limiter here to avoid circular dependencies
limiter = Limiter(key_func=get_remote_address)
