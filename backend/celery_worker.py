from app import create_app
from celery import Celery
from celery.schedules import crontab

app = create_app()

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    # Map the old flask uppercase keys to celery's lowercase names
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND']
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)

# Config for periodic tasks
celery.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0), # Daily at 8 AM
    },
    'monthly-report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0), # 1st of every month at 9 AM
    }
}
celery.conf.timezone = 'UTC'

import tasks
