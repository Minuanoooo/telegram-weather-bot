import os
import httpx
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("tg_key")

commands = [
    {"command": "start", "description": "Начать работу"},
    {"command": "setcity", "description": "Установить город"},
    {"command": "weather", "description": "Узнать погоду"},
    {"command": "stop", "description": "Вкл/выкл рассылку"},
]

url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
response = httpx.post(url, json={"commands": commands})
print(response.json())