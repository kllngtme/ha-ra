# 🕹️ HA-RA (Home Assistant + RetroAchievements)
This is a **RetroAchievements integration for Home Assistant**.  
Bring your retro-gaming stats, history, and live activity right into your smart home setup.  
<a href="https://www.retroachievements.org"><img width="150" height="150" alt="logo" src="https://github.com/user-attachments/assets/1192e0ad-14ff-40ec-bb83-3ce8af7d0de0"/></a><br>
Start playing at 👉 [retroachievements.org](https://retroachievements.org/)
## ✨ Features  
 
🌟 **Achievement of the Week Sensor** — Weekly highlighted achievement<br>
🧑 **User Summary Sensor** — Your global stats, profile, and rich presence<br>
🎮 **15 Game Sensors** — The last 15 games you’ve played  (user selectable. Set to 3 games by default. Max 15, like the website)
<br>

### 🌟 Achievement of the Week Sensor
Tracks the current Achievement of the Week: https://retroachievements.org/event/1-achievement-of-the-week-2025
- 🏆 Achievement Name & Description
- 🎮 Console & Game
- 🕒 Start and End Date  
- 🔗 Links to achievement, game, and console pages  
- 🌍 Total Players who earned it
- 🔓 Unlocked Status
- 🖼️ Artwork `badge_icon`, `game_icon`, `box_art`, `console_icon`

### 🧑 User Summary Sensor
Tracks your overall RetroAchievements account stats:
- 🧑 Username
- 🖼️ Profile Picture
- 👤 Online Status 
- 📅 Member Since  
- 💬 Motto
- 🏆 Total Achievements  
- 🏅 Awards
- 🥇 Rank / Total Ranked
- 🔵 Total Points (core)  
- 🟡 Softcore & True(Hardcore) Points

### 🎮 Game Sensors
- **Up to 15 Most Recently Played Games** are available as entities<br>
Each game sensor includes the following attributes:
  - 🎮 Console  
  - 👨‍💻 Developer  
  - 📚 Genre  
  - 📅 Release Date  
  - 🕒 Last Played (local + UTC)
  - ⭐ Score (achieved + possible)  
  - 🏆 Achievements (total, unlocked, progress)
  - 🏅 Last 5 earned badges per game (icon, link, date earned)
  - 🔗 Direct link to the game’s RetroAchievements page  
  - 💬 Rich Presence (What you're doing currently in Active/Most recently played game)
  - 📊 Softcore and Hardcore Progress
  - 🖼️ Artwork `game_icon`, `box_art`, `title_screen`, `in_game_image`, `console_icon`
<br>  
<br>

### Lovelace Card examples:


## Most Recently Played Game Card Example
Clickable BoxArt brings you to game URL. Badges brings you to each badge. The console icon brings you to the console URL.<br>
<img width="521" height="263" alt="image" src="https://github.com/user-attachments/assets/c880ddf2-11a6-4fcb-8892-cf87c5b89cd0"/>

```
type: horizontal-stack
cards:
  - type: markdown
    content: >-
      {% set g1 = states.sensor.retroachievements_most_recently_played_game %}

      <a href="{{ g1.attributes.url }}">
        <img src="{{ g1.attributes.box_art }}" width="125">
      </a>

      {% if g1.attributes.recent_badges %} <br> {% for badge in
      g1.attributes.recent_badges %}
        <a href="{{ badge.achievement_url }}" target="_blank">
          <img src="{{ badge.badge_icon }}" width="40" style="margin: 2px;">
        </a>
      {% endfor %} {% endif %}
    text_only: true
  - type: markdown
    content: >-
      {% set g1 = states.sensor.retroachievements_most_recently_played_game
      %}<h2> <a href="{{ g1.attributes.console_url }}" target="_blank">
        <img src="{{ g1.attributes.console_icon }}" width="25"></a> {{ g1.state }}</h2>

      <small><font color=lightgreen> {{ g1.attributes.rich_presence
      }}</font></small>


      📊 Completed: **{{ g1.attributes.completion_percentage }}**

      🏆 Achievements: **{{ g1.attributes.achievements_unlocked }}/{{
      g1.attributes.total_achievements }}**

      ⭐ Score: **{{ g1.attributes.score_achieved }}/{{
      g1.attributes.possible_score }}**

      🕒 Last Played: **{{ as_timestamp(g1.attributes.last_played_local) |
      timestamp_custom("%-m/%-d/%y %-I:%M%p") }}**
    text_only: true
```

## Achievement of the Week Card Example
Clickable Badge brings you to the Achievement. The console icon is clickable as well.<br>
<img width="359" height="359" alt="image" src="https://github.com/user-attachments/assets/7ded4626-4cd6-4bb9-b61f-bd1e01746e43" />


```
type: markdown
content: >-
  {% set s = states('sensor.retroachievements_achievement_of_the_week') %}

  {% set a =
  state_attr('sensor.retroachievements_achievement_of_the_week','description')
  %}

  {% set start =
  state_attr('sensor.retroachievements_achievement_of_the_week','start_at') %}

  {% set end =
  state_attr('sensor.retroachievements_achievement_of_the_week','end_at') %}

  <font color=gold><h2>🏆 Achievement of the Week</h2></font>

  {% set tz = now().tzinfo %}{% set start_dt = as_datetime(start).astimezone(tz)
  if start else none %}

  {% set end_dt = as_datetime(end).astimezone(tz) if end else none %} {% if s
  and s != 'unknown' %}

  <a href="{{ state_attr('sensor.retroachievements_achievement_of_the_week',
  'achievement_url') }}" target="_blank">

  <img src="{{ state_attr('sensor.retroachievements_achievement_of_the_week',
  'badge_icon') }}" width="90" style="border-radius:8px;"></a><br>

  <b>{{ s }}</b><br> <small>{{ a }}</small><br>

  <a href="{{
  state_attr('sensor.retroachievements_achievement_of_the_week','console_url')
  }}" target="_blank">

  <img src="{{
  state_attr('sensor.retroachievements_achievement_of_the_week','console_icon')
  }}" width="25" style="vertical-align:middle; margin-right:4px;"></a><b> <a
  href="{{
  state_attr('sensor.retroachievements_achievement_of_the_week','game_url') }}"
  target="_blank">{{
  state_attr('sensor.retroachievements_achievement_of_the_week','game')
  }}</a></b><br>

  ⭐ Points: <b>{{ state_attr('sensor.retroachievements_achievement_of_the_week',
  'points') }}</b><br>
    👥 Players: <b>{{
  state_attr('sensor.retroachievements_achievement_of_the_week',
  'total_players') }}</b><br> 🕒 Start: <b>{% if start_dt %}{{
  start_dt.strftime('%-m/%-d/%Y %-I:%M%p') }}{% endif %}</b><br> ⏳ Ends: <b>{%
  if end_dt %}{{ end_dt.strftime('%-m/%-d/%Y %-I:%M%p') }}<br>{% if
  state_attr('sensor.retroachievements_achievement_of_the_week',
  'unlocked_hardcore') %}

  ✅ <b>You unlocked this in Hardcore Mode!</b>

  {% elif state_attr('sensor.retroachievements_achievement_of_the_week',
  'unlocked_softcore') %}

  ☑️ You unlocked this (Softcore)

  {% else %}

  ❌ You haven't unlocked this yet

  {% endif %}


  {% endif %}</b>{% else %}No data available.{% endif %}
text_only: true
```
<br>
<a href="https://www.buymeacoffee.com/kllngtme" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 30px !important;width: 108px !important;" ></a>
