import requests
import asyncio
import os

API_SEED_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=seed'
API_GEAR_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=gear'
API_EGG_INFO = 'https://api.joshlei.com/v2/growagarden/info?type=egg'
API_WEATHER = 'https://api.joshlei.com/v2/growagarden/weather'

def fetch_seed_info():
    return requests.get(API_SEED_INFO).json()

def fetch_gear_info():
    return requests.get(API_GEAR_INFO).json()

def fetch_egg_info():
    return requests.get(API_EGG_INFO).json()

def fetch_weather():
    return requests.get(API_WEATHER).json().get('weather', [])

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

async def get_images():
    ensure_dir('assets/seed')
    ensure_dir('assets/gear')
    ensure_dir('assets/egg')
    ensure_dir('assets/weather')

    seed_items = fetch_seed_info()
    gear_items = fetch_gear_info()
    egg_items = fetch_egg_info()
    weather_items = fetch_weather()

    saved = {'seed': 0, 'gear': 0, 'egg': 0, 'weather': 0}

    for item in seed_items:
        if item.get('last_seen') == '0':
            continue
        
        image_url = item.get('icon')
        if image_url:
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(f'assets/seed/{item.get("item_id")}.png', 'wb') as f:
                        f.write(image_response.content)
                    print(f'Saved seed/{item.get("item_id")}.png')
                    saved['seed'] += 1
                else:
                    print(f'Failed to fetch image for seed {item.get("item_id")}: {image_response.status_code}')
            except Exception as e:
                print(f'Error fetching image for seed {item.get("item_id")}: {e}')
        else:
            print(f'No image URL found for seed {item.get("item_id")}')

    for item in gear_items:
        if item.get('last_seen') == '0':
            continue
        
        image_url = item.get('icon')
        if image_url:
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(f'assets/gear/{item.get("item_id")}.png', 'wb') as f:
                        f.write(image_response.content)
                    print(f'Saved gear/{item.get("item_id")}.png')
                    saved['gear'] += 1
                else:
                    print(f'Failed to fetch image for gear {item.get("item_id")}: {image_response.status_code}')
            except Exception as e:
                print(f'Error fetching image for gear {item.get("item_id")}: {e}')
        else:
            print(f'No image URL found for gear {item.get("item_id")}')

    for item in egg_items:
        if item.get('last_seen') == '0':
            continue
        
        image_url = item.get('icon')
        if image_url:
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(f'assets/egg/{item.get("item_id")}.png', 'wb') as f:
                        f.write(image_response.content)
                    print(f'Saved egg/{item.get("item_id")}.png')
                    saved['egg'] += 1
                else:
                    print(f'Failed to fetch image for egg {item.get("item_id")}: {image_response.status_code}')
            except Exception as e:
                print(f'Error fetching image for egg {item.get("item_id")}: {e}')
        else:
            print(f'No image URL found for egg {item.get("item_id")}')

    for item in weather_items:
        if item.get('last_seen') == '0':
            continue
        
        image_url = item.get('icon')
        weather_id = item.get('weather_id')
        if image_url and weather_id:
            try:
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    with open(f'assets/weather/{weather_id}.png', 'wb') as f:
                        f.write(image_response.content)
                    print(f'Saved weather/{weather_id}.png')
                    saved['weather'] += 1
                else:
                    print(f'Failed to fetch image for weather {weather_id}: {image_response.status_code}')
            except Exception as e:
                print(f'Error fetching image for weather {weather_id}: {e}')
        else:
            print(f'No image URL found for weather {weather_id}')

    print('\nSummary:')
    for k, v in saved.items():
        print(f'{k.capitalize()} images saved: {v}')

if __name__ == "__main__":
    asyncio.run(get_images())
