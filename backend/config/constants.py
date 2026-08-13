"""
Backend configuration constants for DK Travel.
"""

# Pagination
MAX_RESULTS = 50
DEFAULT_PAGE_SIZE = 10

# Authentication
TOKEN_EXPIRY_HOURS = 24
REFRESH_TOKEN_EXPIRY_DAYS = 30

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60

# File Uploads
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Search
MIN_SEARCH_LENGTH = 2
SEARCH_RESULTS_LIMIT = 20
