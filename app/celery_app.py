from celery import Celery
import os

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

celery_app = Celery('tasks', broker=broker_url, backend=result_backend)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks
celery_app.autodiscover_tasks(['app.tasks'], force=True)

if __name__ == '__main__':
    celery_app.start()