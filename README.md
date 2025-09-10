# 🕹️ HA-RA (Home Assistant + RetroAchievements)
This is a **RetroAchievements integration for Home Assistant**.  
Bring your retro-gaming stats, history, and live activity right into your smart home setup.  
<img width="200" height="200" alt="logo" src="https://github.com/user-attachments/assets/1192e0ad-14ff-40ec-bb83-3ce8af7d0de0"/><br>  
Start playing at 👉 [retroachievements.org](https://retroachievements.org/)  

## ✨ Features  
HA-RA creates **sensors** inside Home Assistant that let you track your RetroAchievements progress.  
Currently, it provides:  

- 🎯 **15 Game Sensors** — The last 15 games you’ve played  (user selectable. Set to 3 games by default. Max 15, like the website)
- 👤 **User Summary Sensor** — Your global stats, profile, and rich presence  
- 🌍 **Global Stats Sensor** — Site-wide leaderboards & totals

### 🧑 User Summary Sensor
Tracks your overall RetroAchievements account stats:
- 🧑 Username
- 🖼️ Profile Picture
- 👤 Online Status 
- 📅 Member Since  
- 💬 Motto
- 🎮 Total Achievements  
- 🏆 Total Points (core)  
- 🟡 Softcore Points  
- 🔵 True Points (hardcore weighted)  
- 🥇 Rank / Total Ranked

### 🎮 Game Sensors
- **15 most recently played games** are available as entities<br>
Each game sensor includes the following attributes:
  - 🖼️ Artwork (icon, box art, title screen, gameplay screenshot, console icon)  
  - 🎮 Console  
  - 🕒 Last Played (local + UTC)  
  - 🏆 Achievements (total, unlocked, progress)  
  - ⭐ Score (achieved + possible)  
  - 👨‍💻 Developer  
  - 📚 Genre  
  - 📅 Release Date  
  - 🔗 Direct link to the game’s RetroAchievements page  
  - 💬 Rich Presence (What you're doing currently in Active/Most recently played game)
  - 🏅 Last 5 earned badges per game (icon, link, date earned)
  - 📊 Softcore and Hardcore Progress

# Lovelace Card Example:
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
          <img src="{{ badge.badge_url }}" width="40" style="margin: 2px;">
        </a>
      {% endfor %} {% endif %}
    text_only: true
  - type: markdown
    content: >-
      {% set g1 = states.sensor.retroachievements_most_recently_played_game
      %}<h2><img src="{{ g1.attributes.console_icon }}" width="25"> {{
      g1.state}}</h2>


      <small><font color=lightgreen> {{ g1.attributes.rich_presence
      }}</font></small>


      📊 Completed: **{{ g1.attributes.completion_percentage }}**

      🏆 Achievements: **{{ g1.attributes.achievements_unlocked }}/{{
      g1.attributes.total_achievements }}**

      ⭐ Score: **{{ g1.attributes.score_achieved }}/{{
      g1.attributes.possible_score }}**

      🕒 Last Played: **{{ as_timestamp(g1.attributes.last_played_local) |
      timestamp_custom("%b %d, %Y %I:%M %p") }}**
    text_only: true

```
<img width="521" height="263" alt="image" src="https://github.com/user-attachments/assets/c880ddf2-11a6-4fcb-8892-cf87c5b89cd0" />


