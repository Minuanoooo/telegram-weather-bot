# Weather Telegram Bot

A Telegram bot that shows current weather and sends a daily morning weather update, built with FastAPI and a real Telegram webhook.

## Technologies

- Python
- FastAPI
- SQLAlchemy (+ SQLite)
- APScheduler (daily scheduled broadcasts)
- OpenWeatherMap API
- Telegram Bot API (webhook-based)

## Features

- `/start` — welcome message with command list
- `/setcity <city>` — register or update your city
- `/weather` — get current weather on demand (temperature, wind speed, condition with emoji)
- `/stop` — toggle daily broadcast subscription on/off
- Automatic daily weather broadcast to all active subscribers
- Graceful handling of non-text messages and unknown commands

## Start

1. Clone the repository

2. Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```
pip install fastapi uvicorn sqlalchemy python-dotenv httpx apscheduler
```

4. Create a `.env` file in the project root with:
```
tg_key=your-telegram-bot-token
weather_key=your-openweathermap-api-key
```

5. Run the server:
```
uvicorn main:app --reload
```

6. Expose your local server publicly (needed for Telegram webhooks) using a tool like ngrok:
```
ngrok http 8000
```

7. Register the webhook with Telegram:
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/webhook
```

8. (Optional) Set up the command menu shown in Telegram's UI:
```
python set_commands.py
```

## Notes

- The daily broadcast time and timezone are configured in `main.py` inside `start_scheduler()`.
- Free ngrok URLs change on every restart — the webhook must be re-registered each time.
