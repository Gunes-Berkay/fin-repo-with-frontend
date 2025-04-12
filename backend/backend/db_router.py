class PapersDBRouter:
    """
    A router to control database operations on models for the papers app.
    """
    def db_for_read(self, model, **hints):
        """Direct read operations for specific models to the correct database."""
        if model._meta.app_label == 'charts':
            return 'papers_db'  # Use 'papers_db' for the 'papers_app' app
        return None

    def db_for_write(self, model, **hints):
        """Direct write operations for specific models to the correct database."""
        if model._meta.app_label == 'charts':
            return 'papers_db'  # Use 'papers_db' for the 'papers_app' app
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if both objects are in the same database."""
        db_set = {'papers_db','default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure migrations are only applied to the correct database."""
        if app_label == 'charts':
            return db == 'papers_db'
        return None
