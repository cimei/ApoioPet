"""
.. topic:: Unidades (views)

    As Unidades na estrutura da instituição.

.. topic:: Ações relacionadas às Unidades

    * lista_unidades: Lista Unidades
    * lista_unidades_filtro: Lista Unidades conforme filtro aplicado

"""

# views.py na pasta unidades

from flask import render_template, request, Blueprint, send_from_directory, redirect, url_for
from flask_login import current_user, login_required

import os, csv

from sqlalchemy import func, distinct
from sqlalchemy.sql import label
from project import db
from project.models import Unidades, Pessoas, unidades_integrantes, unidades_integrantes_atribuicoes, cidades
from project.unidades.forms import PesquisaUnidForm, CSV_Form

# from sqlalchemy.dialects import mysql

unidades = Blueprint('unidades',__name__, template_folder='templates')


## lista unidades da instituição

@unidades.route('/lista_unidades',methods=['GET','POST'])

def lista_unidades():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das unidades da instituição.                                       |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 
    
    lista = '%'
    # Preparação para leitura de unidades

    qtd_unids = db.session.query(Unidades).count()

    page = request.args.get('page', 1, type=int)

    # subqueries para ver quantos gestores cada unidade tem
    
    chefes_s = db.session.query(Pessoas.id,
                              Pessoas.nome,
                              unidades_integrantes.unidade_id,
                              unidades_integrantes_atribuicoes.atribuicao)\
                       .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                       .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                       .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                               unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                       .distinct().subquery()
    substitutos_s = db.session.query(Pessoas.id,
                                   Pessoas.nome,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .distinct().subquery()
    delegados_s = db.session.query(Pessoas.id,
                                   Pessoas.nome,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                            .distinct().subquery()
                          
    # consultas que repetem as subqueries para poder listar os nomes em um modal
    
    chefes = db.session.query(Pessoas.id,
                              Pessoas.nome,
                              unidades_integrantes.unidade_id,
                              unidades_integrantes_atribuicoes.atribuicao)\
                       .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                       .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                       .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                               unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                       .distinct().all()
    substitutos = db.session.query(Pessoas.id,
                                   Pessoas.nome,
                                   unidades_integrantes.unidade_id,
                                   unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .distinct().all()
    delegados = db.session.query(Pessoas.id,
                                 Pessoas.nome,
                                 unidades_integrantes.unidade_id,
                                 unidades_integrantes_atribuicoes.atribuicao)\
                          .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                          .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                          .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                  unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                          .distinct().all()                      
    
    # sobre paginação    
    pag = 500

    unids = db.session.query(Unidades.id,
                             Unidades.sigla,
                             Unidades.nome,
                             Unidades.unidade_pai_id,
                             cidades.uf,
                             Unidades.path,
                             Unidades.codigo,
                             label('titular',func.count(distinct(chefes_s.c.nome))),
                             label('substituto',func.count(distinct(substitutos_s.c.nome))),
                             label('delegado',func.count(distinct(delegados_s.c.nome))),
                             Unidades.data_inativacao)\
                        .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                        .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                        .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                        .outerjoin(delegados_s, delegados_s.c.unidade_id == Unidades.id)\
                        .filter(Unidades.deleted_at == None)\
                        .order_by(Unidades.sigla)\
                        .group_by(Unidades.id)\
                        .paginate(page=page,per_page=pag)

    quantidade = unids.total 
    
    caminho = db.session.query(Unidades.path,Unidades.sigla,Unidades.id).all()
    caminho_dict = {}
    for c in caminho:
        if c.path != None and c.path != '':
            p = c.path.split('/')
            arvore = ''
            for i in p:
                if len(i) > 0:
                    sigla_arvore = db.session.query(Unidades.sigla).filter(Unidades.id == i).first()
                    if sigla_arvore != None:
                        arvore += sigla_arvore.sigla+'/'
            arvore += c.sigla
            caminho_dict[c.id] = arvore 
        else:
            caminho_dict[c.id] = c.sigla              
 

    form = CSV_Form()

    if form.validate_on_submit():

        unids_csv = db.session.query(Unidades.id,
                                     Unidades.sigla,
                                     Unidades.nome,
                                     Unidades.unidade_pai_id,
                                     cidades.uf,
                                     Unidades.path,
                                     Unidades.codigo,
                                     label('titular',func.count(distinct(chefes_s.c.nome))),
                                     label('substituto',func.count(distinct(substitutos_s.c.nome))),
                                     label('delegado',func.count(distinct(delegados_s.c.nome))),
                                     Unidades.data_inativacao)\
                        .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                        .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                        .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                        .outerjoin(delegados_s, delegados_s.c.unidade_id == Unidades.id)\
                        .filter(Unidades.deleted_at == None)\
                        .order_by(Unidades.sigla)\
                        .group_by(Unidades.id)\
                        .all()

        # compiled_query = unids_csv.statement.compile(dialect=mysql.dialect()) 
        # print(str(compiled_query))
        # print("Parameters:", compiled_query.params)

        csv_caminho_arquivo = os.path.normpath('/app/project/static/unidades.csv')
        
        dados_a_escrever = [[caminho_dict[u.id], u.nome, u.sigla, u.uf, u.codigo, u.titular, u.substituto, u.delegado, u.data_inativacao] for u in unids_csv]

        header = ['Hierarquia', 'Nome','Sigla','UF', 'Código', 'Titular', 'Substituto', 'Delegado', 'Data de Inativação']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', 'unidades.csv')

        return redirect(url_for('static', filename = 'unidades.csv'))

    
    return render_template('lista_unidades.html', unids = unids, quantidade = quantidade, chefes = chefes,
                                                  substitutos = substitutos, delegados = delegados,
                                                  caminho_dict = caminho_dict, lista = lista, qtd_unids=qtd_unids,
                                                  form = form)

    

## lista unidades da instituição mediante filtro

@unidades.route('<lista>/lista_unidades_filtro', methods=['GET','POST'])

def lista_unidades_filtro(lista):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das unidades da instituição de acordo com filtro aplicado.         |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 

    page = request.args.get('page', 1, type=int)

    form = PesquisaUnidForm()
    
    unids = db.session.query(Unidades.sigla)\
                      .filter(Unidades.deleted_at == None)\
                      .order_by(Unidades.sigla).all()
    lista_unids = [(u.sigla,u.sigla) for u in unids]
    lista_unids.insert(0,('','Todas'))  
    
    unids_pai = db.session.query(Unidades.id,
                                 Unidades.sigla)\
                          .filter(Unidades.deleted_at == None)\
                          .order_by(Unidades.sigla).all()
    lista_pais = [(u.id,u.sigla) for u in unids_pai]
    lista_pais.insert(0,('','Todas'))                                


    form.sigla.choices = lista_unids
    form.pai.choices   = lista_pais


    if form.validate_on_submit():

        if form.sigla.data == '':
            p_sigla_pattern = '%'
        else:
            p_sigla_pattern = '%'+form.sigla.data+'%'
            
        if form.pai.data == '':
            p_pai_pattern = '%'
        else:
            p_pai_pattern = '%'+form.pai.data+'%'

        # pega valores utilizados como filtro para exibição na tela da lista
        p_sigla = dict(form.sigla.choices).get(form.sigla.data)
        p_pai   = dict(form.pai.choices).get(form.pai.data)
    
        # Lê tabela unidades

        chefes_s = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                        .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                        .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                        .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                        .distinct().subquery()
        substitutos_s = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                                .distinct().subquery()
        delegados_s = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                                .distinct().subquery()
                            
        # consultas que repetem as subqueries para poder listar os nomes em um modal
        
        chefes = db.session.query(Pessoas.id,
                                  Pessoas.nome,
                                  unidades_integrantes.unidade_id,
                                  unidades_integrantes_atribuicoes.atribuicao)\
                        .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                        .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                        .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                        .distinct().all()
        substitutos = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                                .distinct().all()
        delegados = db.session.query(Pessoas.id,
                                    Pessoas.nome,
                                    unidades_integrantes.unidade_id,
                                    unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                            .distinct().all()

        unids = db.session.query(Unidades.id,
                                 Unidades.sigla,
                                 Unidades.nome,
                                 Unidades.unidade_pai_id,
                                 cidades.uf,
                                 Unidades.path,
                                 Unidades.codigo,
                                 label('titular',func.count(distinct(chefes_s.c.nome))),
                                 label('substituto',func.count(distinct(substitutos_s.c.nome))),
                                 label('delegado',func.count(distinct(delegados_s.c.nome))),
                                 Unidades.data_inativacao)\
                           .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                           .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                           .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                           .outerjoin(delegados_s, delegados_s.c.unidade_id == Unidades.id)\
                           .filter(Unidades.sigla.like(p_sigla_pattern),
                                   Unidades.unidade_pai_id.like(p_pai_pattern),
                                   Unidades.nome.like('%'+form.nome.data+'%'),
                                   cidades.uf.like('%'+form.uf.data+'%'))\
                           .order_by(Unidades.sigla)\
                           .group_by(Unidades.id)\
                           .paginate(page=page,per_page=500)

        quantidade = unids.total
        
        caminho = db.session.query(Unidades.path,Unidades.sigla,Unidades.id).all()
        caminho_dict = {}
        for c in caminho:
            if c.path != None and c.path != '':
                p = c.path.split('/')
                arvore = ''
                for i in p:
                    if len(i) > 0:
                        sigla_arvore = db.session.query(Unidades.sigla).filter(Unidades.id == i).first()
                        if sigla_arvore != None:
                             arvore += sigla_arvore.sigla+'/'
                arvore += c.sigla
                caminho_dict[c.id] = arvore 
            else:
                caminho_dict[c.id] = c.sigla

        filtro = [p_sigla_pattern, p_pai_pattern, form.nome.data, form.uf.data]

        return render_template('lista_unidades.html', unids = unids, quantidade = quantidade,
                                                      lista = lista,
                                                      p_sigla = p_sigla,
                                                      p_pai = p_pai,
                                                      p_nome = form.nome.data,
                                                      p_uf = form.uf.data,
                                                      chefes = chefes,
                                                      substitutos = substitutos, delegados = delegados,
                                                      caminho_dict = caminho_dict,
                                                      form = form,
                                                      filtro = filtro)

    return render_template('pesquisa_unidades.html', form = form)

## gera csv com unidades da instituição mediante filtro

@unidades.route('/<filtro>/csv_lista_unidades_filtro', methods=['GET','POST'])

def csv_lista_unidades_filtro(filtro):
    """
    +---------------------------------------------------------------------------------------+
    |Gera csv com lista das unidades da instituição de acordo com filtro aplicado.          |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 

    filtro = filtro.split(',')
    
    chefes_s = db.session.query(Pessoas.id,
                                Pessoas.nome,
                                unidades_integrantes.unidade_id,
                                unidades_integrantes_atribuicoes.atribuicao)\
                    .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                    .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                    .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                            unidades_integrantes_atribuicoes.atribuicao == 'GESTOR')\
                    .distinct().subquery()
    substitutos_s = db.session.query(Pessoas.id,
                                Pessoas.nome,
                                unidades_integrantes.unidade_id,
                                unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_SUBSTITUTO')\
                            .distinct().subquery()
    delegados_s = db.session.query(Pessoas.id,
                                Pessoas.nome,
                                unidades_integrantes.unidade_id,
                                unidades_integrantes_atribuicoes.atribuicao)\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes_atribuicoes.deleted_at == None,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR_DELEGADO')\
                            .distinct().subquery()

    unids_csv = db.session.query(Unidades.id,
                                Unidades.sigla,
                                Unidades.nome,
                                Unidades.unidade_pai_id,
                                cidades.uf,
                                Unidades.path,
                                Unidades.codigo,
                                label('titular',func.count(distinct(chefes_s.c.nome))),
                                label('substituto',func.count(distinct(substitutos_s.c.nome))),
                                label('delegado',func.count(distinct(delegados_s.c.nome))),
                                Unidades.data_inativacao)\
                        .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                        .outerjoin(chefes_s, chefes_s.c.unidade_id == Unidades.id)\
                        .outerjoin(substitutos_s, substitutos_s.c.unidade_id == Unidades.id)\
                        .outerjoin(delegados_s, delegados_s.c.unidade_id == Unidades.id)\
                        .filter(Unidades.sigla.like(filtro[0][1:].split("'")[1]),
                                Unidades.unidade_pai_id.like(filtro[1].split("'")[1]),
                                Unidades.nome.like('%'+filtro[2].split("'")[1]+'%'),
                                cidades.uf.like('%'+filtro[3][:-1].split("'")[1]+'%'))\
                        .order_by(Unidades.sigla)\
                        .group_by(Unidades.id)\
                        .all()
    
    caminho = db.session.query(Unidades.path,Unidades.sigla,Unidades.id).all()
    caminho_dict = {}
    for c in caminho:
        if c.path != None and c.path != '':
            p = c.path.split('/')
            arvore = ''
            for i in p:
                if len(i) > 0:
                    sigla_arvore = db.session.query(Unidades.sigla).filter(Unidades.id == i).first()
                    if sigla_arvore != None:
                            arvore += sigla_arvore.sigla+'/'
            arvore += c.sigla
            caminho_dict[c.id] = arvore 
        else:
            caminho_dict[c.id] = c.sigla


    csv_caminho_arquivo = os.path.normpath('/app/project/static/unidades_filtro.csv')
        
    dados_a_escrever = [[caminho_dict[u.id], u.nome, u.sigla, u.uf, u.codigo, u.titular, u.substituto, u.delegado, u.data_inativacao] for u in unids_csv]

    header = ['Hierarquia', 'Nome','Sigla','UF', 'Código', 'Titular', 'Substituto', 'Delegado', 'Data de Inativação']

    with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header) 
        csv_writer.writerows(dados_a_escrever)

    # o comandinho mágico que permite fazer o download de um arquivo
    send_from_directory('/app/project/static', 'unidades_filtro.csv')

    return redirect(url_for('static', filename = 'unidades_filtro.csv'))

#

