"""
.. topic:: trabalhos (views)

    Planos de Trabalho.

.. topic:: Ações relacionadas a Planos de Trabalho



"""

# views.py dentro da pasta trabalhos

from flask import render_template, Blueprint, send_from_directory, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy import func, case, literal_column
from sqlalchemy.sql import label
from sqlalchemy.orm import aliased
from project import db, app
from project.core.views import data_ref
from project.models import Unidades, Pessoas, planos_trabalhos, planos_trabalhos_consolidacoes, planos_trabalhos_entregas, atividades,\
                           avaliacoes, tipos_modalidades, planos_entregas_entregas

from project.trabalhos.forms import CSV_Form

import os, csv

from datetime import datetime as dt

import random
import string

trabalhos = Blueprint("trabalhos",__name__,template_folder='templates')


def ponto_por_virgula(valor):
    if valor != None and valor != '':
        return str(valor).replace('.',',')
    else:
        return 'N.I.'            

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


# lista dos planos de trabalho da unidade
@trabalhos.route('<tipo>/lista_pts',methods=['GET','POST'])
@login_required
def lista_pts(tipo):

    """
        +----------------------------------------------------------------------+
        |Lista os planos de trabalho, bem como registros                       |
        |associados.                                                           |
        |                                                                      |
        +----------------------------------------------------------------------+
    """
    
    
    hoje = dt.today()

    dias = os.environ.get('DIAS_DATA_REF')


    #subquery que conta trabalhos em cada plano de trabalho 
    trabalhos = db.session.query(atividades.plano_trabalho_id,
                                label('qtd_trabalhos',func.count(atividades.id)))\
                          .filter(atividades.deleted_at == None)\
                          .group_by(atividades.plano_trabalho_id)\
                          .subquery() 
                        
    #subquery que conta avaliações em pt a partir de plano_trabalho_consolidacao
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     label('qtd_aval',func.count(avaliacoes.id)))\
                              .join(avaliacoes, avaliacoes.plano_trabalho_consolidacao_id == planos_trabalhos_consolidacoes.id)\
                              .filter(avaliacoes.data_avaliacao <= hoje,
                                      planos_trabalhos_consolidacoes.deleted_at == None)\
                              .group_by(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .subquery()                                                                                                                            
    
    if tipo == 'geral':
    
        planos_trabalho_lista = db.session.query(planos_trabalhos.id,
                                                planos_trabalhos.data_inicio,
                                                planos_trabalhos.data_fim,
                                                planos_trabalhos.carga_horaria,
                                                planos_trabalhos.forma_contagem_carga_horaria,
                                                planos_trabalhos.status,
                                                label('forma',tipos_modalidades.nome),
                                                planos_trabalhos.data_envio_api_pgd,
                                                Pessoas.nome,
                                                Unidades.sigla,
                                                label('situacao',planos_trabalhos.status),
                                                label('vencido',case((planos_trabalhos.data_fim < hoje, literal_column("'s'")), else_=literal_column("'n'"))),
                                                trabalhos.c.qtd_trabalhos,
                                                avaliacoes_pt.c.qtd_aval)\
                                        .filter(planos_trabalhos.deleted_at == None,
                                                planos_trabalhos.data_inicio >= data_ref(dias))\
                                        .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                        .join(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                        .join(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                        .order_by(planos_trabalhos.status,Unidades.sigla,Pessoas.nome,planos_trabalhos.data_inicio)\
                                        .outerjoin(trabalhos, trabalhos.c.plano_trabalho_id == planos_trabalhos.id)\
                                        .outerjoin(avaliacoes_pt, avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id)\
                                        .all()

        quantidade = len(planos_trabalho_lista) 

    elif tipo == 'conc_sava':

        planos_trabalho_lista = db.session.query(planos_trabalhos.id,
                                                 planos_trabalhos.data_inicio,
                                                 planos_trabalhos.data_fim,
                                                 planos_trabalhos.carga_horaria,
                                                 planos_trabalhos.forma_contagem_carga_horaria,
                                                 planos_trabalhos.status,
                                                 label('forma',tipos_modalidades.nome),
                                                 planos_trabalhos.data_envio_api_pgd,
                                                 Pessoas.nome,
                                                 Unidades.sigla,
                                                 label('situacao',planos_trabalhos.status),
                                                 label('vencido',case((planos_trabalhos.data_fim < hoje, literal_column("'s'")), else_=literal_column("'n'"))),
                                                 trabalhos.c.qtd_trabalhos,
                                                 avaliacoes_pt.c.qtd_aval)\
                                  .filter(planos_trabalhos.deleted_at == None,
                                          planos_trabalhos.status == 'CONCLUIDO',
                                          avaliacoes_pt.c.qtd_aval == 0)\
                                  .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                  .join(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                  .join(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                  .order_by(planos_trabalhos.status,Unidades.sigla,Pessoas.nome,planos_trabalhos.data_inicio)\
                                  .outerjoin(trabalhos, trabalhos.c.plano_trabalho_id == planos_trabalhos.id)\
                                  .outerjoin(avaliacoes_pt, avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id)\
                                  .all()

        quantidade = len(planos_trabalho_lista)
    
    else:

        if tipo == 'ativ_venc':
            status_pesq = 'ATIVO'
        elif tipo == 'incl_venc':
            status_pesq = 'INCLUIDO'
        elif tipo == 'agas_venc':
            status_pesq = 'AGUARDANDO_ASSINATURA'
    
        planos_trabalho_lista = db.session.query(planos_trabalhos.id,
                                                 planos_trabalhos.data_inicio,
                                                 planos_trabalhos.data_fim,
                                                 planos_trabalhos.carga_horaria,
                                                 planos_trabalhos.forma_contagem_carga_horaria,
                                                 planos_trabalhos.status,
                                                 label('forma',tipos_modalidades.nome),
                                                 planos_trabalhos.data_envio_api_pgd,
                                                 Pessoas.nome,
                                                 Unidades.sigla,
                                                 label('situacao',planos_trabalhos.status),
                                                 label('vencido',case((planos_trabalhos.data_fim < hoje, literal_column("'s'")), else_=literal_column("'n'"))),
                                                 trabalhos.c.qtd_trabalhos,
                                                 avaliacoes_pt.c.qtd_aval)\
                                  .filter(planos_trabalhos.deleted_at == None,
                                          planos_trabalhos.status == status_pesq,
                                          planos_trabalhos.data_fim < hoje)\
                                  .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                  .join(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                  .join(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                  .order_by(planos_trabalhos.status,Unidades.sigla,Pessoas.nome,planos_trabalhos.data_inicio)\
                                  .outerjoin(trabalhos, trabalhos.c.plano_trabalho_id == planos_trabalhos.id)\
                                  .outerjoin(avaliacoes_pt, avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id)\
                                  .all()

        quantidade = len(planos_trabalho_lista) 


    qtd_pts_total =  db.session.query(planos_trabalhos.id).filter(planos_trabalhos.deleted_at == None).count()
    
 
    form = CSV_Form()

    if form.validate_on_submit():

        csv_caminho_arquivo = os.path.normpath('/app/project/static/planos_trabalho.csv')
        
        dados_a_escrever = [[p.nome, p.sigla, p.data_inicio, p.data_fim, p.forma, p.situacao, str(p.carga_horaria) +'('+p.forma_contagem_carga_horaria+')', p.qtd_trabalhos, p.qtd_aval] for p in planos_trabalho_lista]

        header = ['Pessoa', 'Unidade','Início','Fim', 'Forma', 'Situação', 'C.H.', 'Trabalhos', 'Avaliações']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', 'planos_trabalho.csv')

        return redirect(url_for('static', filename = 'planos_trabalho.csv'))    
    
    return render_template ('lista_pts.html', planos_trabalho_lista = planos_trabalho_lista, 
                                              quantidade = quantidade,
                                              qtd_pts_total = qtd_pts_total,
                                              tipo = tipo,
                                              form = form,
                                              data_ref = data_ref(dias))



## lista trabalhos (atividades) de um plano de trabalho
@trabalhos.route('/<ptId>/consulta_trabalhos')
@login_required
def consulta_trabalhos(ptId):
    """
    +---------------------------------------------------------------------------------------+
    |Lista os trabalhos (atividades) que foram registrados em um plano de trabalho.         |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    # resgata registros em atividades
    trabalhos = db.session.query(atividades.descricao,
                                 label('entrega',planos_entregas_entregas.descricao),
                                 atividades.status,
                                 atividades.carga_horaria,
                                 atividades.progresso,
                                 atividades.data_inicio,
                                 atividades.data_entrega)\
                          .filter(atividades.deleted_at == None,
                                  atividades.plano_trabalho_id == ptId)\
                          .outerjoin(planos_trabalhos_entregas, planos_trabalhos_entregas.id == atividades.plano_trabalho_entrega_id)\
                          .outerjoin(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                          .all()

    quantidade = len(trabalhos)                    

    return render_template('consulta_trabalhos.html', trabalhos=trabalhos,
                                                      quantidade = quantidade)


## lista avaliações de um plano de trabalho
@trabalhos.route('/<ptId>/consulta_avaliacoes')
@login_required
def consulta_avaliacoes(ptId):
    """
    +---------------------------------------------------------------------------------------+
    |Lista as avaliações que foram registrados em um plano de trabalho.                     |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    hoje = dt.today()
    
    avaliados = aliased(Pessoas)

    # avaliações de um pt
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     avaliacoes.data_avaliacao,
                                     avaliacoes.nota,
                                     label('avaliador',Pessoas.nome),
                                     label('avaliado',avaliados.nome),
                                     planos_trabalhos.data_inicio,
                                     planos_trabalhos.data_fim,
                                     avaliacoes.recurso)\
                              .join(avaliacoes, avaliacoes.plano_trabalho_consolidacao_id == planos_trabalhos_consolidacoes.id)\
                              .join(planos_trabalhos, planos_trabalhos.id == planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .outerjoin(Pessoas, Pessoas.id == avaliacoes.avaliador_id)\
                              .join(avaliados, avaliados.id == planos_trabalhos.usuario_id)\
                              .filter(avaliacoes.data_avaliacao <= hoje,
                                      avaliacoes.deleted_at == None,
                                      planos_trabalhos_consolidacoes.plano_trabalho_id == ptId)\
                              .all()
                              
    quantidade = len(avaliacoes_pt)                    

    return render_template('consulta_avaliacoes.html', avaliacoes_pt=avaliacoes_pt,
                                                      quantidade = quantidade)


