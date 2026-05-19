import os

from slowapi import Limiter
from slowapi.util import get_remote_address


_enabled = os.environ.get("RATE_LIMIT_ENABLED", "1") != "0"

limiter = Limiter(key_func=get_remote_address, enabled=_enabled)
