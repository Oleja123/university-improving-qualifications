import logging

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.engine import Engine
from sqlalchemy import event


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
csrf = CSRFProtect()

from app.services.executer_service import Executer
from app.services.scheduler import Scheduler


login.login_view = 'auth.login'
login.login_message = ('Пожалуйста авторизуйтесь, чтобы просматривать данную страницу')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log'
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    csrf.init_app(app)
    Session(app)
    scheduler = Scheduler(app)
    scheduler.set_executer(Executer())
    scheduler.init_work()

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    if 'postgresql' not in app.config['SQLALCHEMY_DATABASE_URI']:
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    return app

from app import models