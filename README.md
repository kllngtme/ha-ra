# 🕹️ HA-RA (Home Assistant + RetroAchievements)

This is a **RetroAchievements integration for Home Assistant**.  
Bring your gaming stats, history, and live activity right into your smart home setup.  

<img width="256" height="256" alt="logo" src="https://github.com/user-attachments/assets/1192e0ad-14ff-40ec-bb83-3ce8af7d0de0"/><br>  

Start playing at 👉 [retroachievements.org](https://retroachievements.org/)  

---

## ✨ Features  
HA-RA creates **sensors** inside Home Assistant that let you track your RetroAchievements progress.  
Currently, it provides:  

- 🎯 **15 Game Sensors** — The last 15 games you’ve played  (user selectable. Set to 3 games by default. Max 15, like the website)
- 👤 **User Summary Sensor** — Your global stats, profile, and rich presence  
- 🌍 **Global Stats Sensor** — Site-wide leaderboards & totals  

---

### 🎮 Game Sensors
- **15 most recently played games** are available as entities
- Each game sensor includes the following attributes:
  - 🖼️ Artwork (icon, box art, title screen, gameplay screenshot, console icon)  
  - 🎮 Console  
  - 🕒 Last Played (local + UTC)  
  - 🏆 Achievements (total, unlocked, progress)  
  - ⭐ Score (achieved + possible)  
  - 👨‍💻 Developer  
  - 📚 Genre  
  - 📅 Release Date  
  - 🔗 Direct link to the game’s RetroAchievements page  
  - 💬 Rich Presence (what you’re doing in-game, if supported)

---

### 🧑 User Summary Sensor
Tracks your overall RetroAchievements account stats:
- 🧑 Username
- 🖼️ Profile Picture  
- 📅 Member Since  
- 💬 Motto
- 🎮 Total Achievements  
- 🏆 Total Points (core)  
- 🟡 Softcore Points  
- 🔵 True Points (hardcore weighted)  
- 🥇 Rank / Total Ranked
