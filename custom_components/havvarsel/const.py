"""Constants for the Havvarsel integration."""

DOMAIN = "havvarsel"

# Config entry fields
CONF_LONGITUDE = "longitude"
CONF_LATITUDE = "latitude"
CONF_DEPTH = "depth"
CONF_SENSOR_NAME = "sensor_name"

# Default values
DEFAULT_DEPTH = 0
DEFAULT_SENSOR_NAME = "Sea Temperature"

# Update interval
UPDATE_INTERVAL = 600  # 10 minutes in seconds

# API endpoints
API_BASE_URL = "https://api.havvarsel.no/apis/duapi/havvarsel/v2/"
API_PROJECTION_URL = f"{API_BASE_URL}temperatureprojection"
API_VARIABLES_URL = f"{API_BASE_URL}variables"
