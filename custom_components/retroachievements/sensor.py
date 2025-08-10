from datetime import datetime, timedelta
import logging
import async_timeout
import pytz
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from .const import DOMAIN, CONF_USERNAME, CONF_API_KEY

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)
BASE_URL = "https://retroachievements.org/API"
IMG_BASE = "https://retroachievements.org"  # prepend for images


def convert_to_local(utc_string, hass):
    """Convert RA UTC timestamps to HA's configured timezone."""
    try:
        dt_utc = datetime.strptime(utc_string, "%Y-%m-%d %H:%M:%S")
        dt_utc = pytz.utc.localize(dt_utc)
        local_tz = pytz.timezone(hass.config.time_zone)
        return dt_utc.astimezone(local_tz).strftime("%Y-%m-%d %I:%M:%S %p")
    except Exception as e:
        _LOGGER.error("Time conversion error: %s", e)
        return utc_string


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up RetroAchievements sensors for last 3 games."""
    username = entry.data[CONF_USERNAME]
    api_key = entry.data[CONF_API_KEY]
    session = async_get_clientsession(hass)

    async_add_entities([
    RetroAchievementsSensor(session, username, api_key, i, hass) for i in range(3)
] + [
    RetroAchievementsUserSummarySensor(session, username, api_key, hass),
    RetroAchievementsGlobalStatsSensor(session, username, api_key, hass),
], True)

 


class RetroAchievementsSensor(Entity):
    """Representation of a RetroAchievements recent game sensor."""

    def __init__(self, session, username, api_key, index, hass):
        self._session = session
        self._username = username
        self._api_key = api_key
        self._index = index
        self.hass = hass
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return f"RetroAchievements Game {self._index + 1}"

    @property
    def unique_id(self):
        return f"retroachievements_game_{self._index}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    async def async_update(self):
        """Fetch data for this RetroAchievements game."""
        try:
            async with async_timeout.timeout(20):
                url = (
                    f"{BASE_URL}/API_GetUserRecentlyPlayedGames.php"
                    f"?z={self._username}&y={self._api_key}&u={self._username}&c=3"
                )
                async with self._session.get(url) as resp:
                    games = await resp.json(content_type=None)

            if not games or self._index >= len(games):
                _LOGGER.debug("No game at index %s for user %s", self._index, self._username)
                return

            game = games[self._index]
            last_played_raw = game.get("LastPlayed")
            last_played_local = convert_to_local(last_played_raw, self.hass) if last_played_raw else None

            # State: Game title
            self._state = game.get("Title", "Unknown Game")

            # Attributes
            self._attrs = {
                "console": game.get("ConsoleName", "Unknown"),
                "last_played_local": last_played_local or "N/A",
                "achievements_total": safe_int(game.get("AchievementsTotal")),
                "achievements_unlocked": safe_int(game.get("NumAchieved")),
                "total_achievements": safe_int(game.get("NumPossibleAchievements")),
                "score_achieved": safe_int(game.get("ScoreAchieved")),
                "possible_score": safe_int(game.get("PossibleScore")),
                # Media assets
                "icon": f"{IMG_BASE}{game.get('ImageIcon')}" if game.get("ImageIcon") else None,
                "title_screen": f"{IMG_BASE}{game.get('ImageTitle')}" if game.get("ImageTitle") else None,
                "in_game_image": f"{IMG_BASE}{game.get('ImageIngame')}" if game.get("ImageIngame") else None,
                "box_art": f"{IMG_BASE}{game.get('ImageBoxArt')}" if game.get("ImageBoxArt") else None,
                # Raw RA timestamp (for debugging)
                "last_played_utc": last_played_raw,
                "game_id": game.get("GameID"),
            }

        except Exception as e:
            _LOGGER.error("Error fetching RetroAchievements data: %s", e)

class RetroAchievementsUserSummarySensor(Entity):
    """Sensor for overall RetroAchievements user summary."""

    def __init__(self, session, username, api_key, hass):
        self._session = session
        self._username = username
        self._api_key = api_key
        self.hass = hass
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return "RetroAchievements User Summary"

    @property
    def unique_id(self):
        return f"retroachievements_user_summary_{self._username}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    async def async_update(self):
        try:
            async with async_timeout.timeout(20):
                url = (
                    f"{BASE_URL}/API_GetUserSummary.php"
                    f"?z={self._username}&y={self._api_key}&u={self._username}"
                )
                async with self._session.get(url) as resp:
                    data = await resp.json(content_type=None)

            _LOGGER.debug("User summary response: %s", data)

            if not data or "User" not in data:
                self._state = "Unavailable"
                self._attrs = {}
                return

            # Always set state to the username
            self._state = data.get("User", self._username)

            # Parse awarded achievements (may be empty)
            awards = []
            if "Awarded" in data and isinstance(data["Awarded"], dict):
                for game_id, award in data["Awarded"].items():
                    awards.append({
                        "game_id": game_id,
                        "badge_url": f"https://retroachievements.org{award.get('BadgeURL')}" if award.get("BadgeURL") else None,
                        "title": award.get("Title"),
                        "type": award.get("AwardType"),
                    })

            self._attrs = {
                "points": data.get("TotalPoints", 0),
                "softcore_points": data.get("TotalSoftcorePoints", 0),
                "true_points": data.get("TotalTruePoints", 0),
                "rank": data.get("Rank") or "Unranked",
                "profile_pic": f"https://retroachievements.org{data.get('UserPic')}" if data.get("UserPic") else None,
                "motto": data.get("Motto"),
                "status": data.get("Status"),
                "member_since": data.get("MemberSince"),
                "recently_played_count": data.get("RecentlyPlayedCount", 0),
                "awards": awards,
                "rich_presence": data.get("RichPresenceMsg"),
            }

        except Exception as e:
            _LOGGER.error("Error fetching RetroAchievements user summary: %s", e)
            self._state = "Error"
            self._attrs = {}

class RetroAchievementsGlobalStatsSensor(Entity):
    """Sensor for RetroAchievements global user stats."""

    def __init__(self, session, username, api_key, hass):
        self._session = session
        self._username = username
        self._api_key = api_key
        self.hass = hass
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return "RetroAchievements Global Stats"

    @property
    def unique_id(self):
        return f"retroachievements_global_stats_{self._username}"

    @property
    def state(self):
        # Use total points as the main state
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    async def async_update(self):
        try:
            async with async_timeout.timeout(20):
                url = (
                    f"{BASE_URL}/API_GetUserSummary.php"
                    f"?z={self._username}&y={self._api_key}&u={self._username}"
                )
                async with self._session.get(url) as resp:
                    data = await resp.json(content_type=None)

            _LOGGER.debug("Global stats response: %s", data)

            if not data or "User" not in data:
                self._state = "Unavailable"
                self._attrs = {}
                return

            self._state = data.get("TotalPoints", 0)

            self._attrs = {
                "username": data.get("User", self._username),
                "rank": data.get("Rank") or "Unranked",
                "total_points": data.get("TotalPoints", 0),
                "softcore_points": data.get("TotalSoftcorePoints", 0),
                "true_points": data.get("TotalTruePoints", 0),
                "total_ranked": data.get("TotalRanked", 0),
                "member_since": data.get("MemberSince"),
                "status": data.get("Status"),
                "motto": data.get("Motto"),
                "rich_presence": data.get("RichPresenceMsg"),
                "profile_pic": f"https://retroachievements.org{data.get('UserPic')}" if data.get("UserPic") else None,
                "recently_played_count": data.get("RecentlyPlayedCount", 0),
            }

        except Exception as e:
            _LOGGER.error("Error fetching RetroAchievements global stats: %s", e)
            self._state = "Error"
            self._attrs = {}
