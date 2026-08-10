"""Resend HTTPS API + traveler-voiced HTML invite email.

Design: boarding pass strip + passport-stamped hero + torn tape + luggage tag +
paper-plane CTA + postcard-back footer. Tables + inline CSS = email-client safe.
"""

from __future__ import annotations

import logging
import os
import random
import uuid
from datetime import datetime, timezone

from quotes import COUNTRY_STAMP_HINTS, INVITE_HERO_IMAGES, TRAVEL_QUOTES

log = logging.getLogger(__name__)
