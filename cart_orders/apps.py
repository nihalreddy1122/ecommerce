from django.apps import AppConfig


class CartOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart_orders'


from django.apps import AppConfig

class CartOrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart_orders'

    def ready(self):
        import cart_orders.signals  # Import the signals module
