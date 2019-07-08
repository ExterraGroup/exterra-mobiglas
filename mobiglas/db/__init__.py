from peewee import *

from mobiglas.config import settings

class SqliteInstance:
    def __init__(self):
        self.database = SqliteDatabase(settings.db.path)


client = SqliteInstance()
database = client.database
database.connect()


class BaseModel(Model):
    class Meta:
        database = database


def get_1(model, query):
    """
        This function will not throw an exception when there are no results.
    :param model: Model
    :param query: Expression
    :return:
    """
    results = model.select().where(query).limit(1)
    return results[0] if len(results) > 0 else None


def save_and_get(model):
    """
        Use this if there are triggers updating values server-side.
        Server-side updates will not be reflected in the save model.
        It must be re-retrieved.

        Note: may be unsafe in some async operations
    :param model: OLD.Model
    :return: NEW.Model
    """
    model.save()
    return model.get_by_id(model.id)


def execute(sql):
    database.execute_sql(sql, commit=True)
