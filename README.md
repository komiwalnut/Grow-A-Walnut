# Grow-A-Walnut

Grow-A-Walnut is a Discord bot that delivers real-time updates of seed, gear, egg, and other important updates from the Grow a Garden game. It automatically posts the latest stock for seeds, gear, and eggs, tracks traveling merchants, and pings roles for rare items—all in dedicated Discord channels.

## Features

- **Real-Time Stock Alerts:**  
  Instantly notifies your server about new seeds, gear, and eggs as soon as they appear in the game.
- **Traveling Merchant Detection:**  
  Posts merchant info only when new or just became active, avoiding duplicate notifications.
- **Egg, Seed, and Gear Channel Updates:**  
  Keeps a single message in each channel up-to-date with the latest info.
- **Weather Tracking:**  
  Shows which weather events are currently active and their durations.
- **Role Pings for Rare Items:**  
  Automatically pings roles for rare seeds, gear, and eggs (customizable).
- **Event Shop Stock Channel:**
  Posts the latest event shop stock as an embedded message in a dedicated channel.

---

## How to Make a Discord Bot & Get Your Token

1. **Create a Discord Application:**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications).
   - Click **New Application**, give it a name, and save.

2. **Add a Bot to Your Application:**
   - In your application, go to the **Bot** tab.
   - Click **Add Bot** and confirm.
   - (Optional) Set a profile picture and username for your bot.

3. **Get Your Bot Token:**
   - Under the **Bot** tab, click **Reset Token** (if needed) and **Copy** the token.  
   - **Keep this token secret!**

4. **Invite the Bot to Your Server:**
   - Go to the **OAuth2 > URL Generator** tab.
   - Under **Scopes**, select `bot`.
   - Under **Bot Permissions**, select at least:
     - `Send Messages`
     - `Embed Links`
     - `Read Message History`
     - `Manage Messages` (for editing/updating messages)
     - `View Channels`
   - Copy the generated URL, open it in your browser, and invite the bot to your server.

---

## Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/komiwalnut/Grow-A-Walnut.git
   cd Grow-A-Walnut
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   ```
   DISCORD_BOT_TOKEN=your_discord_bot_token
   JS_TOKEN=your_js_token_here
   ```
   - You can get your JS token from the Grow a Garden API & WebSocket Discord: https://discord.gg/tgKNJJaq
   - This token is required for all API requests except images.

4. **Modify `config.py` file:**
   ```python
   STOCK_UPDATES_CHANNEL_ID = stock_updates_channel_id
   WEATHER_UPDATES_CHANNEL_ID = weather_updates_channel_id
   TRAVELING_MERCHANT_CHANNEL_ID = traveling_merchant_channel_id
   SEED_CHANNEL_ID = seed_channel_id
   GEAR_CHANNEL_ID = gear_channel_id
   EGG_CHANNEL_ID = egg_channel_id
   WEATHER_CHANNEL_ID = weather_channel_id
   EVENTSHOP_STOCK_CHANNEL_ID = eventshop_stock_channel_id

   RARE_SEED_ROLES = {
      'beanstalk': 'ROLE_ID_BEANSTALK',
      'burning_bud': 'ROLE_ID_BURNING_BUD',
      'cacao': 'ROLE_ID_CACAO',
      'cactus': 'ROLE_ID_CACTUS',
      'coconut': 'ROLE_ID_COCONUT',
      'dragon_fruit': 'ROLE_ID_DRAGON_FRUIT',
      'ember_lily': 'ROLE_ID_EMBER_LILY',
      'giant_pinecone': 'ROLE_ID_GIANT_PINECONE',
      'grape': 'ROLE_ID_GRAPE',
      'mango': 'ROLE_ID_MANGO',
      'mushroom': 'ROLE_ID_MUSHROOM',
      'pepper': 'ROLE_ID_PEPPER',
      'sugar_apple': 'ROLE_ID_SUGAR_APPLE',
   }
   RARE_GEAR_ROLES = {
      'advanced_sprinkler': 'ROLE_ID_ADVANCED_SPRINKLER',
      'basic_sprinkler': 'ROLE_ID_BASIC_SPRINKLER',
      'friendship_pot': 'ROLE_ID_FRIENDSHIP_POT',
      'godly_sprinkler': 'ROLE_ID_GODLY_SPRINKLER',
      'levelup_lollipop': 'ROLE_ID_LEVELUP_LOLLIPOP',
      'master_sprinkler': 'ROLE_ID_MASTER_SPRINKLER',
      'medium_toy': 'ROLE_ID_MEDIUM_TOY',
      'medium_treat': 'ROLE_ID_MEDIUM_TREAT',
      'tanning_mirror': 'ROLE_ID_TANNING_MIRROR',
   }
   RARE_EGG_ROLES = {
      'bug_egg': 'ROLE_ID_BUG_EGG',
      'mythical_egg': 'ROLE_ID_MYTHICAL_EGG',
      'paradise_egg': 'ROLE_ID_PARADISE_EGG',
      'rare_summer_egg': 'ROLE_ID_RARE_SUMMER_EGG',
   }
   ```
   - To get channel IDs: Enable Developer Mode in Discord (User Settings > Advanced), then right-click a channel and select "Copy ID".
   - **Fill in the correct Discord role IDs for each rare item in the dictionaries above.**

   **Custom Emojis:**
   - You can upload custom emojis for your bot in the [Discord Developer Portal](https://discord.com/developers/applications) under your application, on the **Emojis** page.
   - When uploading, take note of both the emoji **name** and the **emoji ID** (the numeric ID assigned to the emoji). You will need both to configure the bot to use your custom emojis.
   - In your `config.py`, add each emoji to the `EMOJI_IDS` dictionary in the format: `'emoji_name': 'emoji_id'`.

5. **Run the bot:**
   ```sh
   nohup python GrowWalnut.py > bot.log 2>&1 &
   ```

---

## Downloading Game Images

To download the latest seed, gear, egg, and weather images from the API, run:

```sh
python GetImages.py
```

This will save images to the `assets/` directory, organized by type.

---

## Required Bot Permissions

For the bot to function correctly, it needs the following permissions in the channels you specify:
- **Send Messages**
- **Embed Links**
- **Read Message History**
- **Manage Messages** (to edit/update its own messages)
- **View Channels**

If you want the bot to ping roles for rare items, make sure it has permission to mention those roles (Server Settings > Roles > Allow "Mention @role").

---

## Join Us

- **Grow a Garden API & WebSocket by JoshLei:** [https://discord.gg/kCryJ8zPwy](https://discord.gg/kCryJ8zPwy)

## Credits

- **API & WebSocket:** [JoshLei](https://discord.gg/kCryJ8zPwy)

## License

MIT License

---

*This project is not affiliated with or endorsed by JoshLei or the Grow a Garden game. All API data and game assets belong to their respective owners.*