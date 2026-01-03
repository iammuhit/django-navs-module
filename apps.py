from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NavsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.modules.navs'
    label = 'app__navs_module'
    verbose_name = _('navigation')
