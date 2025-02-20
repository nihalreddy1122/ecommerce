from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    verbose_name = _("Products Management")

    def ready(self):
        """
        This method is called when the application is ready.
        You can import and connect your signals here.
        """
        import products.signals  # Import signals to handle events like post_save or pre_save
