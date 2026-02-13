from project import app
from project import db
from datetime import datetime as dt
import os
import locale
import ast
import re
import logging

from sqlalchemy import func

from project.models import migrations

from threading import Timer

gunicorn_logger = logging.getLogger('gunicorn.error')
if gunicorn_logger.handlers:
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

# filtros cusomizado para o jinja

@app.template_filter('verifica_serv_bd')
def verifica_serv_bd(chave):
    return os.getenv(chave)
#
@app.template_filter('retorna_var_amb')
def retorna_var_amb(chave):
    return os.getenv(chave)

@app.template_filter('str_to_date')
def str_to_date(valor):
    if valor == None or valor == '':
        return 0
    else:
        return dt.strptime(valor,'%Y-%m-%dT%H:%M:%S')   
    
@app.template_filter('decimal_com_virgula')
def decimal_com_virgula(valor,casas_decimais):
    if valor == None or valor == '':
        return 0
    else:
        if casas_decimais != 0:
            return locale.format_string('%.1f',round(valor,casas_decimais),grouping=True)
        else:
            return locale.format_string('%d',round(valor),grouping=True)

@app.template_filter('splitpart')
def splitpart (value, char = '/'):
    return value.split(char)                  

@app.template_filter('dic_key')
def str_to_dict (valor):
    return list((ast.literal_eval(valor)).keys())[0]

@app.template_filter('dic_value')
def str_to_dict (valor):
    return list((ast.literal_eval(valor)).values())[0]

@app.template_filter('safe_percentage')
def safe_percentage(numerator, denominator, decimal_places=1):
    """Calcula percentual de forma segura, evitando divisão por zero"""
    if denominator == 0 or denominator is None:
        return "N/A"
    if numerator is None:
        return "N/A"
    try:
        result = (numerator / denominator) * 100
        return locale.format_string(f'%.{decimal_places}f', round(result, decimal_places), grouping=True)
    except (TypeError, ValueError, ZeroDivisionError):
        return "N/A"

@app.template_filter('safe_division')
def safe_division(numerator, denominator, default="0", decimal_places=2):
    """Divisão segura com valor padrão configurável"""
    if denominator == 0 or denominator is None:
        return default
    if numerator is None:
        return default
    try:
        result = numerator / denominator
        return locale.format_string(f'%.{decimal_places}f', round(result, decimal_places), grouping=True)
    except (TypeError, ValueError, ZeroDivisionError):
        return default

def obter_versao_dados():
    try:
        migracao_versao = db.session.query(migrations.migration)\
                                  .filter(func.lower(migrations.migration).contains('version'))\
                                  .order_by(migrations.id.desc())\
                                  .first()

        if migracao_versao and migracao_versao[0]:
            match = re.search(r'version(.*)$', migracao_versao[0], flags=re.IGNORECASE)
            if match:
                return match.group(1).lstrip(' _-:') or None
    except Exception:
        return None

    return None

@app.context_processor
def injeta_versao_dados():
    return {'versao_dados': obter_versao_dados()}

with app.app_context():
    versao_dados = obter_versao_dados()
    app.logger.warning('Versão dos dados do banco (migrations): %s', versao_dados or 'não identificada')

if __name__ == '__main__':
    app.run(port = 5003)