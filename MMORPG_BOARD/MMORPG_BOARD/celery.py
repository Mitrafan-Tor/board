import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MMORPG_BOARD.settings')

app = Celery('MMORPG_BOARD')

# Используем строку настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач во всех приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Расписание для периодических задач
app.conf.beat_schedule = {
    'weekly-newsletter': {
        'task': 'board.tasks.send_weekly_newsletter',
        'schedule': crontab(hour=8, minute=0, day_of_week=1),  # Понедельник 8:00
    },
}