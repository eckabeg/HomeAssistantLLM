import requests
from fastmcp import FastMCP

HASS_URL = "http://localhost:8000"
HASS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI4Yzg3NmE3ZWJmOWU0ZDc2YTkxMDg5OTZlYjNlOWYxNSIsImlhdCI6MTc0Njc4MTU3NCwiZXhwIjoyMDYyMTQxNTc0fQ.odURYTbRy1aU1GmUqZgUET_lNhX4rUSeUYjHBD1qZVM"
HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

mcp = FastMCP("HomeAssistant")

@mcp.tool()
def turn_on_light(entity_id: str) -> str:
    """
    Turns on a light in Home Assistant.
    Parameters:
        - entity_id: ex.: "light.living_room" or "light.kitchen"
    Return:
    Status as string.
    """
    url = f"{HASS_URL}/api/services/light/turn_on"
    payload = {"entity_id": entity_id}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return f"Light {entity_id} turned on."
    else:
        return f"Error turning on light {entity_id}: {response.text}"

@mcp.tool()
def turn_off_light(entity_id: str) -> str:
    """
    Turns off a light in Home Assistant.
    Parameters:
        - entity_id: ex.: "light.living_room" or "light.kitchen"
    Return:
    Status as string.
    """
    url = f"{HASS_URL}/api/services/light/turn_off"
    payload = {"entity_id": entity_id}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return f"Light {entity_id} was turned off."
    else:
        return f"Error turning off light {entity_id}: {response.text}"

@mcp.tool()
def set_temperature(entity_id: str, temperature: float) -> str:
    """
    Setting the temperature of a thermostat in Home Assistant.
    Parameter:
      - entity_id: ex. "climate.thermostat_living_room"
      - temperature: Goal temperature (ex. 21.5)
    """
    url = f"{HASS_URL}/api/services/climate/set_temperature"
    payload = {
        "entity_id": entity_id,
        "temperature": temperature
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return f"Set Thermostat {entity_id} to {temperature} °C."
    else:
        return f"Error on setting temperature: {response.text}"


if __name__ == "__main__":
    mcp.run()