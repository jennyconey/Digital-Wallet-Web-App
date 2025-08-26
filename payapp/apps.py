from django.apps import AppConfig
from django.contrib.auth import get_user_model


class PayappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payapp'

    def ready(self):
        User = get_user_model()
        if not User.objects.filter(username='admin1').exists():
            User.objects.create_superuser('admin1', 'admin1@example.com', 'admin1')
