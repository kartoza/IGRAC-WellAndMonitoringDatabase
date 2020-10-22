from django.conf import settings

try:
    GWML2DATABASE = settings.GWML2_DATABASE_CONFIG
except AttributeError:
    GWML2DATABASE = 'default'

DEFAULT_DATABASE = 'default'


class GWML2Router(object):
    """
        A router to control all database operations on models in the
        auth and contenttypes applications.
        """
    app_label = 'gwml2'

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == self.app_label:
            return GWML2DATABASE
        return DEFAULT_DATABASE

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label == self.app_label:
            return GWML2DATABASE
        return DEFAULT_DATABASE

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if obj1._state.db == obj2._state.db:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.app_label:
            return db == GWML2DATABASE
        elif app_label == self.app_label:
            return db == GWML2DATABASE
        else:
            return db == DEFAULT_DATABASE
