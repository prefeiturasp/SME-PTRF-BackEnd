from config import celery_app

@celery_app.task()
def get_users_count():
    # A pointless Celery task to demonstrate usage.
    from django.contrib.auth import get_user_model
    return get_user_model().objects.count()