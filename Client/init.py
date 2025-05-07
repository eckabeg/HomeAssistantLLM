from homeassistant.core import HomeAssistant, ServiceCall
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from .client import send_model_context

DOMAIN = "model_context"

SERVICE_REQUEST = "request"

SERVICE_SCHEMA = vol.Schema({
    vol.Required("model_key"): cv.string,
    vol.Optional("features"): vol.All(cv.ensure_list, [vol.Coerce(float)]),
    vol.Optional("prompt"): cv.string,
})

async def async_setup(hass: HomeAssistant, config: dict):
    async def handle_request(call: ServiceCall):
        model_key = call.data["model_key"]
        features = call.data.get("features")
        prompt = call.data.get("prompt")

        payload = {"model_key": model_key}
        if features:
            payload["features"] = features
        if prompt:
            payload["prompt"] = prompt

        try:
            result = send_model_context(payload)
            msg = f"Response from model `{model_key}`: {result}"
        except Exception as e:
            msg = f"Model request failed: {e}"

        hass.components.persistent_notification.create(
            msg, title="Model Context Result"
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REQUEST,
        handle_request,
        schema=SERVICE_SCHEMA
    )

    return True
