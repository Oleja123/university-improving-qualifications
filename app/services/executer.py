from app.interfaces.iexecuter import IExecuter
import sqlalchemy as sa

class Executer(IExecuter):
    def execute(self):
        query = sa.select()