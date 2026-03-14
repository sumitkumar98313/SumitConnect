from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts'

    def ready(self):
        # import signals here so they get registered when app starts
        # if we don't do this the signals won't work
        import accounts.signals
