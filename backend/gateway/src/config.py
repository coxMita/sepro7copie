import os

from dotenv import load_dotenv

load_dotenv()

BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL")
if not BOOKING_SERVICE_URL:
    raise RuntimeError("BOOKING_SERVICE_URL environment variable is not set")
DESK_INVENTORY_SERVICE_URL = os.getenv("DESK_INVENTORY_SERVICE_URL")
if not DESK_INVENTORY_SERVICE_URL:
    raise RuntimeError("DESK_INVENTORY_SERVICE_URL environment variable is not set")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
if not USER_SERVICE_URL:
    raise RuntimeError("USER_SERVICE_URL environment variable is not set")
OCCUPANCY_SERVICE_URL = os.getenv("OCCUPANCY_SERVICE_URL")
if not OCCUPANCY_SERVICE_URL:
    raise RuntimeError("OCCUPANCY_SERVICE_URL environment variable is not set")
DESK_INTEGRATION_SERVICE_URL = os.getenv("DESK_INTEGRATION_SERVICE_URL")
if not DESK_INTEGRATION_SERVICE_URL:
    raise RuntimeError("DESK_INTEGRATION_SERVICE_URL environment variable is not set")
SCHEDULING_SERVICE_URL = os.getenv("SCHEDULING_SERVICE_URL")
if not SCHEDULING_SERVICE_URL:
    raise RuntimeError("SCHEDULING_SERVICE_URL environment variable is not set")
