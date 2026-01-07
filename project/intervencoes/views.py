"""
.. topic:: Intervenções (views)

    Invervenções no sistema (recurso de último caso).


"""

# views.py na pasta intervencoes

from flask import abort, flash, render_template, request, Blueprint, send_from_directory, redirect, url_for
from flask_login import current_user, login_required

import uuid

from sqlalchemy import func, distinct
from sqlalchemy.sql import label
from project import db
from project.models import Unidades, Pessoas, integracao_servidores, integracao_unidades, unidades_integrantes,\
                            unidades_integrantes_atribuicoes, tipos_modalidades_siape, cidades, perfis
from project.intervencoes.forms import CPFForm

# from sqlalchemy.dialects import mysql

intervencoes = Blueprint('intervencoes',__name__, template_folder='templates')


## Mostra dados de usuarios e unidades a partir de CPF informado

@intervencoes.route('/servidor_unidade',methods=['GET','POST'])

def servidor_unidade():
    """
    +---------------------------------------------------------------------------------------+
    |Apresenta os dados de servidor e unidade nas tabelas de integrção e de produção.       |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 

    if not current_user.is_authenticated:
        abort(401)

    form = CPFForm()

    if form.validate_on_submit():

        cpf_consulta = form.cpf_consulta.data.replace('.', '').replace('-', '')

        # Dados da pessa e sua unidade nas tabelas de integração

        consulta_serv_integ = db.session.query(integracao_servidores.cpf,
                                            integracao_servidores.nome,
                                            integracao_servidores.sexo,
                                            integracao_servidores.emailfuncional,
                                            integracao_servidores.matriculasiape,
                                            integracao_servidores.codigo_cargo,
                                            integracao_servidores.coduorgexercicio,
                                            integracao_servidores.coduorglotacao,
                                            integracao_servidores.situacao_funcional,
                                            integracao_servidores.cpf_chefia_imediata,
                                            integracao_servidores.participa_pgd,
                                            tipos_modalidades_siape.nome.label('modalidade_pgd'))\
                                        .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == integracao_servidores.modalidade_pgd)\
                                        .filter(integracao_servidores.cpf == cpf_consulta)\
                                        .first()

        if not consulta_serv_integ:
            flash('CPF '+cpf_consulta+' não encontrado nas tabelas de integração.','erro')
            return redirect(url_for('intervencoes.servidor_unidade'))

        consulta_unid_integ = db.session.query(integracao_unidades.codigo_siape,
                                            integracao_unidades.siglauorg,
                                            integracao_unidades.nomeuorg,
                                            integracao_unidades.municipio_nome,
                                            integracao_unidades.municipio_uf,
                                            integracao_unidades.ativa,
                                            integracao_unidades.cpf_titular_autoridade_uorg)\
                                        .filter(integracao_unidades.codigo_siape == consulta_serv_integ.coduorgexercicio)\
                                        .first()

        # Dados da pessoa e sua unidade na produção

        consulta_serv_prod = db.session.query(Pessoas.id,
                                            Pessoas.cpf,
                                            Pessoas.nome,
                                            Pessoas.sexo,
                                            Pessoas.email,
                                            Pessoas.matricula,
                                            Pessoas.situacao_funcional,
                                            Pessoas.participa_pgd,
                                            tipos_modalidades_siape.nome.label('modalidade_pgd'))\
                                        .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == Pessoas.tipo_modalidade_id)\
                                        .filter(Pessoas.cpf == cpf_consulta)\
                                        .first()
        
        # Verifica se o servidor é gestor de unidade
        if consulta_serv_prod:
            c_s_g_p = db.session.query(Pessoas.id,
                                    unidades_integrantes.unidade_id)\
                                .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                                .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                .filter(Pessoas.id == consulta_serv_prod.id,
                                        unidades_integrantes_atribuicoes.atribuicao == 'GESTOR',
                                        unidades_integrantes_atribuicoes.deleted_at == None)\
                            .first()
        else:
            c_s_g_p = None    
        
        if consulta_serv_prod:
            consulta_unid_prod = db.session.query(unidades_integrantes.unidade_id,
                                                Unidades.codigo,
                                                Unidades.sigla,
                                                Unidades.nome,
                                                cidades.nome.label('cidade_nome'),
                                                cidades.uf.label('cidade_uf'),
                                                unidades_integrantes.id.label('unidade_integrante_id'),
                                                unidades_integrantes_atribuicoes.id.label('unidade_integrante_atribuicao_id'))\
                                            .join(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                                            .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                                            .filter(unidades_integrantes.usuario_id == consulta_serv_prod.id,
                                                    unidades_integrantes_atribuicoes.atribuicao == 'LOTADO',
                                                    unidades_integrantes_atribuicoes.deleted_at == None)\
                                            .first()
        else:
            consulta_unid_prod = None    

        return render_template('servidor_unidade.html', cpf = cpf_consulta,
                                                        c_s_i = consulta_serv_integ,
                                                        c_u_i = consulta_unid_integ,
                                                        c_s_p = consulta_serv_prod,
                                                        c_u_p = consulta_unid_prod,
                                                        c_s_g_p = c_s_g_p,
                                                        form = form)

    
    return render_template('servidor_unidade.html', cpf = None,
                                                    c_s_i = None,
                                                    c_u_i = None,
                                                    c_s_p = None,
                                                    c_u_p = None,
                                                    form = form)


@intervencoes.route('<cpf>/ajustar',methods=['GET','POST'])

def ajustar(cpf):
    """
    +---------------------------------------------------------------------------------------+
    |Ajusta os dados de servidor e unidade em produção conform tabelas de integrção         |
    |                                                                                       |
    +---------------------------------------------------------------------------------------+
    """ 
    if not current_user.is_authenticated:
        abort(401)

    cpf_consulta = cpf

    # Dados da pessoa e sua unidade de exercício na tabela integracao_servidores
    c_s_i = db.session.query(integracao_servidores.cpf,
                            integracao_servidores.nome,
                            integracao_servidores.sexo,
                            integracao_servidores.emailfuncional,
                            integracao_servidores.matriculasiape,
                            integracao_servidores.nomeguerra,
                            integracao_servidores.telefone,
                            integracao_servidores.data_nascimento,
                            integracao_servidores.uf,
                            integracao_servidores.codigo_cargo,
                            integracao_servidores.coduorgexercicio,
                            integracao_servidores.situacao_funcional,
                            integracao_servidores.cpf_chefia_imediata,
                            integracao_servidores.cod_jornada,
                            integracao_servidores.nome_jornada,
                            integracao_servidores.participa_pgd,
                            label('modalidade_pgd', tipos_modalidades_siape.nome))\
                        .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == integracao_servidores.modalidade_pgd)\
                        .filter(integracao_servidores.cpf == cpf_consulta)\
                        .first()
    # Dados da unidade de exercício na tabela integracao_unidades
    c_u_i = db.session.query(integracao_unidades.codigo_siape,
                            integracao_unidades.siglauorg,
                            integracao_unidades.nomeuorg,
                            integracao_unidades.municipio_nome,
                            integracao_unidades.municipio_uf,
                            integracao_unidades.ativa,
                            integracao_unidades.cpf_titular_autoridade_uorg)\
                        .filter(integracao_unidades.codigo_siape == c_s_i.coduorgexercicio)\
                        .first()

    if c_u_i.cpf_titular_autoridade_uorg == c_s_i.cpf:
        print('Servidor é chefe da unidade de exercício (',c_u_i.siglauorg,').')
        chefe_unidade = True
    else:
        chefe_unidade = False

    # Dados da pessoa e unidade em que está lotado produção
    c_s_p = db.session.query(Pessoas.id,
                            Pessoas.cpf,
                            Pessoas.nome,
                            Pessoas.sexo,
                            Pessoas.email,
                            Pessoas.matricula,
                            Pessoas.situacao_funcional,
                            Pessoas.participa_pgd,
                            tipos_modalidades_siape.nome.label('modalidade_pgd'))\
                        .outerjoin(tipos_modalidades_siape, tipos_modalidades_siape.id == Pessoas.tipo_modalidade_id)\
                        .filter(Pessoas.cpf == cpf_consulta)\
                        .first()

    # Dados da unidade de lotação em produção
    if c_s_p:
        c_u_p = db.session.query(Unidades.codigo,
                                Unidades.sigla,
                                Unidades.nome,
                                cidades.nome.label('cidade_nome'),
                                cidades.uf.label('cidade_uf'),
                                unidades_integrantes.unidade_id,
                                unidades_integrantes.id.label('unidade_integrante_id'),
                                unidades_integrantes_atribuicoes.id.label('unidade_integrante_atribuicao_id'))\
                            .join(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                            .outerjoin(cidades, cidades.id == Unidades.cidade_id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .filter(unidades_integrantes.usuario_id == c_s_p.id,
                                    unidades_integrantes_atribuicoes.atribuicao == 'LOTADO',
                                    unidades_integrantes_atribuicoes.deleted_at == None)\
                            .first()
    else:
        c_u_p = None

    # Realiza os ajustes na base de produção

    ## divergênia em e-mail ou participação/modalidade PGD e, se necessário, registro do servidor em produção
    if c_s_p:

        ## servidor com e-mail diferente
        if c_s_i.emailfuncional and c_s_i.emailfuncional != c_s_p.email:
            print('E-mail diferente. SIAPE ',c_s_i.emailfuncional,'Prod ', c_s_p.email,'. Ajustando...')
            db.session.query(Pessoas)\
                        .filter(Pessoas.id == c_s_p.id)\
                        .update({'email': c_s_i.emailfuncional,'updated_at': func.now()})
            db.session.commit()
        # servidor com participação PGD diferente
        if c_s_i.participa_pgd != c_s_p.participa_pgd:
            print('Participação PGD diferente. SIAPE ',c_s_i.participa_pgd,'Prod ', c_s_p.participa_pgd,'. Ajustando...')
            if c_s_i.participa_pgd is None:
                participa_pgd = 'não'
            else:
                participa_pgd = c_s_i.participa_pgd
            db.session.query(Pessoas)\
                        .filter(Pessoas.id == c_s_p.id)\
                        .update({'participa_pgd': participa_pgd,'updated_at': func.now()})
            db.session.commit()
        # servidor com modalidade PGD diferente
        if c_s_i.modalidade_pgd != c_s_p.modalidade_pgd:
            print('Modalidade PGD diferente. SIAPE ',c_s_i.modalidade_pgd,'Prod ', c_s_p.modalidade_pgd,'. Ajustando...')
            if c_s_i.modalidade_pgd:
                modalidade = db.session.query(tipos_modalidades_siape)\
                                    .filter(tipos_modalidades_siape.nome == c_s_i.modalidade_pgd)\
                                    .first()
                db.session.query(Pessoas)\
                            .filter(Pessoas.id == c_s_p.id)\
                            .update({'modalidade_pgd': modalidade.id,'updated_at': func.now()})
                db.session.commit()
            else:
                flash('Modalidade PGD não informada no SIAPE. Ajuste não realizado.','erro')
                print('Modalidade PGD não informada no SIAPE. Ajuste não realizado.')
    
    
    
    else:
        print('Servidor não encontrado na base de produção. Teremos que inserí-lo...')
        # verificar se a unidade de exercício existe na base de produção
        unid_exercicio = db.session.query(Unidades.id)\
                            .filter(Unidades.codigo == c_u_i.codigo_siape)\
                            .first()
        if not unid_exercicio:
            flash('Unidade de exercício do SIAPE ('+c_u_i.codigo_siape+') não encontrada na base de produção. Impossível inserir o servidor.','erro')
            return redirect(url_for('intervencoes.servidor_unidade'))
        # pegar a modalidade PGD
        if c_s_i.modalidade_pgd:
            modalidade = db.session.query(tipos_modalidades_siape)\
                                .filter(tipos_modalidades_siape.nome == c_s_i.modalidade_pgd)\
                                .first()
        else:
            modalidade = db.session.query(tipos_modalidades_siape)\
                                .filter(tipos_modalidades_siape.nome == 'presencial')\
                                .first()
        modalidade_id = modalidade.id if modalidade else None  
        # pegar perfil_id
        perfil = db.session.query(perfis)\
                            .filter(perfis.nome == 'Perfil Participante')\
                            .first()
        perfil_id = perfil.id if perfil else None  

        # inserir o servidor na base de produção
        id_pessoa = uuid.uuid4()
        created_at = updated_at = func.now()
        nova_pessoa = Pessoas(id         = id_pessoa,
                              created_at = created_at,
                              updated_at = updated_at,
                              cpf       = c_s_i.cpf,
                              nome      = c_s_i.nome,
                              sexo      = c_s_i.sexo,
                              email     = c_s_i.emailfuncional,
                              matricula = c_s_i.matriculasiape,
                              apelido            = c_s_i.nomeguerra,
                              telefone           = c_s_i.telefone,
                              data_nascimento    = c_s_i.data_nascimento,
                              uf                 = c_s_i.uf,
                              situacao_funcional = c_s_i.situacao_funcional,
                              situacao_siape     = 'ATIVO',
                              usuario_externo    = 0,
                              perfil_id          = perfil_id,
                              is_admin           = 0,
                              cod_jornada        = c_s_i.cod_jornada,
                              nome_jornada       = c_s_i.nome_jornada,
                              tipo_modalidade_id = modalidade_id,
                              participa_pgd      = c_s_i.participa_pgd,
                              deleted_at = None,
                              remember_token = None,
                              password = None,
                              id_google = None,
                              url_foto = None,
                              texto_complementar_plano = None,
                              foto_perfil = None,
                              foto_google = None,
                              foto_microsoft = None,
                              foto_firebase = None,
                              id_sei = None,
                              email_verified_at = None,
                              data_ativacao_temporaria = None,
                              justicativa_ativacao_temporaria = None,
                              config = None,
                              notificacoes = None,
                              metadados = None,
                              data_modificacao = None,
                              data_envio_api_pgd = None,
                              data_inicial_pedagio = None,
                              data_final_pedagio = None,
                              tipo_pedagio = None)
        db.session.add(nova_pessoa)
        # tornar pessoa integrante da unidade de exercício
        id_unid_integrantes = uuid.uuid4()
        created_at = updated_at = func.now()
        unidades_integrantes_novo = unidades_integrantes(id          = id_unid_integrantes,
                                                         created_at  = created_at,
                                                         updated_at  = updated_at,
                                                         deleted_at  = None,
                                                         usuario_id  = id_pessoa,
                                                         unidade_id  = unid_exercicio.id)
        db.session.add(unidades_integrantes_novo)
        # lotar a pessoa em unidades_integrantes_atribuicoes
        id_unid_integrantes_atrib = uuid.uuid4()
        created_at = updated_at = func.now()
        u_i_a_novo = unidades_integrantes_atribuicoes(id                    = id_unid_integrantes_atrib,
                                                      created_at            = created_at,
                                                      updated_at            = updated_at,
                                                      deleted_at            = None,
                                                      atribuicao            = 'LOTADO',
                                                      unidade_integrante_id = id_unid_integrantes)
        db.session.add(u_i_a_novo)

        db.session.commit()

    ## servidor existe no SIAPE e em produção, mas está lotado em unidade diferente do que consta no SIAPE
    ## vamos alterar o registro atual de integrante e criar um novo para manter ele como vinculado na unidade antiga
    if c_s_p and c_u_p and c_u_i.codigo_siape != c_u_p.codigo:
        # pegar a unidade correta em produção
        unid_correta = db.session.query(Unidades.id)\
                                 .filter(Unidades.codigo == c_u_i.codigo_siape)\
                                 .first()

        print('A unidade de lotação está diferente. SIAPE ',c_u_i.codigo_siape,'Prod ', c_u_p.codigo,'. Ajustando...')
        # buscar o id da unidade correta e atualizar o unidade_id em unidades_integrantes,
        # não precisa mexer na lotação, poi o c_u_p só pega os lotados)
        if unid_correta:
            print('unidade_id no registro ', c_u_p.unidade_integrante_id,' de unidades_integrantes será trocado para:', unid_correta.id)
            db.session.query(unidades_integrantes)\
                        .filter(unidades_integrantes.id == c_u_p.unidade_integrante_id)\
                        .update({'unidade_id': unid_correta.id,'updated_at': func.now()})
            
            # manter a pessoa vinculada na unidade anterior
            id_unid_integrantes_velho = uuid.uuid4()
            created_at = updated_at = func.now()
            unidades_integrantes_velha = unidades_integrantes(id         = id_unid_integrantes,
                                                                created_at = created_at,
                                                                updated_at = updated_at,
                                                                deleted_at = None,
                                                                usuario_id = c_s_p.id,
                                                                unidade_id = c_u_p.unidade_id)
            db.session.add(unidades_integrantes_velha)
            # criar a atribuição de COLABORADOR na unidade antiga
            id_unid_integrantes_atrib = uuid.uuid4()
            created_at = updated_at = func.now()
            u_i_a_velho = unidades_integrantes_atribuicoes(id         = id_unid_integrantes_atrib,
                                                            created_at = created_at,
                                                            updated_at = updated_at,
                                                            deleted_at = None,
                                                            unidade_integrante_id = id_unid_integrantes_velho,
                                                            atribuicao = 'COLABORADOR')
            db.session.add(u_i_a_velho)
            db.session.commit()

        else:
            flash('Unidade do SIAPE ('+c_u_i.codigo_siape+') não encontrada na base de produção. Impossível ajustar a lotação.','erro')
            print('Unidade do SIAPE ('+c_u_i.codigo_siape+') não encontrada na base de produção. Impossível ajustar a lotação.')
            return redirect(url_for('intervencoes.servidor_unidade')) 
    elif c_s_p and not c_u_p:
        print('Não encontrada lotação para o servidor em produção.')  
        # pegar a unidade correta em produção
        unid_correta = db.session.query(Unidades.id)\
                                 .filter(Unidades.codigo == c_u_i.codigo_siape)\
                                 .first()
        if unid_correta:
            # ver se servidor faz parte (integrante) da unidade que consta no SIAPE
            # para forçar que ele seja lotado nela (atribuição)
            integrante_existente = db.session.query(unidades_integrantes.id)\
                                                .filter(unidades_integrantes.usuario_id == c_s_p.id,
                                                        unidades_integrantes.unidade_id == unid_correta.id)\
                                                .first()
            if not integrante_existente:
                # não sendo integrante, criar o vínculo
                print('Integrando servidor na unidade_id:', unid_correta.id)
                id_unid_integrantes = uuid.uuid4()
                created_at = updated_at = func.now()
                unidades_integrantes_novo = unidades_integrantes(id         = id_unid_integrantes,
                                                                created_at = created_at,
                                                                updated_at = updated_at,
                                                                deleted_at = None,
                                                                usuario_id = c_s_p.id,
                                                                unidade_id = unid_correta.id)
                db.session.add(unidades_integrantes_novo)
            else:
                id_unid_integrantes = integrante_existente.id    
            # criar a atribuição de LOTADO
            id_unid_integrantes_atrib = uuid.uuid4()
            created_at = updated_at = func.now()
            u_i_a_novo = unidades_integrantes_atribuicoes(id         = id_unid_integrantes_atrib,
                                                            created_at = created_at,
                                                            updated_at = updated_at,
                                                            deleted_at = None,
                                                            unidade_integrante_id = id_unid_integrantes,
                                                            atribuicao = 'LOTADO')
            db.session.add(u_i_a_novo)
            db.session.commit()
        else:
            flash('Unidade do SIAPE ('+c_u_i.codigo_siape+') não encontrada na base de produção. Impossível integrar servidor.','erro')
            print('Unidade do SIAPE ('+c_u_i.codigo_siape+') não encontrada na base de produção. Impossível integrar servidor.')
            return redirect(url_for('intervencoes.servidor_unidade'))        

    # Verifica se o servidor é gestor de unidade no Petrvs
    if c_s_p:
        c_s_g_p = db.session.query(Pessoas.id,
                                unidades_integrantes.unidade_id,
                                Unidades.codigo.label('unidade_codigo'))\
                            .join(unidades_integrantes, unidades_integrantes.usuario_id == Pessoas.id)\
                            .join(unidades_integrantes_atribuicoes, unidades_integrantes_atribuicoes.unidade_integrante_id == unidades_integrantes.id)\
                            .join(Unidades, Unidades.id == unidades_integrantes.unidade_id)\
                            .filter(Pessoas.id == c_s_p.id,
                                    unidades_integrantes_atribuicoes.atribuicao == 'GESTOR',
                                    unidades_integrantes_atribuicoes.deleted_at == None)\
                            .first()
    else:
        c_s_g_p = None    
    
    ## servidor é chefe, segundo o SIAPE, mas sem atribuição de GESTOR na unidade
    if not c_s_g_p and chefe_unidade:
        # criar a atribuição de GESTOR
        id_unid_integrantes_atrib = uuid.uuid4()
        created_at = updated_at = func.now()
        u_i_a_novo = unidades_integrantes_atribuicoes(id                 = id_unid_integrantes_atrib,
                                                      created_at         = created_at,
                                                      updated_at         = updated_at,
                                                      deleted_at         = None,
                                                      unidade_integrante_id = c_u_p.unidade_integrante_id,
                                                      atribuicao = 'GESTOR')
        db.session.add(u_i_a_novo)
  
        # colocar Perfil Unidade para a pessoa
        perfil = db.session.query(perfis)\
                            .filter(perfis.nome == 'Perfil Unidade')\
                            .first()
        perfil_id = perfil.id if perfil else None 
        db.session.query(Pessoas)\
                    .filter(Pessoas.id == c_s_p.id)\
                    .update({'perfil_id': perfil_id,'updated_at': func.now()})
        
        # verificar se o servidor é chefe substituto na unidade, se sim, remover essa atribuição
        db.session.query(unidades_integrantes_atribuicoes.id)\
                  .filter(unidades_integrantes_atribuicoes.unidade_integrante_id == c_u_p.unidade_integrante_id,
                          unidades_integrantes_atribuicoes.atribuicao == 'CHEFE_SUBSTITUTO',
                          unidades_integrantes_atribuicoes.deleted_at == None)\
                  .update({'deleted_at': func.now()})
        db.session.commit()

    flash('Ajustes para '+ c_s_i.nome +' ('+ c_s_i.cpf +')'+' realizados na base de produção conforme tabelas de integração.','sucesso')

    return redirect(url_for('intervencoes.servidor_unidade'))   

