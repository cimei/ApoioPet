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

from sqlalchemy import func, or_, case, and_, text, distinct
from sqlalchemy.sql import label

from project import db

from project.core.forms import data_ref_Form

from project.models import planos_entregas, avaliacoes, planos_trabalhos, planos_trabalhos_consolidacoes,\
                           Pessoas, programas_participantes, Unidades, unidades_integrantes, unidades_integrantes_atribuicoes

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


@core.route('/numeros')
def numeros():
    """
    +---------------------------------------------------------------------------------------+
    |Números para uma visão geral do PGD.                                                   |
    +---------------------------------------------------------------------------------------+
    """

    hoje = dt.now()

    # Dados de Planos de Entregas

    qtd_pes =  db.session.query(label('pes_total',func.count(planos_entregas.id)),
                                label('pes_ativ',func.count(case((planos_entregas.status == 'ATIVO',planos_entregas.id)))),
                                label('pes_ativ_venc',func.count(case((and_(planos_entregas.status == 'ATIVO', planos_entregas.data_fim < hoje),planos_entregas.id)))),
                                label('pes_incl',func.count(case((planos_entregas.status == 'INCLUIDO',planos_entregas.id)))),
                                label('pes_incl_venc',func.count(case((and_(planos_entregas.status == 'INCLUIDO', planos_entregas.data_fim < hoje),planos_entregas.id)))),
                                label('pes_homo',func.count(case((planos_entregas.status == 'HOMOLOGANDO',planos_entregas.id)))),
                                label('pes_homo_venc',func.count(case((and_(planos_entregas.status == 'HOMOLOGANDO', planos_entregas.data_fim < hoje),planos_entregas.id)))),
                                label('pes_conc',func.count(case((planos_entregas.status == 'CONCLUIDO',planos_entregas.id)))),
                                label('pes_aval',func.count(case((planos_entregas.status == 'AVALIADO',planos_entregas.id)))),
                                label('pes_canc',func.count(case((planos_entregas.status == 'CANCELADO',planos_entregas.id)))),
                                label('pes_susp',func.count(case((planos_entregas.status == 'SUSPENSO',planos_entregas.id)))))\
                          .filter(planos_entregas.deleted_at == None)\
                          .all()

    avaliacoes_dados = db.session.query(label('dif_datas',func.datediff(avaliacoes.data_avaliacao,planos_entregas.data_fim)))\
                                 .outerjoin(planos_entregas, planos_entregas.id == avaliacoes.plano_entrega_id)\
                                 .filter(avaliacoes.plano_entrega_id != None)\
                                 .all()
  
    dados = [ a.dif_datas for a in avaliacoes_dados if a.dif_datas != None and a.dif_datas > 0 ]
    n = len(dados)
    media_a_pes = sum(dados) / n
    variancia_a_pes = sum([(x - media_a_pes) ** 2 for x in dados]) / n  # Para desvio padrão populacional
    desvio_padrao_a_pes = variancia_a_pes ** 0.5

    # Dados de Planos de Trabalho
    
    qtd_pts =  db.session.query(label('pts_total',func.count(planos_trabalhos.id)),
                                label('pts_ativ',func.count(case((planos_trabalhos.status == 'ATIVO',planos_trabalhos.id)))),
                                label('pts_ativ_venc',func.count(case((and_(planos_trabalhos.status == 'ATIVO', planos_trabalhos.data_fim < hoje),planos_trabalhos.id)))),
                                label('pts_incl',func.count(case((planos_trabalhos.status == 'INCLUIDO',planos_trabalhos.id)))),
                                label('pts_incl_venc',func.count(case((and_(planos_trabalhos.status == 'INCLUIDO', planos_trabalhos.data_fim < hoje),planos_trabalhos.id)))),
                                label('pts_agas',func.count(case((planos_trabalhos.status == 'AGUARDANDO_ASSINATURA',planos_trabalhos.id)))),
                                label('pts_agas_venc',func.count(case((and_(planos_trabalhos.status == 'AGUARDANDO_ASSINATURA', planos_trabalhos.data_fim < hoje),planos_trabalhos.id)))),
                                label('pts_conc',func.count(case((planos_trabalhos.status == 'CONCLUIDO',planos_trabalhos.id)))),
                                label('pts_aval',func.count(case((planos_trabalhos.status == 'AVALIADO',planos_trabalhos.id)))),
                                label('pts_canc',func.count(case((planos_trabalhos.status == 'CANCELADO',planos_trabalhos.id)))),
                                label('pts_susp',func.count(case((planos_trabalhos.status == 'SUSPENSO',planos_trabalhos.id)))))\
                          .filter(planos_trabalhos.deleted_at == None)\
                          .all()
    
    # Contando avaliaçaões em consolidaçoes de pts
    pts_conclu = db.session.query(planos_trabalhos.id)\
                           .filter(planos_trabalhos.status == 'CONCLUIDO')\
                           .subquery()
    avaliacoes_pt_consol = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                                     .join(pts_conclu, pts_conclu.c.id == planos_trabalhos_consolidacoes.plano_trabalho_id)\
                                     .filter(planos_trabalhos_consolidacoes.deleted_at == None)\
                                     .distinct().all()
    qtd_pts_aval = len(avaliacoes_pt_consol)

    # Calculado media das distâncias entre envios de registros e respectivas avaliações
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     label('dt_conclu',planos_trabalhos_consolidacoes.data_conclusao),
                                     label('dt_avaliacao',avaliacoes.data_avaliacao),
                                     label('dif_datas',func.datediff(avaliacoes.data_avaliacao, planos_trabalhos_consolidacoes.data_conclusao)))\
                              .join(avaliacoes, avaliacoes.plano_trabalho_consolidacao_id == planos_trabalhos_consolidacoes.id)\
                              .order_by(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .all()

    dados = [ a.dif_datas for a in avaliacoes_pt if a.dif_datas != None and a.dif_datas > 0 ]
    n = len(dados)
    media = sum(dados) / n
    variancia = sum([(x - media) ** 2 for x in dados]) / n  # Para desvio padrão populacional
    desvio_padrao = variancia ** 0.5  

    # Dados de Pessoas

    pessoas_subq = db.session.query(Pessoas.id,
                                     label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))),
                                     label('qtd_regramentos',func.count(distinct(programas_participantes.programa_id))))\
                                .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                .outerjoin(programas_participantes, programas_participantes.usuario_id == Pessoas.id)\
                                .filter(Pessoas.deleted_at == None)\
                                .group_by(Pessoas.id)\
                                .subquery()

    qtd_pessoas = db.session.query(label('pessoas_total',func.count(pessoas_subq.c.id)),
                                   label('com_pt',func.count(case((pessoas_subq.c.qtd_planos_trab != 0,pessoas_subq.c.id)))),
                                   label('com_regra',func.count(case((pessoas_subq.c.qtd_regramentos != 0,pessoas_subq.c.id)))))\
                            .all()
    

    # Dados de Unidades

    chefes_s = db.session.query(Pessoas.id,
                                unidades_integrantes.unidade_id,
                                unidades_integrantes_atribuicoes.atribuicao)\
                         .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                         .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                         .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                 unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                       .distinct().subquery()
    substitutos_s = db.session.query(Pessoas.id,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .distinct().subquery()
    
    unidades_s = db.session.query(label('id',Unidades.id),
                                  label('cont_tit', func.count(distinct(chefes_s.c.id))),
                                  label('cont_sub', func.count(distinct(substitutos_s.c.id))))\
                            .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                            .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                            .filter(Unidades.deleted_at == None)\
                            .group_by(Unidades.id)\
                            .distinct().subquery()
                                  

    unids = db.session.query(label('unids_total',func.count(distinct(unidades_s.c.id))),
                             label('sem_chefe',func.count(case((and_(unidades_s.c.cont_tit == 0, unidades_s.c.cont_sub == 0), unidades_s.c.id)))),
                             label('sem_titu',func.count(case((unidades_s.c.cont_tit == 0, unidades_s.c.id)))),
                             label('sem_subs',func.count(case((unidades_s.c.cont_sub == 0, unidades_s.c.id)))))\
                       .all()

    return render_template('numeros.html', qtd_pes = qtd_pes, mda = media_a_pes, des_pes = desvio_padrao_a_pes,
                                           qtd_pts = qtd_pts, 
                                           mda_pts = media, des_pts = desvio_padrao,
                                           qtd_pts_aval = qtd_pts_aval,
                                           qtd_pessoas = qtd_pessoas,
                                           unids = unids)

@core.route('/graficos')
def graficos():
    """
    +---------------------------------------------------------------------------------------+
    |Gráficos para uma visão geral do PGD.                                                  |
    +---------------------------------------------------------------------------------------+
    """

    hoje = dt.now()

    # dados de planos de entregas

    qtd_pes =  db.session.query(label('pes_total',func.count(planos_entregas.id)),
                                label('pes_ativ',func.count(case((planos_entregas.status == 'ATIVO',planos_entregas.id)))),
                                label('pes_ativ_venc',func.count(case((and_(planos_entregas.status == 'ATIVO', planos_entregas.data_fim < hoje),planos_entregas.id)))),
                                label('pes_incl',func.count(case((planos_entregas.status == 'INCLUIDO',planos_entregas.id)))),
                                label('pes_incl_venc',func.count(case((and_(planos_entregas.status == 'INCLUIDO', planos_entregas.data_fim < hoje),planos_entregas.id)))),
                                label('pes_homo',func.count(case((planos_entregas.status == 'HOMOLOGANDO',planos_entregas.id)))),
                                label('pes_homo_venc',func.count(case((and_(planos_entregas.status == 'HOMOLOGANDO', planos_entregas.data_fim < hoje),planos_entregas.id)))),
                                label('pes_conc',func.count(case((planos_entregas.status == 'CONCLUIDO',planos_entregas.id)))),
                                label('pes_aval',func.count(case((planos_entregas.status == 'AVALIADO',planos_entregas.id)))),
                                label('pes_canc',func.count(case((planos_entregas.status == 'CANCELADO',planos_entregas.id)))),
                                label('pes_susp',func.count(case((planos_entregas.status == 'SUSPENSO',planos_entregas.id)))))\
                          .filter(planos_entregas.deleted_at == None)\
                          .all()

    rotulos_pes = ['Ativos', 'Incluídos', 'Homologando', 'Concluídos', 'Avaliados', 'Cancelados', 'Suspensos']
    valores_pes = [qtd_pes[0].pes_ativ, qtd_pes[0].pes_incl, qtd_pes[0].pes_homo, qtd_pes[0].pes_conc, qtd_pes[0].pes_aval, qtd_pes[0].pes_canc, qtd_pes[0].pes_susp]
    valores_pes_2 = [qtd_pes[0].pes_ativ_venc, qtd_pes[0].pes_incl_venc, qtd_pes[0].pes_homo_venc, 0, 0, 0, 0]

    # dados de planos de trabalho

    qtd_pts =  db.session.query(label('pts_total',func.count(planos_trabalhos.id)),
                                label('pts_ativ',func.count(case((planos_trabalhos.status == 'ATIVO',planos_trabalhos.id)))),
                                label('pts_ativ_venc',func.count(case((and_(planos_trabalhos.status == 'ATIVO', planos_trabalhos.data_fim < hoje),planos_trabalhos.id)))),
                                label('pts_incl',func.count(case((planos_trabalhos.status == 'INCLUIDO',planos_trabalhos.id)))),
                                label('pts_incl_venc',func.count(case((and_(planos_trabalhos.status == 'INCLUIDO', planos_trabalhos.data_fim < hoje),planos_trabalhos.id)))),
                                label('pts_agas',func.count(case((planos_trabalhos.status == 'AGUARDANDO_ASSINATURA',planos_trabalhos.id)))),
                                label('pts_agas_venc',func.count(case((and_(planos_trabalhos.status == 'AGUARDANDO_ASSINATURA', planos_trabalhos.data_fim < hoje),planos_trabalhos.id)))),
                                label('pts_conc',func.count(case((planos_trabalhos.status == 'CONCLUIDO',planos_trabalhos.id)))),
                                label('pts_aval',func.count(case((planos_trabalhos.status == 'AVALIADO',planos_trabalhos.id)))),
                                label('pts_canc',func.count(case((planos_trabalhos.status == 'CANCELADO',planos_trabalhos.id)))),
                                label('pts_susp',func.count(case((planos_trabalhos.status == 'SUSPENSO',planos_trabalhos.id)))))\
                          .filter(planos_trabalhos.deleted_at == None)\
                          .all()
    
    # Contando avaliaçaões em consolidaçoes de pts
    pts_conclu = db.session.query(planos_trabalhos.id)\
                           .filter(planos_trabalhos.status == 'CONCLUIDO')\
                           .subquery()
    avaliacoes_pt_consol = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                                     .join(pts_conclu, pts_conclu.c.id == planos_trabalhos_consolidacoes.plano_trabalho_id)\
                                     .filter(planos_trabalhos_consolidacoes.deleted_at == None)\
                                     .distinct().all()
    qtd_pts_aval = len(avaliacoes_pt_consol)

    rotulos_pts = ['Ativos', 'Incluídos', 'Aguardando Assinatura', 'Concluídos', 'Cancelados', 'Suspensos']
    valores_pts = [qtd_pts[0].pts_ativ, qtd_pts[0].pts_incl, qtd_pts[0].pts_agas, qtd_pts[0].pts_conc, qtd_pts[0].pts_canc, qtd_pts[0].pts_susp]
    valores_pts_2 = [qtd_pts[0].pts_ativ_venc, qtd_pts[0].pts_incl_venc, qtd_pts[0].pts_agas_venc, qtd_pts[0].pts_conc - qtd_pts_aval, 0, 0]

    # Dados de Unidades

    chefes_s = db.session.query(Pessoas.id,
                                unidades_integrantes.unidade_id,
                                unidades_integrantes_atribuicoes.atribuicao)\
                         .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                         .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                         .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                 unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                       .distinct().subquery()
    substitutos_s = db.session.query(Pessoas.id,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .distinct().subquery()
    
    unidades_s = db.session.query(label('id',Unidades.id),
                                  label('cont_tit', func.count(distinct(chefes_s.c.id))),
                                  label('cont_sub', func.count(distinct(substitutos_s.c.id))))\
                            .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                            .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                            .filter(Unidades.deleted_at == None)\
                            .group_by(Unidades.id)\
                            .distinct().subquery()
                                  

    unids = db.session.query(label('unids_total',func.count(distinct(unidades_s.c.id))),
                             label('sem_chefe',func.count(case((and_(unidades_s.c.cont_tit == 0, unidades_s.c.cont_sub == 0), unidades_s.c.id)))),
                             label('sem_titu',func.count(case((unidades_s.c.cont_tit == 0, unidades_s.c.id)))),
                             label('sem_subs',func.count(case((unidades_s.c.cont_sub == 0, unidades_s.c.id)))))\
                       .all()
    
    rotulos_unids = ['Com alguma chefia', 'Sem Titular e Substituto']
    valores_unids = [unids[0].unids_total - unids[0].sem_chefe, unids[0].sem_chefe]

    # Dados de Pessoas

    pessoas_subq = db.session.query(Pessoas.id,
                                     label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))),
                                     label('qtd_regramentos',func.count(distinct(programas_participantes.programa_id))))\
                                .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                .outerjoin(programas_participantes, programas_participantes.usuario_id == Pessoas.id)\
                                .filter(Pessoas.deleted_at == None)\
                                .group_by(Pessoas.id)\
                                .subquery()

    qtd_pessoas = db.session.query(label('pessoas_total',func.count(pessoas_subq.c.id)),
                                   label('com_pt',func.count(case((pessoas_subq.c.qtd_planos_trab != 0,pessoas_subq.c.id)))),
                                   label('com_regra',func.count(case((pessoas_subq.c.qtd_regramentos != 0,pessoas_subq.c.id)))))\
                            .all()

    rotulos_pessoas = ['Sem', 'Com']
    valores_pessoas = [qtd_pessoas[0].pessoas_total - qtd_pessoas[0].com_regra, qtd_pessoas[0].com_regra]
    valores_pessoas2 = [qtd_pessoas[0].pessoas_total - qtd_pessoas[0].com_pt, qtd_pessoas[0].com_pt]


    return render_template('graficos.html', qtd_pes = qtd_pes[0][0],
                                            rotulos_pes = rotulos_pes, valores_pes = valores_pes, valores_pes_2 = valores_pes_2,
                                            qtd_pts = qtd_pts[0][0],
                                            rotulos_pts = rotulos_pts, valores_pts = valores_pts, valores_pts_2 = valores_pts_2,
                                            qtd_pts_aval = qtd_pts_aval,
                                            unids = unids,
                                            rotulos_unids = rotulos_unids, valores_unids = valores_unids,
                                            qtd_pessoas = qtd_pessoas,
                                            rotulos_pessoas = rotulos_pessoas, valores_pessoas = valores_pessoas, valores_pessoas2 = valores_pessoas2)


@core.route('/dados')
def dados():
    """
    +---------------------------------------------------------------------------------------+
    |Abre menu de dados agregados.                                                          |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('dados.html')

@core.route('/v_a')
def v_a():
    """
    +---------------------------------------------------------------------------------------+
    |Lista variáveis de ambiente.                                                           |
    +---------------------------------------------------------------------------------------+
    """

    return render_template('v_a.html')



