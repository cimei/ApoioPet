"""
.. topic:: envios (views)

    Informações sobre envios.

"""

# views.py dentro da pasta envios

from flask import render_template, url_for, send_from_directory, redirect, Blueprint
from flask_login import current_user, login_required
from sqlalchemy import cast, Date
from sqlalchemy.sql import label
from sqlalchemy.orm import aliased
from project import db, app
from project.core.views import data_ref
from project.models import Pessoas, planos_entregas,\
                           planos_trabalhos, envio_itens
from project.envios.forms import CSV_Form

from datetime import datetime as dt, timedelta

import csv, os

envios = Blueprint("envios",__name__,template_folder='templates')  


## envios não realizados

@envios.route('/envios_insucesso')
@login_required
def envios_insucesso():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta tela para escolha do tipo de envio mal sucedido.                             |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """                           

    return render_template('envio.html')


@envios.route('/envios_insucesso_pe',methods=['GET','POST'])
@login_required
def envios_insucesso_pe():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta dados dos PEs cujo envio não foi bem sucedido.                               |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """                    

    tipo = 'pe'

    dias = os.environ.get('DIAS_DATA_REF')

    envios_sem_sucesso = db.session.query(envio_itens.id,
                                          envio_itens.tipo,
                                          envio_itens.uid,
                                          envio_itens.sucesso,
                                          envio_itens.erros,
                                          envio_itens.created_at,
                                          planos_entregas.nome,
                                          planos_entregas.status)\
                            .outerjoin(planos_entregas, planos_entregas.id == envio_itens.uid)\
                            .filter(envio_itens.sucesso == 0,
                                    envio_itens.tipo == 'entrega',
                                    envio_itens.created_at >= data_ref(dias))\
                            .order_by(envio_itens.created_at.cast(Date).desc(),
                                      planos_entregas.nome)\
                            .all() 
                                          

    quantidade = len(envios_sem_sucesso)

    qtd_envios_sem_sucesso_total = db.session.query(envio_itens.id)\
                                             .filter(envio_itens.sucesso == 0,
                                                     envio_itens.tipo == 'entrega')\
                                             .count()

    form = CSV_Form()

    if form.validate_on_submit():
        
        csv_caminho_arquivo = os.path.normpath('/app/project/static/'+ tipo +'.csv')

        dados_a_escrever = [[e.nome, e.status, e.erros, e.created_at] for e in envios_sem_sucesso]
        
        header = ['Nome', 'Status','Erro','Data']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', tipo +'.csv')

        return redirect(url_for('static', filename = tipo +'.csv'))
            

    return render_template('lista_envios_sem_sucesso.html', 
                                            envios_sem_sucesso = envios_sem_sucesso,
                                            quantidade = quantidade,
                                            qtd_envios_sem_sucesso_total = qtd_envios_sem_sucesso_total,
                                            tipo = tipo,
                                            form = form,
                                            data_ref = data_ref(dias))

@envios.route('/envios_insucesso_pt',methods=['GET','POST'])
@login_required
def envios_insucesso_pt():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta dados dos PTs cujo envio não foi bem sucedido.                               |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """    

    tipo = 'pt'       

    dias = os.environ.get('DIAS_DATA_REF')         
                                                                                                           
    donos_pts = aliased(Pessoas)                                                                          
        
    envios_sem_sucesso = db.session.query(envio_itens.id,
                                          envio_itens.tipo,
                                          envio_itens.uid,
                                          envio_itens.sucesso,
                                          envio_itens.erros,
                                          envio_itens.created_at,
                                          planos_trabalhos.numero,
                                          label('pt_dono',donos_pts.nome),
                                          label('status_pt',planos_trabalhos.status))\
                            .outerjoin(planos_trabalhos, planos_trabalhos.id == envio_itens.uid)\
                            .outerjoin(donos_pts, donos_pts.id == planos_trabalhos.usuario_id)\
                            .filter(envio_itens.sucesso == 0,
                                    envio_itens.tipo == 'trabalho',
                                    envio_itens.created_at >= data_ref(dias))\
                            .order_by(envio_itens.created_at.cast(Date).desc(),
                                      donos_pts.nome)\
                            .all() 
                                          

    quantidade = len(envios_sem_sucesso)

    qtd_envios_sem_sucesso_total = db.session.query(envio_itens.id)\
                                             .filter(envio_itens.sucesso == 0,
                                                     envio_itens.tipo == 'trabalho')\
                                             .count()

    form = CSV_Form()

    if form.validate_on_submit():
        
        csv_caminho_arquivo = os.path.normpath('/app/project/static/'+ tipo +'.csv')

        dados_a_escrever = [[str(e.numero) +' - '+e.pt_dono, e.status_pt, e.erros, e.created_at] for e in envios_sem_sucesso]
        
        header = ['Nº - Nome', 'Status','Erro','Data']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', tipo +'.csv')

        return redirect(url_for('static', filename = tipo +'.csv'))
            

    return render_template('lista_envios_sem_sucesso.html', 
                                            envios_sem_sucesso = envios_sem_sucesso,
                                            quantidade = quantidade,
                                            qtd_envios_sem_sucesso_total = qtd_envios_sem_sucesso_total,
                                            tipo = tipo,
                                            form = form,
                                            data_ref = data_ref(dias))


@envios.route('/envios_insucesso_par',methods=['GET','POST'])
@login_required
def envios_insucesso_par():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta dados dos Participantes cujo envio não foi bem sucedido.                     |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """  

    tipo = 'par'  

    dias = os.environ.get('DIAS_DATA_REF')                
                                                                                                                   
    envios_sem_sucesso = db.session.query(envio_itens.id,
                                          envio_itens.tipo,
                                          envio_itens.uid,
                                          envio_itens.sucesso,
                                          envio_itens.erros,
                                          envio_itens.created_at,
                                          label('participante_nome',Pessoas.nome),
                                          Pessoas.matricula)\
                            .outerjoin(Pessoas, Pessoas.id == envio_itens.uid)\
                            .filter(envio_itens.sucesso == 0,
                                    envio_itens.tipo == 'participante',
                                    envio_itens.created_at >= data_ref(dias))\
                            .order_by(envio_itens.created_at.cast(Date).desc(),
                                      Pessoas.nome)\
                            .all() 
                                          
    quantidade = len(envios_sem_sucesso)

    qtd_envios_sem_sucesso_total = db.session.query(envio_itens.id)\
                                             .filter(envio_itens.sucesso == 0,
                                                     envio_itens.tipo == 'participante')\
                                             .count()

    form = CSV_Form()

    if form.validate_on_submit():
        
        csv_caminho_arquivo = os.path.normpath('/app/project/static/'+ tipo +'.csv')

        dados_a_escrever = [[e.participante_nome, e.matricula, e.erros, e.created_at] for e in envios_sem_sucesso]
        
        header = ['Nome', 'Matrícula','Erro','Data']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', tipo +'.csv')

        return redirect(url_for('static', filename = tipo +'.csv'))    
        
    return render_template('lista_envios_sem_sucesso.html', 
                                            envios_sem_sucesso = envios_sem_sucesso,
                                            quantidade = quantidade,
                                            qtd_envios_sem_sucesso_total = qtd_envios_sem_sucesso_total,
                                            tipo = tipo,
                                            form = form,
                                            data_ref = data_ref(dias))


