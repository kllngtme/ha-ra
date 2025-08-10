import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN, CONF_USERNAME, CONF_API_KEY

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_API_KEY): str,
})

class RetroAchievementsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="RetroAchievements", data=user_input)
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

    @callback
    def async_get_options_flow(config_entry):
        return RetroAchievementsOptionsFlow(config_entry)


class RetroAchievementsOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        return self.async_show_form(step_id="init")
