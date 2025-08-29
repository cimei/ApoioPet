"""
.. topic:: entregas (views)

    Planos de Entregas.

"""

# views.py dentro da pasta entregas

from flask import render_template, url_for, flash, redirect, Blueprint, send_from_directory
from flask_login import current_user, login_required
from sqlalchemy import func, case, literal_column, or_, distinct
from sqlalchemy.sql import label
from sqlalchemy.orm import aliased
from project import db, app
from project.core.views import data_ref
from project.models import Unidades, Pessoas, programas, planos_entregas, unidades_integrantes,\
                           avaliacoes, planos_entregas_entregas, planos_trabalhos_entregas, tipos_modalidades, planos_trabalhos_consolidacoes,\
                           planos_trabalhos

from project.entregas.forms import CSV_Form

from datetime import datetime as dt

import os, csv

entregas = Blueprint("entregas",__name__,template_folder='templates')    


## lista planos de entregas

@entregas.route('/lista_pe',methods=['GET','POST'])
@login_required
def lista_pe():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta os planos de entregas.                                                       |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """
        
    dias = os.environ.get('DIAS_DATA_REF')    

    unid_dados = db.session.query(Unidades.id, Unidades.sigla, Unidades.path)\
                            .all()

    entregas = db.session.query(planos_entregas_entregas.plano_entrega_id,
                                label('qtd_entregas',func.count(planos_entregas_entregas.id)))\
                         .group_by(planos_entregas_entregas.plano_entrega_id)\
                         .subquery()                                               
                            
    pts_todos_1 = db.session.query(label('pt_id',planos_trabalhos_entregas.plano_trabalho_id.distinct()),
                                   planos_trabalhos_entregas.plano_entrega_entrega_id,
                                   planos_entregas_entregas.plano_entrega_id)\
                            .join(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                            .subquery()
    planos_trab = db.session.query(label('pe_id',pts_todos_1.c.plano_entrega_id.distinct()),
                                   label('qtd_planos_trab',func.count(distinct(pts_todos_1.c.pt_id))))\
                            .group_by(pts_todos_1.c.plano_entrega_id)\
                            .subquery()                      
                                                                                      
                            
    unidades_pai = aliased(Unidades)                                                                          


    hoje = dt.now()
        
    planos_entregas_todos = db.session.query(planos_entregas.id,
                                       planos_entregas.status,
                                       planos_entregas.data_inicio,
                                       planos_entregas.data_fim,
                                       planos_entregas.deleted_at,
                                       entregas.c.qtd_entregas,
                                       planos_trab.c.qtd_planos_trab,
                                       Unidades.sigla,
                                       label('sigla_pai', unidades_pai.sigla),
                                       planos_entregas.unidade_id,
                                       Unidades.unidade_pai_id,
                                       label('vencido',case((planos_entregas.data_fim < hoje, literal_column("'s'")), else_=literal_column("'n'"))),
                                       avaliacoes.nota,
                                       avaliacoes.data_avaliacao,
                                       label('just_avalia',avaliacoes.justificativas),
                                       label('parecer_avalia',avaliacoes.justificativa))\
                                .join(Unidades, Unidades.id == planos_entregas.unidade_id)\
                                .outerjoin(unidades_pai, unidades_pai.id == Unidades.unidade_pai_id)\
                                .outerjoin(entregas, entregas.c.plano_entrega_id == planos_entregas.id)\
                                .outerjoin(planos_trab,planos_trab.c.pe_id == planos_entregas.id)\
                                .outerjoin(avaliacoes,avaliacoes.plano_entrega_id == planos_entregas.id)\
                                .filter(planos_entregas.deleted_at == None,
                                        planos_entregas.data_inicio >= data_ref(dias))\
                                .order_by(planos_entregas.status, Unidades.sigla, planos_entregas.data_inicio)\
                                .all() 
                               

    quantidade = len(planos_entregas_todos)

    qtd_pes_total =  db.session.query(planos_entregas.id).filter(planos_entregas.deleted_at == None).count()

    form = CSV_Form()

    if form.validate_on_submit():

        csv_caminho_arquivo = os.path.normpath('/app/project/static/planos_entrega.csv')
        
        dados_a_escrever = [[p.sigla, p.status, p.data_inicio, p.data_fim, p.qtd_entregas, p.qtd_planos_trab, p.nota] for p in planos_entregas_todos]

        header = ['Unidade', 'Status','Início','Fim', 'Qtd. Entregas', 'Qtd. PTs', 'Nota']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', 'planos_entrega.csv')

        return redirect(url_for('static', filename = 'planos_entrega.csv'))        

    return render_template('lista_pe.html', unid_dados = unid_dados,
                                            planos_entregas_todos = planos_entregas_todos,
                                            quantidade = quantidade,
                                            qtd_pes_total = qtd_pes_total,
                                            form = form,
                                            data_ref = data_ref(dias))


## consulta entregas de um plano de entregas

@entregas.route('/<peId>/consulta_entregas')
@login_required
def consulta_entregas(peId):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das entregas de um Plano de Entergas.                              |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   
    
    plano_entregas = db.session.query(planos_entregas.status,
                                      planos_entregas.data_inicio,
                                      planos_entregas.data_fim, 
                                      Unidades.sigla)\
                               .join(Unidades, Unidades.id == planos_entregas.unidade_id)\
                               .filter(planos_entregas.id == peId).first()
    
    entregas = db.session.query(planos_entregas_entregas).filter(planos_entregas_entregas.plano_entrega_id == peId).all()
    
    
    quantidade = len(entregas)
    
    return render_template("consulta_entregas.html", plano_entregas =plano_entregas, 
                                                     entregas = entregas,
                                                     quantidade = quantidade)
    
    
## lista planos de trabalho vinculados a um plano de entregas

@entregas.route('/<peId>/consulta_pts')
@login_required
def consulta_pts(peId):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista de planos de trabalho vinculados a um plano de entregas.           |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   

    hoje = dt.today().date()
    
    pe = db.session.query(planos_entregas.status,
                          planos_entregas.data_inicio,
                          planos_entregas.data_fim, 
                          Unidades.sigla)\
                   .join(Unidades, Unidades.id == planos_entregas.unidade_id)\
                   .filter(planos_entregas.id == peId).first()
                         

    #subquery que conta avaliações realizadas até em cada pt (exclui as autormáticas futuras)
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     label('qtd_aval',func.count(avaliacoes.id)))\
                              .join(planos_trabalhos_consolidacoes, planos_trabalhos_consolidacoes.id == avaliacoes.plano_trabalho_consolidacao_id)\
                              .group_by(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .subquery()                                            
    
    
    planos_trab_pe  = db.session.query(planos_trabalhos.id.distinct(),
                                       planos_trabalhos.data_inicio,
                                       planos_trabalhos.data_fim,
                                       planos_trabalhos.carga_horaria,
                                       planos_trabalhos.forma_contagem_carga_horaria,
                                       planos_trabalhos.status,
                                       planos_trabalhos.tempo_total,
                                       planos_trabalhos.tempo_proporcional,
                                       planos_trabalhos_entregas.plano_trabalho_id,
                                       planos_entregas_entregas.plano_entrega_id,
                                       Pessoas.nome,
                                       Unidades.sigla,
                                       label('forma',tipos_modalidades.nome),
                                       avaliacoes_pt.c.qtd_aval)\
                                .filter(planos_entregas_entregas.plano_entrega_id == peId)\
                                .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                .join(planos_trabalhos_entregas, planos_trabalhos_entregas.plano_trabalho_id == planos_trabalhos.id)\
                                .join(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                                .join(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                .join(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                .outerjoin(avaliacoes_pt,avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id,)\
                                .order_by(Pessoas.nome)\
                                .all()    

    quantidade = len(planos_trab_pe)


    return render_template('consulta_pts.html', pe = pe, 
                                                quantidade = quantidade,
                                                planos_trab_pe = planos_trab_pe)                                                



# ver dados de um plano de entregas



