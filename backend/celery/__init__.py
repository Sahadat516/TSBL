from app.core.config import settings

broker_url = settings.celery_broker_url
result_backend = settings.celery_result_backend
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True
task_track_started = True
task_time_limit = 300
task_soft_time_limit = 240
worker_max_tasks_per_child = 200
worker_prefetch_multiplier = 1
result_expires = 86400
