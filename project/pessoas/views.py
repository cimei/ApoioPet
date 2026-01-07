"""
.. topic:: Pessoas (views)

    As Pessoas são os servidores lotados na intituição.
    
.. topic:: Ações relacionadas à gestão de pessoas

    * lista_pessoas: Lista das pessoas da instituição
    * lista_pessoas_filtro: Procura pessoas na instituição 

"""

# views.py na pasta pessoas

import os, csv

from flask import render_template, Blueprint, request, redirect, send_from_directory, url_for
from flask_login import current_user, login_required

from sqlalchemy.sql import label
from sqlalchemy import func, distinct

from project import db
from project.models import Unidades, unidades_integrantes, Pessoas, perfis, unidades_integrantes_atribuicoes, planos_trabalhos,\
                           planos_trabalhos_entregas, planos_entregas_entregas, tipos_modalidades, planos_trabalhos_consolidacoes,\
                           avaliacoes, programas_participantes, programas, tipos_modalidades_siape
                            
from project.pessoas.forms import PesquisaForm, CSV_Form


pessoas = Blueprint('pessoas',__name__, template_folder='templates')


 ## lista pessoas da instituição

@pessoas.route('/lista_pessoas',methods=['GET','POST'])
@login_required

def lista_pessoas():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das pessoas da instituição.                                        |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    page = request.args.get('page', 1, type=int)    

    tipo = "inst"
    
    # Verifica a quantidade de pessoas para decidir sobre paginação
    
    qtd_pessoas = db.session.query(Pessoas).count()
        
    if qtd_pessoas < 500:
        pag = 500
    else:
        pag = 100
    
    atribuicoes_pessoas = db.session.query(Pessoas.id,
                                           Unidades.sigla,
                                           unidades_integrantes_atribuicoes.atribuicao)\
                                    .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                    .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                    .join(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                    .filter(Pessoas.deleted_at == None)\
                                    .order_by(Pessoas.id)\
                                    .distinct().all()

    
    # Lê tabela pessoas

    pessoas_lista = db.session.query(Pessoas.id,
                                     Pessoas.nome,
                                     Pessoas.cpf,
                                     Pessoas.data_nascimento,
                                     Pessoas.matricula,
                                     Pessoas.email,
                                     label('qtd_unidades',func.count(distinct(Unidades.sigla))),
                                     label('atribuicoes',func.count(distinct(unidades_integrantes_atribuicoes.atribuicao))),
                                     Pessoas.situacao_funcional,
                                     label('perfil',perfis.nome),
                                     label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))),
                                     label('qtd_regramentos',func.count(distinct(programas_participantes.programa_id))),
                                     Pessoas.participa_pgd,
                                     label('modalidade_pgd',tipos_modalidades_siape.nome))\
                                .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .outerjoin(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                .join(perfis, perfis.id == Pessoas.perfil_id)\
                                .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                .outerjoin(programas_participantes, programas_participantes.usuario_id == Pessoas.id)\
                                .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == Pessoas.tipo_modalidade_id)\
                                .filter(Pessoas.deleted_at == None)\
                                .order_by(Pessoas.nome)\
                                .group_by(Pessoas.id)\
                                .paginate(page=page,per_page=pag)

    quantidade = pessoas_lista.total

    form = CSV_Form()

    if form.validate_on_submit():
        
        csv_caminho_arquivo = os.path.normpath('/app/project/static/pessoas.csv')

        pessoas_csv = db.session.query(Pessoas.id,
                                     Pessoas.nome,
                                     Pessoas.cpf,
                                     Pessoas.data_nascimento,
                                     Pessoas.matricula,
                                     Pessoas.email,
                                     label('qtd_unidades',func.count(distinct(Unidades.sigla))),
                                     label('atribuicoes',func.count(distinct(unidades_integrantes_atribuicoes.atribuicao))),
                                     Pessoas.situacao_funcional,
                                     label('perfil',perfis.nome),
                                     label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))),
                                     label('qtd_regramentos',func.count(distinct(programas_participantes.programa_id))),
                                     Pessoas.participa_pgd,
                                     label('modalidade_pgd',tipos_modalidades_siape.nome))\
                                .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .outerjoin(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                .join(perfis, perfis.id == Pessoas.perfil_id)\
                                .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                .outerjoin(programas_participantes, programas_participantes.usuario_id == Pessoas.id)\
                                .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == Pessoas.tipo_modalidade_id)\
                                .filter(Pessoas.deleted_at == None)\
                                .order_by(Pessoas.nome)\
                                .group_by(Pessoas.id)\
                                .all()

        dados_a_escrever = []
        for p in pessoas_csv:
            atribs = ''
            for a in atribuicoes_pessoas:
                if a.id == p.id:
                    if a.atribuicao != None:
                        atr = a.atribuicao
                    else:
                        atr = 'N.I.'    
                    atribs += (a.sigla + '(' + atr + ')' + ';')
            atribs = atribs[:-1]        
            dados_a_escrever.append([p.nome, p.data_nascimento, p.matricula, p.email, atribs, p.situacao_funcional, p.perfil, p.qtd_planos_trab, p.qtd_regramentos, p.participa_pgd, p.modalidade_pgd])
        
        # dados_a_escrever = [[p.nome, p.data_nascimento, p.matricula, p.email, p.sigla, p.atribuicao, p.situacao_funcional, p.perfil, p.qtd_planos_trab, p.qtd_regramentos] for p in pessoas_csv]

        header = ['Nome', 'Data Nascimento','Matrícula','E-mail', 'Unidades (atribuições)', 'Situação', 'Perfil', 'PTs', 'Regramentos', 'Participa PGD', 'Modalidade PGD']

        with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header) 
            csv_writer.writerows(dados_a_escrever)

        # o comandinho mágico que permite fazer o download de um arquivo
        send_from_directory('/app/project/static', 'pessoas.csv')

        return redirect(url_for('static', filename = 'pessoas.csv'))


    return render_template('lista_pessoas_gestor.html', pessoas = pessoas_lista,
                                                        quantidade = quantidade,
                                                        qtd_pessoas = qtd_pessoas,
                                                        tipo = tipo,
                                                        form = form,
                                                        atribuicoes_pessoas = atribuicoes_pessoas)
    
    
## lista pessoas da instituição conforme filtro aplicado

@pessoas.route('/lista_pessoas_filtro', methods=['GET','POST'])
@login_required

def lista_pessoas_filtro():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista das pessoas da instituição via filtro                              |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    tipo = "pesq"

    atribuicoes_pessoas = db.session.query(Pessoas.id,
                                           Unidades.sigla,
                                           unidades_integrantes_atribuicoes.atribuicao)\
                                    .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                    .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                    .join(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                    .filter(Pessoas.deleted_at == None)\
                                    .order_by(Pessoas.id)\
                                    .distinct().all()
    

    form = PesquisaForm() 
    
    unids = db.session.query(Unidades.id,Unidades.sigla)\
                      .filter(Unidades.deleted_at == None)\
                      .order_by(Unidades.sigla).all()
    lista_unids = [(u.id,u.sigla) for u in unids]
    lista_unids.insert(0,('','Todas'))         

    perf = db.session.query(perfis.id, perfis.nome).order_by(perfis.nome).all()
    lista_perf = [(p.id,p.nome) for p in perf]
    lista_perf.insert(0,('','Todos'))
    
    situ = db.session.query(label('situ',Pessoas.situacao_funcional.distinct()))\
                     .order_by(Pessoas.situacao_funcional).all()
    lista_situ = [(s.situ,s.situ) for s in situ]
    lista_situ.insert(0,('','Todas'))

    atrib = db.session.query(label('atrib',unidades_integrantes_atribuicoes.atribuicao.distinct()))\
                      .order_by(unidades_integrantes_atribuicoes.atribuicao).all()
    lista_atrib = [(a.atrib,a.atrib) for a in atrib]
    lista_atrib.insert(0,('','Todas'))

    form.perf.choices    = lista_perf
    form.situ.choices    = lista_situ
    form.atrib.choices   = lista_atrib
    form.unidade.choices = lista_unids

    if form.submit.data and form.validate_on_submit():

        nome_pesq = form.nome.data
        
        if form.situ.data == '':
            p_situ_pattern = '%'
        else:
            p_situ_pattern = '%'+form.situ.data+'%'

        if form.perf.data == '':
            p_perf_pattern = '%'
        else:
            p_perf_pattern = '%'+form.perf.data+'%'
            
        if form.atrib.data == '':
            p_atrib_pattern = '%'
        else:
            p_atrib_pattern = form.atrib.data
            
        if form.unidade.data == '':
            p_unid_pattern = '%'
        else:
            p_unid_pattern = '%'+form.unidade.data+'%'       

        # pega valores utilizados como filtro para exibição na tela da lista
        p_situ  = dict(form.situ.choices).get(form.situ.data)
        p_unid  = dict(form.unidade.choices).get(form.unidade.data) 
        p_perf  = dict(form.perf.choices).get(form.perf.data) 
        p_atrib = dict(form.atrib.choices).get(form.atrib.data) 

        pessoas_lista = db.session.query(Pessoas.id,
                                         Pessoas.nome,
                                         Pessoas.cpf,
                                         Pessoas.data_nascimento,
                                         Pessoas.matricula,
                                         Pessoas.email,
                                         label('qtd_unidades',func.count(distinct(Unidades.sigla))),
                                         label('atribuicoes',func.count(distinct(unidades_integrantes_atribuicoes.atribuicao))),
                                         Pessoas.situacao_funcional,
                                         label('perfil',perfis.nome),
                                         label('perfil_id',perfis.id),
                                         label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))),
                                         label('qtd_regramentos',func.count(distinct(programas_participantes.programa_id))),
                                         Pessoas.participa_pgd,
                                         label('modalidade_pgd',tipos_modalidades_siape.nome))\
                                  .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                  .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                  .outerjoin(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                  .join(perfis, perfis.id == Pessoas.perfil_id)\
                                  .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                  .outerjoin(programas_participantes, programas_participantes.usuario_id == Pessoas.id)\
                                  .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == Pessoas.tipo_modalidade_id)\
                                  .filter(Pessoas.deleted_at == None,
                                          Pessoas.nome.like('%'+nome_pesq+'%'),
                                          Unidades.id.like(p_unid_pattern),
                                          Pessoas.situacao_funcional.like(p_situ_pattern),
                                          perfis.id.like(p_perf_pattern),
                                          unidades_integrantes_atribuicoes.atribuicao.like(p_atrib_pattern))\
                                  .order_by(Pessoas.nome)\
                                  .group_by(Pessoas.id)\
                                  .all()
    
        quantidade = len(pessoas_lista)

        filtro = [nome_pesq, p_unid_pattern, p_situ_pattern, p_perf_pattern, p_atrib_pattern]

        return render_template('lista_pessoas_filtro.html', pessoas = pessoas_lista, quantidade=quantidade,
                                                        tipo = tipo,
                                                        p_atrib = p_atrib, p_perf = p_perf,
                                                        p_situ = p_situ, p_unid = p_unid, p_nome = nome_pesq,
                                                        filtro = filtro,
                                                        atribuicoes_pessoas = atribuicoes_pessoas)


    return render_template('pesquisa_pessoas.html', form = form)
    

## cria csv do resultado de um filtro
## feito separado por conta da dificuldade de ter as duas ações (gerar lista e criar csv) em uma só view

@pessoas.route('/<filtro>/csv_pessoas_filtro')
@login_required

def csv_pessoas_filtro(filtro):
    """
    +---------------------------------------------------------------------------------------+
    |Cria o csv do resultado de um filtro aplicado na lista de pessoas.                     |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """

    filtro = filtro.split(',')

    atribuicoes_pessoas = db.session.query(Pessoas.id,
                                           Unidades.sigla,
                                           unidades_integrantes_atribuicoes.atribuicao)\
                                    .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                    .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                    .join(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                    .filter(Pessoas.deleted_at == None)\
                                    .order_by(Pessoas.id)\
                                    .distinct().all()
    

    pessoas_csv_filtro = db.session.query(Pessoas.id,
                                         Pessoas.nome,
                                         Pessoas.cpf,
                                         Pessoas.data_nascimento,
                                         Pessoas.matricula,
                                         Pessoas.email,
                                         label('qtd_unidades',func.count(distinct(Unidades.sigla))),
                                         label('atribuicoes',func.count(distinct(unidades_integrantes_atribuicoes.atribuicao))),
                                         Pessoas.situacao_funcional,
                                         label('perfil',perfis.nome),
                                         label('perfil_id',perfis.id),
                                         label('qtd_planos_trab',func.count(distinct(planos_trabalhos.id))),
                                         label('qtd_regramentos',func.count(distinct(programas_participantes.programa_id))),
                                         Pessoas.participa_pgd,
                                         label('modalidade_pgd',tipos_modalidades_siape.nome))\
                                  .outerjoin(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                  .outerjoin(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                  .outerjoin(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                  .join(perfis, perfis.id == Pessoas.perfil_id)\
                                  .outerjoin(planos_trabalhos, planos_trabalhos.usuario_id == Pessoas.id)\
                                  .outerjoin(programas_participantes, programas_participantes.usuario_id == Pessoas.id)\
                                  .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == Pessoas.tipo_modalidade_id)\
                                  .filter(Pessoas.deleted_at == None,
                                          Pessoas.nome.like('%'+filtro[0][1:].split("'")[1]+'%'),
                                          Unidades.id.like(filtro[1].split("'")[1]),
                                          Pessoas.situacao_funcional.like(filtro[2].split("'")[1]),
                                          perfis.id.like(filtro[3].split("'")[1]),
                                          unidades_integrantes_atribuicoes.atribuicao.like(filtro[4][:-1].split("'")[1]))\
                                  .order_by(Pessoas.nome)\
                                  .group_by(Pessoas.id)\
                                  .all()

    csv_caminho_arquivo = os.path.normpath('/app/project/static/pessoas_filtro.csv')    

    dados_a_escrever = []
    for p in pessoas_csv_filtro:
        atribs = ''
        for a in atribuicoes_pessoas:
            if a.id == p.id:
                if a.atribuicao != None:
                    atr = a.atribuicao
                else:
                    atr = 'N.I.'    
                atribs += (a.sigla + '(' + atr + ')' + ';')
        atribs = atribs[:-1]    
        dados_a_escrever.append([p.nome, p.data_nascimento, p.matricula, p.email, atribs, p.situacao_funcional, p.perfil, p.qtd_planos_trab, p.qtd_regramentos, p.participa_pgd, p.modalidade_pgd])
    
    header = ['Nome', 'Data Nascimento','Matrícula','E-mail', 'Unidades (atribuições)', 'Situação', 'Perfil', 'PTs', 'Regramentos', 'Participa PGD', 'Modalidade PGD']

    with open(csv_caminho_arquivo, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header) 
        csv_writer.writerows(dados_a_escrever)

    # o comandinho mágico que permite fazer o download de um arquivo
    send_from_directory('/app/project/static', 'pessoas_filtro.csv')

    return redirect(url_for('static', filename = 'pessoas_filtro.csv'))
                                                 
     
## lista planos de trabalho vinculados a uma pessoa

@pessoas.route('/<pessoa_id>/consulta_pts_pessoa')
@login_required
def consulta_pts_pessoa(pessoa_id):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista de planos de trabalho vinculados a uma pessoa.                     |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   
                         
    dados_pessoa = db.session.query(Pessoas.nome).filter(Pessoas.id == pessoa_id).first()
    
    #subquery que conta avaliações realizadas até em cada pt (exclui as autormáticas futuras)
    avaliacoes_pt = db.session.query(planos_trabalhos_consolidacoes.plano_trabalho_id,
                                     label('qtd_aval',func.count(avaliacoes.id)))\
                              .join(planos_trabalhos_consolidacoes, planos_trabalhos_consolidacoes.id == avaliacoes.plano_trabalho_consolidacao_id)\
                              .group_by(planos_trabalhos_consolidacoes.plano_trabalho_id)\
                              .subquery()                                            
    
    
    planos_trab_pessoa  = db.session.query(label('pt_id',planos_trabalhos.id.distinct()),
                                           planos_trabalhos.data_inicio,
                                           planos_trabalhos.data_fim,
                                           planos_trabalhos.carga_horaria,
                                           planos_trabalhos.forma_contagem_carga_horaria,
                                           planos_trabalhos.status,
                                           Pessoas.nome,
                                           Unidades.sigla,
                                           label('forma',tipos_modalidades.nome),
                                           avaliacoes_pt.c.qtd_aval)\
                                    .filter(planos_trabalhos.usuario_id == pessoa_id)\
                                    .join(Pessoas, Pessoas.id == planos_trabalhos.usuario_id)\
                                    .outerjoin(planos_trabalhos_entregas, planos_trabalhos_entregas.plano_trabalho_id == planos_trabalhos.id)\
                                    .outerjoin(planos_entregas_entregas, planos_entregas_entregas.id == planos_trabalhos_entregas.plano_entrega_entrega_id)\
                                    .outerjoin(Unidades, Unidades.id == planos_trabalhos.unidade_id)\
                                    .outerjoin(tipos_modalidades, tipos_modalidades.id == planos_trabalhos.tipo_modalidade_id)\
                                    .outerjoin(avaliacoes_pt,avaliacoes_pt.c.plano_trabalho_id == planos_trabalhos.id,)\
                                    .order_by(planos_trabalhos.data_inicio,)\
                                    .all()    

    quantidade = len(planos_trab_pessoa)


    return render_template('consulta_pts_pessoa.html', quantidade = quantidade,
                                                dados_pessoa = dados_pessoa,
                                                planos_trab_pessoa = planos_trab_pessoa)                                                
        
## lista regramentos vinculados a uma pessoa

@pessoas.route('/<pessoa_id>/regramentos_pessoa')
@login_required
def regramentos_pessoa(pessoa_id):
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta uma lista de regramentos vinculados a uma pessoa.                            |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """   
                         
    dados_pessoa = db.session.query(Pessoas.nome).filter(Pessoas.id == pessoa_id).first()                                          
    
    
    regram_pessoa = db.session.query(programas_participantes.id,
                                     programas_participantes.habilitado,
                                     programas.nome,
                                     programas.data_inicio,
                                     programas.data_fim)\
                              .join(programas, programas.id == programas_participantes.programa_id)\
                              .filter(programas_participantes.deleted_at == None,
                                      programas_participantes.usuario_id == pessoa_id)\
                              .order_by(programas.data_inicio,)\
                              .all()    

    quantidade = len(regram_pessoa)


    return render_template('consulta_regramentos_pessoa.html', quantidade = quantidade,
                                                dados_pessoa = dados_pessoa,
                                                regram_pessoa = regram_pessoa) 
#