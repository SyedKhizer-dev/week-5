class BaseController:

    def __init__(self, model, database):
        self.model = model
        self.db = database

    def create(self, data):
        instance = self.model(**data)

        try:
            self.db.session.add(instance)
            self.db.session.commit()

            return instance

        except Exception:
            self.db.session.rollback()
            raise

    def get_all(self):
        return self.db.session.execute(self.db.select(self.model)).scalars().all()

    def get_by_id(self, record_id):
        return self.db.session.get(self.model, record_id)

    def update(self, instance, data):
        try:
            for field, value in data.items():
                setattr(instance, field, value)

            self.db.session.commit()

            return instance

        except Exception:
            self.db.session.rollback()
            raise
