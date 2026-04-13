from django.apps import AppConfig


class CrmConfig(AppConfig):
    name = 'core.crm'

    def ready(self):
        import core.crm.signals.message_signal
