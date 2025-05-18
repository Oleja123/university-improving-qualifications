from flask_apscheduler import APScheduler

from app.interfaces.iexecuter import IExecuter


class Scheduler(APScheduler):

    def __init__(self, app):
        super().__init__()
        self.app = app

    def set_executer(self, executer: IExecuter):
        self.executer = executer

    def init_work(self):
        self.add_job(
            id='ban_users',
            func=self._job_wrapper,
            trigger='interval',
            days=1
        )

        self.start()

    def _job_wrapper(self):
        with self.app.app_context():
            self.executer.execute()
