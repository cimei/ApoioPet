from project import app
from datetime import datetime as dt
import os
import locale
import ast

from threading import Timer

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
def decimal_com_virgula(valor):
    if valor == None or valor == '':
        return 0
    else:
        return locale.format_string('%.1f',round(valor,1),grouping=True) 

@app.template_filter('splitpart')
def splitpart (value, char = '/'):
    return value.split(char)                  

@app.template_filter('dic_key')
def str_to_dict (valor):
    return list((ast.literal_eval(valor)).keys())[0]

@app.template_filter('dic_value')
def str_to_dict (valor):
    return list((ast.literal_eval(valor)).values())[0]

if __name__ == '__main__':
    app.run(port = 5003)