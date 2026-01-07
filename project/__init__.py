# __init__.py dentro da pasta project

import os
import locale
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import pyodbc

pyodbc.setDecimalSeparator('.')

TOP_LEVEL_DIR = os.path.abspath(os.curdir)

app = Flask (__name__, static_url_path=None, instance_relative_config=True, static_folder='/app/project/static')

app.config.from_pyfile('flask.cfg')

app.static_url_path=app.config.get('STATIC_PATH')

db = SQLAlchemy(app)

mail = Mail(app)

locale.setlocale( locale.LC_ALL, '' )


#################################
## log in - cofigurações

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'usuarios.login'

############################################
## blueprints - registros

from project.core.views import core
from project.error_pages.handlers import error_pages
from project.usuarios.views import usuarios

from project.planejamento.views import planejamento
from project.entregas.views import entregas
from project.trabalhos.views import trabalhos
from project.pessoas.views import pessoas
from project.unidades.views import unidades
from project.envios.views import envios
from project.intervencoes.views import intervencoes

app.register_blueprint(core)
app.register_blueprint(usuarios)
app.register_blueprint(error_pages)

app.register_blueprint(planejamento,url_prefix='/planejamento')
app.register_blueprint(entregas,url_prefix='/entregas')
app.register_blueprint(trabalhos,url_prefix='/trabalhos')
app.register_blueprint(pessoas,url_prefix='/pessoas')
app.register_blueprint(unidades,url_prefix='/unidades')
app.register_blueprint(envios,url_prefix='/envios')
app.register_blueprint(intervencoes,url_prefix='/intervencoes')



