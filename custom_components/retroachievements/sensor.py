import logging
from datetime import datetime, timedelta, timezone
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import requests

from .const import CONF_USERNAME, CONF_API_KEY, CONF_NUM_GAMES

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)
IMG_BASE = "https://retroachievements.org"
BASE_API = "https://retroachievements.org/API"

def safe_int(value, default=0):
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

def _to_local_timestamp(raw: str) -> str | None:
    if not raw:
        return None
    try:
        dt = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return raw


class RetroAchievementsData:
    def __init__(self, username, api_key, num_games):
        self._username = username
        self._api_key = api_key
        self._num_games = num_games
        self.data = {}

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        try:
            # --- User summary ---
            summary_url = f"{BASE_API}/API_GetUserSummary.php?z={self._username}&y={self._api_key}&u={self._username}"
            summary_resp = requests.get(summary_url, timeout=20)
            summary_resp.raise_for_status()
            self.data["summary"] = summary_resp.json()

            # --- Recently played games ---
            recent_url = f"{BASE_API}/API_GetUserRecentlyPlayedGames.php?z={self._username}&y={self._api_key}&u={self._username}&c=15"
            recent_resp = requests.get(recent_url, timeout=20)
            recent_resp.raise_for_status()
            recent = recent_resp.json()
            if not isinstance(recent, list):
                _LOGGER.debug("Recent games payload not a list: %s", recent)
                recent = []

            # Sort by LastPlayed desc and keep only requested number
            recent_sorted = sorted(recent, key=lambda g: g.get("LastPlayed", ""), reverse=True)
            recent_sorted = recent_sorted[:self._num_games]

            # Fetch full game info, badges, and completion (single API call per game)
            for game in recent_sorted:
                game_id = game.get("GameID")
                if not game_id:
                    continue
                try:
                    # Fetch full game info
                    full_url = f"{BASE_API}/API_GetGame.php?i={game_id}&y={self._api_key}"
                    full_resp = requests.get(full_url, timeout=20)
                    full_resp.raise_for_status()
                    full_game = full_resp.json()
                    if isinstance(full_game, dict):
                        for key in ["ImageIcon", "ImageBoxArt", "ImageTitle", "ImageIngame"]:
                            if key in game and key not in full_game:
                                full_game[key] = game[key]
                        game.update(full_game)
                except Exception as e:
                    _LOGGER.debug("Failed to fetch full game info for %s: %s", game.get("Title"), e)

                try:
                    # Fetch badges and user completion once here (single API call)
                    badge_url = f"{BASE_API}/API_GetGameInfoAndUserProgress.php?g={game_id}&u={self._username}&y={self._api_key}"
                    badge_resp = requests.get(badge_url, timeout=20)
                    badge_resp.raise_for_status()
                    badge_data = badge_resp.json()

                    # Extract recent badges
                    achievements = badge_data.get("Achievements", {})
                    unlocked = []
                    for ach_id, ach in achievements.items():
                        date_earned = ach.get("DateEarned")
                        badge_name = ach.get("BadgeName")
                        if date_earned and badge_name:
                            unlocked.append(
                                {
                                    "title": ach.get("Title"),
                                    "badge_url": f"{IMG_BASE}/Badge/{badge_name}.png",
                                    "achievement_url": f"https://retroachievements.org/Achievement/{ach_id}",
                                    "date": date_earned,
                                }
                            )
                    unlocked.sort(key=lambda x: x["date"], reverse=True)
                    game["recent_badges"] = unlocked[:5]

                    # Add user completion percentages
                    game["completion_percentage"] = badge_data.get("UserCompletion", "unknown")
                    game["completion_percentage_hardcore"] = badge_data.get("UserCompletionHardcore", "unknown")

                except Exception as e:
                    _LOGGER.debug("Failed to fetch badges or completion for %s: %s", game.get("Title"), e)
                    game["recent_badges"] = []
                    game["completion_percentage"] = "unknown"
                    game["completion_percentage_hardcore"] = "unknown"

            self.data["recent_games"] = recent_sorted
            self.data["active_game"] = recent_sorted[0] if recent_sorted else None

        except Exception as e:
            _LOGGER.error("Error updating RetroAchievements data: %s", e)


# ---- Console icon mapping ----
CONSOLE_ICON_MAP = {
    "Amiga": "amiga.png",
    "Arcade": "arc.png",
    "Atari 2600": "2600.png",
    "Atari 7800": "7800.png",
    "Atari Lynx": "lynx.png",
    "DOS": "dos.png",
    "NES/Famicom": "nes.png",
    "SNES/Super Famicom": "snes.png",
    "Game Boy": "gb.png",
    "Game Boy Color": "gbc.png",
    "Game Boy Advance": "gba.png",
    "GameCube": "gc.png",
    "Game Gear": "gamegear.png",
    "Mega Drive/Genesis": "md.png",
    "Master System": "sms.png",
    "Nintendo 64": "n64.png",
    "Nintendo DS": "ds.png",
    "Nintendo 3DS": "3ds.png",
    "Wii": "wii.png",
    "Wii U": "wiiu.png",
    "PlayStation": "ps1.png",
    "PlayStation 2": "ps2.png",
    "PlayStation Portable": "psp.png",
    "Xbox": "xbox.png",
    "Sega Saturn": "sat.png",
    "Dreamcast": "dc.png",
}
def get_console_icon(console_name: str) -> str | None:
    if console_name in CONSOLE_ICON_MAP:
        return f"https://static.retroachievements.org/assets/images/system/{CONSOLE_ICON_MAP[console_name]}"
    return None


class RetroAchievementsActiveGameSensor(Entity):
    def __init__(self, ra_data):
        self._ra_data = ra_data
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return "RetroAchievements Most Recently Played Game"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    def update(self):
        self._ra_data.update()
        game = self._ra_data.data.get("active_game")
        summary = self._ra_data.data.get("summary") or {}
        if game:
            game_id = game.get("GameID")
            last_played_raw = game.get("LastPlayed")
            last_played_local = _to_local_timestamp(last_played_raw)
            console_name = game.get("ConsoleName", "Unknown")

            self._state = game.get("Title", "Unknown Game")
            self._attrs = {
                "rich_presence": summary.get("RichPresenceMsg"),
                "last_played_local": last_played_local,
                "achievements_total": safe_int(game.get("AchievementsTotal")),
                "achievements_unlocked": safe_int(game.get("NumAchieved")),
                "total_achievements": safe_int(game.get("NumPossibleAchievements")),
                "score_achieved": safe_int(game.get("ScoreAchieved")),
                "possible_score": safe_int(game.get("PossibleScore")),
                "console": game.get("ConsoleName", "Unknown"),
                "console_icon": get_console_icon(console_name),
                "url": f"https://retroachievements.org/game/{game_id}" if game_id else None,
                "developer": game.get("Developer") or "Unknown",
                "genre": game.get("Genre") or "Unknown",
                "released": game.get("Released") or "Unknown",
                "icon": f"{IMG_BASE}{game.get('ImageIcon')}" if game.get("ImageIcon") else None,
                "box_art": f"{IMG_BASE}{game.get('ImageBoxArt')}" if game.get("ImageBoxArt") else None,
                "title_screen": f"{IMG_BASE}{game.get('ImageTitle')}" if game.get("ImageTitle") else None,
                "in_game_image": f"{IMG_BASE}{game.get('ImageIngame')}" if game.get("ImageIngame") else None,
                "last_played_utc": last_played_raw,
                "recent_badges": game.get("recent_badges", []),
                "completion_percentage": game.get("completion_percentage", "unknown"),
                "completion_percentage_hardcore": game.get("completion_percentage_hardcore", "unknown"),
            }
        else:
            self._state = "No Game"
            self._attrs = {}


class RetroAchievementsRecentGameSensor(Entity):
    def __init__(self, ra_data, index):
        self._ra_data = ra_data
        self._index = index
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return f"RetroAchievements Last Played Game {self._index + 1}"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    def update(self):
        self._ra_data.update()
        games = self._ra_data.data.get("recent_games", [])
        if len(games) > self._index:
            game = games[self._index]
            game_id = game.get("GameID")
            last_played_raw = game.get("LastPlayed")
            last_played_local = _to_local_timestamp(last_played_raw)
            console_name = game.get("ConsoleName", "Unknown")

            self._state = game.get("Title", "Unknown Game")
            self._attrs = {
                "last_played_local": last_played_local,
                "achievements_total": safe_int(game.get("AchievementsTotal")),
                "achievements_unlocked": safe_int(game.get("NumAchieved")),
                "total_achievements": safe_int(game.get("NumPossibleAchievements")),
                "score_achieved": safe_int(game.get("ScoreAchieved")),
                "possible_score": safe_int(game.get("PossibleScore")),
                "console": game.get("ConsoleName", "Unknown"),
                "console_icon": get_console_icon(console_name),
                "url": f"https://retroachievements.org/game/{game_id}" if game_id else None,
                "developer": game.get("Developer") or "Unknown",
                "genre": game.get("Genre") or "Unknown",
                "released": game.get("Released") or "Unknown",
                "icon": f"{IMG_BASE}{game.get('ImageIcon')}" if game.get("ImageIcon") else None,
                "box_art": f"{IMG_BASE}{game.get('ImageBoxArt')}" if game.get("ImageBoxArt") else None,
                "title_screen": f"{IMG_BASE}{game.get('ImageTitle')}" if game.get("ImageTitle") else None,
                "in_game_image": f"{IMG_BASE}{game.get('ImageIngame')}" if game.get("ImageIngame") else None,
                "last_played_utc": last_played_raw,
                "recent_badges": game.get("recent_badges", []),
                "completion_percentage": game.get("completion_percentage", "unknown"),
                "completion_percentage_hardcore": game.get("completion_percentage_hardcore", "unknown"),
            }
        else:
            self._state = "Unavailable"
            self._attrs = {}


class RetroAchievementsUserSummarySensor(Entity):
    def __init__(self, ra_data):
        self._ra_data = ra_data
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return "RetroAchievements User Summary"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attrs

    def update(self):
        self._ra_data.update()
        data = self._ra_data.data.get("summary") or {}
        active_game = self._ra_data.data.get("active_game")
        now = datetime.now().astimezone()

        status = "Offline"
        last_online = None

        if active_game:
            last_played_raw = active_game.get("LastPlayed")
            last_played_local_str = _to_local_timestamp(last_played_raw)
            if last_played_local_str:
                try:
                    last_played_dt = datetime.strptime(
                        last_played_local_str, "%Y-%m-%d %H:%M:%S"
                    ).astimezone()
                    last_online = last_played_dt.strftime("%Y-%m-%d %H:%M")
                    if (now - last_played_dt) <= timedelta(minutes=5):
                        status = "Online"
                except Exception:
                    pass

        if data:
            self._state = data.get("User", self._ra_data._username)

            awards = []
            awarded = data.get("Awarded")
            if isinstance(awarded, dict):
                for game_id, award in awarded.items():
                    awards.append(
                        {
                            "game_id": game_id,
                            "badge_url": f"{IMG_BASE}{award.get('BadgeURL')}" if award and award.get("BadgeURL") else None,
                            "title": award.get("Title") if award else None,
                            "type": award.get("AwardType") if award else None,
                        }
                    )
            elif isinstance(awarded, list):
                for award in awarded:
                    awards.append(
                        {
                            "game_id": award.get("GameID") if isinstance(award, dict) else None,
                            "badge_url": f"{IMG_BASE}{award.get("BadgeURL")}" if isinstance(award, dict) and award.get("BadgeURL") else None,
                            "title": award.get("Title") if isinstance(award, dict) else None,
                            "type": award.get("AwardType") if isinstance(award, dict) else None,
                        }
                    )

            self._attrs = {
                "username": data.get("User", self._ra_data._username),
                "member_since": data.get("MemberSince"),
                "motto": data.get("Motto"),
                "rank": data.get("Rank") or "Unranked",
                "total_ranked": data.get("TotalRanked", 0),
                "total_points": data.get("TotalPoints", 0),
                "softcore_points": data.get("TotalSoftcorePoints", 0),
                "true_points": data.get("TotalTruePoints", 0),
                "awards": awards,
                "status": status,
                "last_online": last_online,
                "profile_pic": f"{IMG_BASE}{data.get("UserPic")}" if data.get("UserPic") else None,
                "recently_played_count": safe_int(data.get("RecentlyPlayedCount", 0)),
            }
        else:
            self._state = "Unavailable"
            self._attrs = {}


# ---- HA entry point ----
async def async_setup_entry(hass, entry, async_add_entities):
    username = entry.data[CONF_USERNAME]
    api_key = entry.data[CONF_API_KEY]
    num_games = entry.data.get(CONF_NUM_GAMES, 5)

    ra_data = RetroAchievementsData(username, api_key, num_games)

    sensors = [
        RetroAchievementsActiveGameSensor(ra_data),
        RetroAchievementsUserSummarySensor(ra_data),
    ]
    for i in range(1, num_games):
        sensors.append(RetroAchievementsRecentGameSensor(ra_data, i))

    async_add_entities(sensors, update_before_add=True)
