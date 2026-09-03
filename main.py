from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session
from models import Subscribers
from database import Base, engine, get_db,Session
import os
from dotenv import load_dotenv
import httpx
from apscheduler.schedulers.background import BackgroundScheduler



load_dotenv()
WEATHER_TOKEN = os.getenv("weather_key")
BOT_TOKEN = os.getenv("tg_key")
app = FastAPI()
Base.metadata.create_all(engine)
scheduler = BackgroundScheduler()

weather_emojis = {
    "ясно": "☀️",
    "малооблачно": "🌤️",
    "рассеянные облака": "⛅",
    "облачно с прояснениями": "🌥️",
    "пасмурно": "☁️",
    "легкий дождь": "🌦️",
    "умеренный дождь": "🌧️",
    "сильный дождь": "🌧️",
    "гроза": "⛈️",
    "снег": "❄️",
    "туман": "🌫️",
}

@app.post("/webhook")
def telegram_webhook(update: dict, db: Session = Depends(get_db)):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")  
    
    if text is None:
        send_message(chat_id, f'Я пока не могу такого(')

    elif text.startswith("/start"):
        send_message(chat_id,f'Привет! Я бот погоды.\n\nКоманды:\n/setcity <город> — установить город\n/weather — узнать погоду сейчас\n/stop — отписаться от рассылки')

    elif text.startswith('/stop'):
        subscriber = db.query(Subscribers).filter(Subscribers.chat_id == chat_id).first()
        if subscriber:
            subscriber.is_active = not subscriber.is_active
            db.commit()
            if subscriber.is_active:
                send_message(chat_id, "Подписка включена")
            else:
                send_message(chat_id, "Подписка выключена")
        else:
            send_message(chat_id,f'Подписчик не найден')

    elif text.startswith("/setcity"):
        city = text.split()[-1]
        subscriber = db.query(Subscribers).filter(Subscribers.chat_id == chat_id).first()
        if not subscriber:
            subscriber = Subscribers(chat_id = chat_id, city = city)
            db.add(subscriber)
        else:
            subscriber.city = city
        db.commit()
        send_message(chat_id, f"Город установлен: {subscriber.city}")

    elif text.startswith('/weather'):
        subscriber = db.query(Subscribers).filter(Subscribers.chat_id == chat_id).first()
        if not subscriber:
            send_message(chat_id, "Укажите ваш город через /setcity")
        elif len(subscriber.city) == 0:
            send_message(chat_id,f'Укажите ваш город')
        else:
            send_message(chat_id, get_weather(subscriber.city))

    else:
        send_message(chat_id, 'Я пока такого не могу(')
def send_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    httpx.post(url, params={"chat_id": chat_id, "text": text})
def get_weather(city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_TOKEN}&units=metric&lang=ru"
    get = httpx.get(url)
    data = get.json()
    if data.get("cod") != 200:
        return "Не удалось найти такой город 😕"
    print(data)
    temp = data["main"]["temp"]
    wind = data['wind']['speed']
    description = data["weather"][0]["description"]
    emoji = weather_emojis.get(description, "🌍")
    weather = f'За окном {round(temp)}°C , скорость ветра {round(wind)} м/с, {description} {emoji}'
    return weather
def send_daily_weather():
    session = Session()
    daily = session.query(Subscribers).filter(Subscribers.is_active == True).all()
    for t in daily:
        send_message(t.chat_id, f'Доброе утро, за окном {get_weather(t.city)}.')
    session.close()
@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(send_daily_weather, "cron", hour=7, minute=00)
    scheduler.start()