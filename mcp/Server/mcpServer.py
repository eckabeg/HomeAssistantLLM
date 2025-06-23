import requests
from fastmcp import FastMCP

HASS_URL = "http://localhost:9090"
HASS_TOKEN = ""
HEADERS = {
    "Authorization": f"Bearer {HASS_TOKEN}",
    "Content-Type": "application/json"
}

mcp = FastMCP("HomeAssistant")

ROOM_NAME_MAP = {
    "wohnzimmer": "living_room",
    "küche": "kitchen",
    "schlafzimmer": "bedroom",
    "badezimmer": "bathroom",
    "büro": "office",
    "flur": "hallway",
    "living_room": "living_room",
    "bedroom": "bedroom",
    "hallway": "hallway",
    "bath": "bath",
}

@mcp.tool()
async def turn_on_light(entity_id: str) -> str:
    """
    Turns on a light in Home Assistant.
    Parameters:
        - entity_id: ex.: "light.living_room" or "light.kitchen"
    Return:
    Status as string.
    """

    # Normalisieren und übersetzen des Raumnamens
    entity_parts = entity_id.split(".")
    domain = entity_parts[0]
    room = entity_parts[1] if len(entity_parts) > 1 else ""

    print(room)
    room_en = ROOM_NAME_MAP.get(room.lower())
    print(room_en)
    entity_id = f"{domain}.{room_en}"

    url = f"{HASS_URL}/api/services/light/turn_on"
    payload = {"entity_id": entity_id}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return f"Light {entity_id} turned on."
    else:
        return f"Error turning on light {entity_id}: {response.text}"

@mcp.tool()
async def turn_off_light(entity_id: str) -> str:
    """
    Turns off a light in Home Assistant.
    Parameters:
        - entity_id: ex.: "light.living_room" or "light.kitchen"
    Return:
    Status as string.
    """
    # Normalisieren und übersetzen des Raumnamens
    entity_parts = entity_id.split(".")
    domain = entity_parts[0]
    room = entity_parts[1] if len(entity_parts) > 1 else ""

    room_en = ROOM_NAME_MAP[room.lower()]
    entity_id = f"{domain}.{room_en}"

    url = f"{HASS_URL}/api/services/light/turn_off"
    payload = {"entity_id": entity_id}
    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return f"Light {entity_id} was turned off."
    else:
        return f"Error turning off light {entity_id}: {response.text}"

@mcp.tool()
async def set_temperature(entity_id: str, temperature: float) -> str:
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