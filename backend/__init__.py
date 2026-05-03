from flask import Flask
import flask_sqlalchemy #type: ignore
from flask_migrate import Migrate #type: ignore
import os

# Inicializamos as extensões fora da função para que outros arquivos possam importá-las
db = flask_sqlalchemy.SQLAlchemy()
migrate = Migrate()

def create_app():
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    
    app = Flask(__name__, template_folder=template_dir)
    
    # Configuração para SQLite (O arquivo será criado na pasta instance)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ifmaker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key_ifal')

    # Inicializa as extensões no app
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes_pages import main
    app.register_blueprint(main)

    return app