import os
import requests
from celery import Celery
from databases.databases import get_user_admin, check_time
from dotenv import load_dotenv
from celery.schedules import crontab
from redis import Redis

load_dotenv()

celery = Celery(
    'main',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
)
token = os.getenv('TOKEN')
redis_client = Redis(host='localhost', port=6379, db=0)

celery.conf.timezone = 'UTC'

@celery.task()
def send_telegram_message():
    lock_key = 'send_telegram_message_lock'
    with redis_client.lock(lock_key, timeout=60):
        datas = check_time()
        if datas:
            admins = get_user_admin()
            api_url = f"https://api.telegram.org/bot{token}/sendPhoto"

            for data in datas:
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                lavozim = data.get('lavozim')
                image_url = data.get('image')

                chat_message = (
                    f"Bugun {first_name} {last_name} {lavozim}ning tavallud topgan kun🎊🎉"
                )
                for admin in admins:
                    chat_id = admin[-1]

                    payload = {
                        "chat_id": chat_id,
                        "caption": chat_message,
                        "photo": image_url,
                    }

                    try:
                        response = requests.post(api_url, json=payload)
                        response.raise_for_status()
                    except requests.RequestException as e:
                        print(f"Failed to send message to Telegram: {e}")
                        continue

            return True

celery.conf.beat_schedule = {
    'send_telegram_message': {
        'task': 'celery_app.send_telegram_message',
        'schedule': crontab(hour=3, minute=0),
    },
}
