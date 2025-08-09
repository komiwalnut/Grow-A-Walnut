import os
import json
import asyncio
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import discord
from discord.ext import tasks
import time
import config
import math

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
JS_TOKEN = os.getenv('JS_TOKEN')

HEADERS = {'accept': 'application/json', 'jstudio-key': JS_TOKEN}

STOCK_UPDATES_CHANNEL_ID = config.STOCK_UPDATES_CHANNEL_ID
WEATHER_UPDATES_CHANNEL_ID = config.WEATHER_UPDATES_CHANNEL_ID
TRAVELING_MERCHANT_CHANNEL_ID = config.TRAVELING_MERCHANT_CHANNEL_ID
SEED_CHANNEL_ID = config.SEED_CHANNEL_ID
GEAR_CHANNEL_ID = config.GEAR_CHANNEL_ID
EGG_CHANNEL_ID = config.EGG_CHANNEL_ID
WEATHER_CHANNEL_ID = config.WEATHER_CHANNEL_ID

def ensure_data_directory():
    """Ensure the data directory exists"""
    if not os.path.exists('data'):
        os.makedirs('data')

ensure_data_directory()

MESSAGE_ID_FILE = 'data/message_ids.json'

def load_message_ids():
    if os.path.exists(MESSAGE_ID_FILE):
        with open(MESSAGE_ID_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_message_ids(ids):
    with open(MESSAGE_ID_FILE, 'w') as f:
        json.dump(ids, f)

message_ids = load_message_ids()

intents = discord.Intents.default()
client = discord.Client(intents=intents)

API_STOCK = 'https://api.joshlei.com/v2/growagarden/stock'
API_EGG_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=egg'
API_SEED_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=seed'
API_GEAR_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=gear'
API_WEATHER = 'https://api.joshlei.com/v2/growagarden/weather'
API_WEATHER_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=weather'

def fetch_stock_api():
    return requests.get(API_STOCK, headers=HEADERS).json()

def fetch_egg_info_api():
    return requests.get(API_EGG_INFO, headers=HEADERS).json()

def fetch_seed_info_api():
    return requests.get(API_SEED_INFO, headers=HEADERS).json()

def fetch_gear_info_api():
    return requests.get(API_GEAR_INFO, headers=HEADERS).json()

def fetch_weather_api():
    return requests.get(API_WEATHER, headers=HEADERS).json()

def fetch_weather_info_api():
    return requests.get(API_WEATHER_INFO, headers=HEADERS).json()

def get_emoji(item_id):
    emoji_id = config.EMOJI_IDS.get(item_id)
    if emoji_id:
        return f'<:{item_id}:{emoji_id}>'
    return ''

def build_embed(title, items, color=0x8e44ad, time_key='start_date_unix'):
    embed = discord.Embed(title=title, color=color, timestamp=datetime.now(timezone.utc))
    description_lines = []
    end_times = []
    
    for item in items:
        item_id = item.get('item_id', 'unknown')
        display_name = item.get('display_name', item.get('item_id', 'Unknown'))
        qty = item.get('quantity', '-')
        t_end = item.get('end_date_unix')

        name = f"{get_emoji(item_id)} {display_name} **{qty}x**"
        description_lines.append(name)
        
        if t_end:
            end_times.append(t_end)
    
    if description_lines:
        if end_times:
            min_end_time = min(end_times)
            embed.description = f"<t:{min_end_time}:R>\n\n" + '\n'.join(description_lines)
        else:
            embed.description = '\n'.join(description_lines)
    
    return embed

def build_info_embed(title, items, color=0x8e44ad, time_key='last_seen'):
    embed = discord.Embed(title=title, color=color, timestamp=datetime.now(timezone.utc))
    lines = []
    for item in items:
        t = item.get(time_key)
        if t == 0 or t == '0':
            continue
        item_id = item.get('item_id', 'unknown')
        display_name = item.get('display_name', item.get('item_id', 'Unknown'))
        name = f"{get_emoji(item_id)} {display_name}"
        if t and t != 0 and t != '0':
            t_fmt = f'<t:{t}:R>'
        else:
            t_fmt = 'N/A'
        lines.append(f'{name} {t_fmt}')
    
    if lines:
        description = '\n'.join(lines)
        if len(description) > 4000:
            description = '\n'.join(lines[:50]) + f'\n\n... and {len(lines) - 50} more items'
        embed.description = description
    else:
        embed.description = "No recent activity found."
    
    return embed

def build_weather_embed(weather_data):
    if not weather_data:
        return None

    embed = discord.Embed(
        title=weather_data[0].get('weather_name', 'Unknown'),
        color=0x00cccc,
        timestamp=datetime.now(timezone.utc)
    )

    events = []
    for w in weather_data:
        weather_id = w.get('weather_id', 'unknown')
        end_unix = w.get('end_duration_unix', 0)
        weather_emoji = get_emoji(weather_id)
        end_fmt = f'<t:{end_unix}:R>'
        events.append(f'{weather_emoji} Ends {end_fmt}')

    if events:
        description = '\n'.join(events)
        embed.description = description

    return embed

def get_mention_for_item(item_id, category):
    if category == 'seed':
        role_id = config.RARE_SEED_ROLES.get(item_id)
    elif category == 'gear':
        role_id = config.RARE_GEAR_ROLES.get(item_id)
    elif category == 'egg':
        role_id = config.RARE_EGG_ROLES.get(item_id)
    else:
        role_id = None
    return f'<@&{role_id}>' if role_id else ''

async def send_or_edit(channel, embed, key, mention=None):
    global message_ids
    msg_id = message_ids.get(key)
    msg = None
    if msg_id:
        try:
            msg = await channel.fetch_message(msg_id)
            await msg.edit(content=mention if mention else None, embed=embed)
            return
        except Exception:
            pass
    msg = await channel.send(content=mention if mention else None, embed=embed)
    message_ids[key] = msg.id
    save_message_ids(message_ids)

def build_traveling_merchant_embed(merchant_name, items):
    embed = discord.Embed(title=f"{merchant_name}", color=0xff6600, timestamp=datetime.now(timezone.utc))
    
    if items:
        end_unix = items[0].get('end_date_unix', 0)
        end_fmt = f'<t:{end_unix}:R>'
        embed.description = f"{end_fmt}"
        
        lines = []
        for item in items:
            item_id = item.get('item_id', 'unknown')
            display_name = item.get('display_name', item.get('item_id', 'Unknown'))
            qty = item.get('quantity', '-')
            item_emoji = get_emoji(item_id)
            
            lines.append(f"{item_emoji} {display_name} **{qty}x**")
        
        if lines:
            stock_description = '\n'.join(lines)

            embed.add_field(name="Stock", value=stock_description, inline=False)
    
    return embed

LAST_SEEN_STOCK_FILE = 'last_seen_stock.json'
ACTIVE_WEATHER_FILE = 'active_weather.json'

def load_json_file(filename, default):
    """Load JSON file from data directory"""
    data_path = os.path.join('data', filename)
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return json.load(f)
    return default

def save_json_file(filename, data):
    """Save JSON file to data directory"""
    data_path = os.path.join('data', filename)
    with open(data_path, 'w') as f:
        json.dump(data, f)

last_seen_stock = load_json_file(LAST_SEEN_STOCK_FILE, {'seed': [], 'gear': [], 'merchant': {}, 'merchant_info': {'merchantName': None, 'stock_ids': [], 'active_window': [0, 0]}})
last_seen_weather = load_json_file(ACTIVE_WEATHER_FILE, {'active_weathers': []})

async def dynamic_sleep(next_unix, fallback_seconds):
    now = time.time()
    if next_unix and next_unix > now:
        sleep_for = max(1, int(next_unix - now))
    else:
        sleep_for = fallback_seconds
    await asyncio.sleep(sleep_for)

@tasks.loop(count=1)
async def update_stock():
    while True:
        stock = fetch_stock_api()
        now = int(time.time())

        def is_active(item):
            start = item.get('start_date_unix', 0)
            end = item.get('end_date_unix', 0)
            return (start or 0) <= now < (end or 0)

        seed_items = [item for item in stock.get('seed_stock', []) if is_active(item)]
        gear_items = [item for item in stock.get('gear_stock', []) if is_active(item)]
        egg_items = [item for item in stock.get('egg_stock', []) if is_active(item)]
        eventshop_items = [item for item in stock.get('eventshop_stock', []) if is_active(item)]

        last_seen_stock = load_json_file(
            LAST_SEEN_STOCK_FILE,
            {'seed': [], 'gear': [], 'egg': [], 'merchant': {}, 'eventshop': []}
        )
        new_stock = False
        new_egg_stock = False
        new_eventshop_stock = False

        current_seed_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in seed_items}
        last_seed_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in last_seen_stock.get('seed', [])}
        if current_seed_ids != last_seed_ids:
            new_stock = True
            last_seen_stock['seed'] = seed_items

        current_gear_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in gear_items}
        last_gear_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in last_seen_stock.get('gear', [])}
        if current_gear_ids != last_gear_ids:
            new_stock = True
            last_seen_stock['gear'] = gear_items

        current_egg_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in egg_items}
        last_egg_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in last_seen_stock.get('egg', [])}
        if current_egg_ids != last_egg_ids:
            new_egg_stock = True
            last_seen_stock['egg'] = egg_items

        current_eventshop_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in eventshop_items}
        last_eventshop_ids = {item.get('item_id', '') + str(item.get('quantity', '')) for item in last_seen_stock.get('eventshop', [])}
        if current_eventshop_ids != last_eventshop_ids:
            new_eventshop_stock = True
            last_seen_stock['eventshop'] = eventshop_items

        if new_stock and (seed_items or gear_items):
            save_json_file(LAST_SEEN_STOCK_FILE, last_seen_stock)
            stock_channel = client.get_channel(STOCK_UPDATES_CHANNEL_ID)
            if stock_channel:
                if seed_items:
                    embed = build_embed('Seed Stock', seed_items, color=0x00ff99)
                    await send_or_edit(stock_channel, embed, 'stock_seed')
                if gear_items:
                    embed = build_embed('Gear Stock', gear_items, color=0x3399ff)
                    await send_or_edit(stock_channel, embed, 'stock_gear')

        if new_egg_stock and egg_items:
            save_json_file(LAST_SEEN_STOCK_FILE, last_seen_stock)
            stock_channel = client.get_channel(STOCK_UPDATES_CHANNEL_ID)
            if stock_channel:
                embed = build_embed('Egg Stock', egg_items, color=0xffcc00)
                await send_or_edit(stock_channel, embed, 'stock_egg')

        if new_eventshop_stock and eventshop_items:
            save_json_file(LAST_SEEN_STOCK_FILE, last_seen_stock)
            eventshop_channel = client.get_channel(config.EVENTSHOP_STOCK_CHANNEL_ID)
            if eventshop_channel:
                embed = build_embed('Event Shop Stock', eventshop_items, color=0xff6600)
                await send_or_edit(eventshop_channel, embed, 'stock_eventshop')

        next_stock_unix = min((item.get('end_date_unix', 0) for item in seed_items if item.get('end_date_unix', 0) > now), default=0)
        next_eventshop_unix = min((item.get('end_date_unix', 0) for item in eventshop_items if item.get('end_date_unix', 0) > now), default=0)

        if next_eventshop_unix and next_stock_unix:
            sleep_until = min(next_stock_unix, next_eventshop_unix)
        else:
            sleep_until = next_stock_unix or next_eventshop_unix

        await dynamic_sleep(sleep_until, 300)

@tasks.loop(count=1)
async def update_merchant():
    while True:
        stock = fetch_stock_api()
        merchant = stock.get('travelingmerchant_stock', {})
        merchant_name = merchant.get('merchantName', 'Traveling Merchant')
        merchant_items = merchant.get('stock', [])
        
        now = int(time.time())
        def is_active(item):
            start = item.get('start_date_unix', 0)
            end = item.get('end_date_unix', 0)
            return (start or 0) <= now < (end or 0)
        
        active_merchant_items = [item for item in merchant_items if is_active(item)]
        
        merchant_start = None
        merchant_end = None
        if active_merchant_items:
            merchant_start = active_merchant_items[0].get('start_date_unix')
            merchant_end = active_merchant_items[0].get('end_date_unix')

        last_seen_stock = load_json_file(LAST_SEEN_STOCK_FILE, {'seed': [], 'gear': [], 'merchant': {}, 'merchant_info': {'merchantName': None, 'stock_ids': [], 'active_window': [0, 0]}})
        new_merchant = False

        if merchant != last_seen_stock.get('merchant', {}):
            last_seen_stock['merchant'] = merchant
            save_json_file(LAST_SEEN_STOCK_FILE, last_seen_stock)

        if active_merchant_items:
            stock_ids = [item.get('item_id') for item in active_merchant_items]
            active_window = [merchant_start, merchant_end]
            last_merchant_info = last_seen_stock.get('merchant_info', {'merchantName': None, 'stock_ids': [], 'active_window': [0, 0]})
            if (
                merchant_name != last_merchant_info.get('merchantName') or
                stock_ids != last_merchant_info.get('stock_ids') or
                active_window != last_merchant_info.get('active_window')
            ):
                last_seen_stock['merchant_info'] = {
                    'merchantName': merchant_name,
                    'stock_ids': stock_ids,
                    'active_window': active_window
                }
                save_json_file(LAST_SEEN_STOCK_FILE, last_seen_stock)
                new_merchant = True

        if active_merchant_items:
            merchant_channel = client.get_channel(TRAVELING_MERCHANT_CHANNEL_ID)
            if merchant_channel:
                embed = build_traveling_merchant_embed(merchant_name, active_merchant_items)
                await send_or_edit(merchant_channel, embed, 'merchant')

        next_unix = min((item.get('end_date_unix', 0) for item in active_merchant_items if item.get('end_date_unix', 0) > now), default=0)
        await dynamic_sleep(next_unix, 14400)

@tasks.loop(count=1)
async def update_egg_channel():
    while True:
        egg_info = fetch_egg_info_api()
        egg_channel = client.get_channel(EGG_CHANNEL_ID)
        if egg_channel and egg_info:
            embed = build_info_embed('Eggs', egg_info, color=0xffcc00)
            await send_or_edit(egg_channel, embed, 'egg')

        valid_times = []
        for item in egg_info:
            last_seen = item.get('last_seen', 0)
            if last_seen and last_seen != 0 and last_seen != '0':
                try:
                    valid_times.append(int(last_seen))
                except (ValueError, TypeError):
                    continue
        next_unix = min(valid_times) if valid_times else 0
        await dynamic_sleep(next_unix, 1800)

@tasks.loop(minutes=5)
async def update_seed_gear_channels():
    seed_info = fetch_seed_info_api()
    gear_info = fetch_gear_info_api()
    seed_channel = client.get_channel(SEED_CHANNEL_ID)
    gear_channel = client.get_channel(GEAR_CHANNEL_ID)
    
    if seed_channel and seed_info:
        embed = build_info_embed('Seeds', seed_info, color=0x00ff99)
        await send_or_edit(seed_channel, embed, 'seed')
    if gear_channel and gear_info:
        embed = build_info_embed('Gear', gear_info, color=0x3399ff)
        await send_or_edit(gear_channel, embed, 'gear')

@tasks.loop(minutes=1)
async def update_weather_channels():
    try:
        weather_response = fetch_weather_api()
        weather_data = weather_response.get('weather', [])

        weather_info = fetch_weather_info_api()
        
        weather_updates_channel = client.get_channel(WEATHER_UPDATES_CHANNEL_ID)
        weather_channel = client.get_channel(WEATHER_CHANNEL_ID)

        active_weathers = [w for w in weather_data if w.get('active', False)]

        last_seen_weather = load_json_file(ACTIVE_WEATHER_FILE, {'active_weathers': []})
        now = int(time.time())
        
        current_active_weathers = []
        for weather in last_seen_weather.get('active_weathers', []):
            end_time = weather.get('end_duration_unix', 0)
            if end_time > now:
                current_active_weathers.append(weather)

        current_active_weather_ids = {w.get('weather_id') for w in current_active_weathers}
        new_active_weathers = [w for w in active_weathers if w.get('weather_id') not in current_active_weather_ids]

        if weather_updates_channel and new_active_weathers:
            for weather in new_active_weathers:
                weather_id = weather.get('weather_id', 'unknown')
                embed = build_weather_embed([weather])
                if embed:
                    await weather_updates_channel.send(embed=embed)

        if active_weathers != current_active_weathers:
            last_seen_weather['active_weathers'] = active_weathers
            save_json_file(ACTIVE_WEATHER_FILE, last_seen_weather)

        if weather_channel and weather_info:
            embed = build_info_embed('Weather', weather_info, color=0x00cccc, time_key='last_seen')
            await send_or_edit(weather_channel, embed, 'weather')
        
        await asyncio.sleep(60)
        
    except Exception as e:
        print(f"Error in update_weather_channels: {e}")
        await asyncio.sleep(60)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    update_stock.start()
    update_merchant.start()
    update_egg_channel.start()
    update_seed_gear_channels.start()
    update_weather_channels.start()

if __name__ == '__main__':
    client.run(DISCORD_TOKEN) 
