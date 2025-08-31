import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_USERNAME, CONF_API_KEY, CONF_NUM_GAMES

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_API_KEY): str,
    vol.Optional(CONF_NUM_GAMES, default=3): vol.All(int, vol.Range(min=1, max=15)),
})

class RetroAchievementsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="RetroAchievements", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            description_placeholders={"num_games": "Number of Games to Monitor (including Active/Last Played)"}
        )
