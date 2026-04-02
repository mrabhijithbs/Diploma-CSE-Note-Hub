from django.apps import AppConfig


class NotesConfig(AppConfig):
    name = 'notes'
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notes'

    def ready(self):
        import notes.signals  # This line is crucial!