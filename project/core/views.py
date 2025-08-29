"""
.. topic:: Core (views)

    Este é o módulo inicial do sistema.

    Apresenta as telas de início, informação e procedimentos genéricos do sistema.

.. topic:: Ações relacionadas ao Core

    * Funções:
        PegaArquivo   
    
    * index: Tela inicial. Pede o login do usuário.
    * inicio: Rotinas executadas quando se entra no aplicativo.
    * info: informações do sistema.
    * internas_i: abre tela de menu das funções internas
    * apoio_i: abre tela de menu das funções de apoio
    * cargas_i: abre tela de menu das cargas
    

"""

# core/views.py

from flask import render_template,url_for, redirect, Blueprint

from datetime import datetime as dt, timedelta

import os

from project.core.forms import data_ref_Form

core = Blueprint("core",__name__)

# n dias antes de hoje (hoje não entra na conta)
def data_ref(n):
    hoje = dt.today()
    d = timedelta(days = int(n))
    data_ref = hoje - d
    return data_ref


@core.route('/')
def index():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela de login.                                                             |
    +---------------------------------------------------------------------------------------+
    """

    return redirect(url_for('usuarios.login'))

@core.route('/inicio')
def inicio():
    
    """
    +---------------------------------------------------------------------------------------+
    |Ações quando o aplicativo é colocado no ar.                                            |
    |Inicia jobs de envio e de reenvio conforme ultimo registro de agendamento no log.      |
    +---------------------------------------------------------------------------------------+
    """

    dias_data_ref = os.environ.get('DIAS_DATA_REF')    

    return render_template ('index.html', data_ref = data_ref(dias_data_ref), dias_data_ref = dias_data_ref)  

@core.route('/info')
def info():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta a tela de informações do aplicativo.                                         |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('info.html')

@core.route('/data_referencia', methods=['GET','POST'])
def data_referencia():
    """
    +---------------------------------------------------------------------------------------+
    |Consulta e alteração da data de referência.                                            |
    +---------------------------------------------------------------------------------------+
    """

    form = data_ref_Form()

    if form.validate_on_submit():

        os.environ["DIAS_DATA_REF"] = str(form.dias_atras.data)

        return render_template('index.html', data_ref = data_ref(form.dias_atras.data), dias_data_ref = str(form.dias_atras.data))
    
    return render_template('dias_data_ref.html', form = form)

@core.route('/v_a')
def v_a():
    """
    +---------------------------------------------------------------------------------------+
    |Lista variáveis de ambiente.                                                           |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('v_a.html')



