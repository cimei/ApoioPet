"""
.. topic:: Modelos (tabelas nos bancos de dados)

    Os modelos são classes que definem a estrutura das tabelas dos bancos de dados.

    Os modelos de interesse do banco petrvs_home são os seguintes:

    * Unidades
    * Pessoas (usuarios)
    * programas
    * avaliacoes
    * planos_entregas
    * panos_entregas_entregas


    Abaixo seguem os Modelos e respectivos campos.
"""
# models.py
from project import app
from project import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet 
from flask_login import UserMixin
from datetime import datetime, date
from ldap3 import Server, Connection, NTLM
import os

from sqlalchemy.orm import relationship

@login_manager.user_loader
def load_user(id):
    return Pessoas.query.get(id)


#Planejamento

class planejamentos(db.Model):

    __tablename__ = 'planejamentos'
    # __table_args__ = {"schema": ""}

    id                        = db.Column(db.String, primary_key = True)
    created_at                = db.Column(db.DateTime)
    updated_at                = db.Column(db.DateTime)
    deleted_at                = db.Column(db.DateTime)
    nome                      = db.Column(db.String)
    missao                    = db.Column(db.String)
    visao                     = db.Column(db.String)
    data_inicio               = db.Column(db.DateTime)
    data_fim                  = db.Column(db.DateTime)
    data_arquivamento         = db.Column(db.DateTime)
    valores                   = db.Column(db.JSON)
    resultados_institucionais = db.Column(db.JSON)
    entidade_id               = db.Column(db.String)
    unidade_id                = db.Column(db.String)
    planejamento_superior_id  = db.Column(db.String)
    
    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , nome
                     , missao
                     , visao
                     , data_inicio
                     , data_fim
                     , data_arquivamento
                     , valores
                     , resultados_institucionais
                     , entidade_id
                     , unidade_id
                     , planejamento_superior_id):
        
        self.id = id      
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.nome = nome
        self.missao = missao
        self.visao = visao
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.data_arquivamento = data_arquivamento
        self.valores = valores
        self.resultados_institucionais = resultados_institucionais
        self.entidade_id = entidade_id
        self.unidade_id = unidade_id
        self.planejamento_superior_id =  planejamento_superior_id
        
    def __repr__ (self):
        return f"{self.nome};{self.data_inicio};{self.data_fim}"


#Objetivos no Planejamento

class planejamentos_objetivos(db.Model):

    __tablename__ = 'planejamentos_objetivos'
    # __table_args__ = {"schema": ""}

    id                        = db.Column(db.String, primary_key = True)
    created_at                = db.Column(db.DateTime)
    updated_at                = db.Column(db.DateTime)
    deleted_at                = db.Column(db.DateTime)
    sequencia                 = db.Column(db.Integer)
    fundamentacao             = db.Column(db.String)
    nome                      = db.Column(db.String)
    path                      = db.Column(db.String)
    planejamento_id           = db.Column(db.String)
    eixo_tematico_id          = db.Column(db.String)
    objetivo_pai_id           = db.Column(db.String)
    objetivo_superior_id      = db.Column(db.String)
    integra_okr               = db.Column(db.Integer)

    def __init__(self, id
                     ,created_at
                     ,updated_at
                     ,deleted_at
                     ,sequencia
                     ,fundamentacao
                     ,nome
                     ,path
                     ,planejamento_id
                     ,eixo_tematico_id
                     ,objetivo_pai_id
                     ,objetivo_superior_id
                     ,integra_okr):

        self.id                   = id
        self.created_at           = created_at
        self.updated_at           = updated_at
        self.deleted_at           = deleted_at
        self.sequencia            = sequencia
        self.fundamentacao        = fundamentacao
        self.nome                 = nome
        self.path                 = path
        self.planejamento_id      = planejamento_id
        self.eixo_tematico_id     = eixo_tematico_id
        self.objetivo_pai_id      = objetivo_pai_id
        self.objetivo_superior_id = objetivo_superior_id
        self.integra_okr          = integra_okr
        
    def __repr__ (self):
        return f"{self.nome}"    


#Eixos temáticos no Planejamento

class eixos_tematicos(db.Model):

    __tablename__ = 'eixos_tematicos'
    # __table_args__ = {"schema": ""}

    id          = db.Column(db.String, primary_key = True)
    created_at  = db.Column(db.DateTime)
    updated_at  = db.Column(db.DateTime)
    deleted_at  = db.Column(db.DateTime)
    nome        = db.Column(db.String)
    icone       = db.Column(db.String)
    cor         = db.Column(db.String)
    descricao   = db.Column(db.String)

    def __init__(self, id
                     ,created_at
                     ,updated_at
                     ,deleted_at
                     ,nome
                     ,icone
                     ,cor
                     ,descricao):

        self.id         = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.nome       = nome
        self.icone      = icone
        self.cor        = cor
        self.descricao  = descricao
        
    def __repr__ (self):
        return f"{self.nome}"    


# Unidades

class Unidades(db.Model):

    __tablename__ = 'unidades'
    # __table_args__ = {"schema": ""}

    id              = db.Column(db.String, primary_key = True)
    created_at      = db.Column(db.DateTime)
    updated_at      = db.Column(db.DateTime)
    deleted_at      = db.Column(db.DateTime)
    codigo          = db.Column(db.String)
    sigla           = db.Column(db.String)
    nome            = db.Column(db.String)
    instituidora    = db.Column(db.Integer)
    path            = db.Column(db.String)
    texto_complementar_plano            = db.Column(db.String)
    atividades_arquivamento_automatico  = db.Column(db.Integer)
    atividades_avaliacao_automatico     = db.Column(db.Integer)
    planos_prazo_comparecimento         = db.Column(db.Integer)
    planos_tipo_prazo_comparecimento    = db.Column(db.String)
    data_inativacao                     = db.Column(db.DateTime)
    distribuicao_forma_contagem_prazos  = db.Column(db.String)
    entrega_forma_contagem_prazos       = db.Column(db.String)
    autoedicao_subordinadas             = db.Column(db.Integer)
    etiquetas           = db.Column(db.String)
    checklist           = db.Column(db.String)
    notificacoes        = db.Column(db.String)
    expediente          = db.Column(db.String)
    cidade_id           = db.Column(db.String)
    unidade_pai_id      = db.Column(db.String)
    entidade_id         = db.Column(db.String)
    informal            = db.Column(db.Integer)
    data_modificacao    = db.Column(db.DateTime)

    def __init__(self, id
                     , data_modificacao
                     , created_at
                     , updated_at
                     , deleted_at
                     , codigo
                     , sigla
                     , nome
                     , instituidora
                     , path
                     , texto_complementar_plano
                     , atividades_arquivamento_automatico
                     , atividades_avaliacao_automatico
                     , planos_prazo_comparecimento
                     , planos_tipo_prazo_comparecimento
                     , data_inativacao
                     , distribuicao_forma_contagem_prazos
                     , entrega_forma_contagem_prazos
                     , autoedicao_subordinadas
                     , etiquetas
                     , checklist
                     , notificacoes
                     , expediente
                     , cidade_id
                     , unidade_pai_id
                     , entidade_id
                     , informal):
        
        self.id                 = id
        self.data_modificacao   = data_modificacao
        self.created_at         = created_at
        self.updated_at         = updated_at
        self.deleted_at         = deleted_at
        self.codigo             = codigo
        self.sigla              = sigla
        self.nome               = nome
        self.instituidora       = instituidora
        self.path               = path
        self.texto_complementar_plano           = texto_complementar_plano
        self.atividades_arquivamento_automatico = atividades_arquivamento_automatico
        self.atividades_avaliacao_automatico    = atividades_avaliacao_automatico
        self.planos_prazo_comparecimento        = planos_prazo_comparecimento
        self.planos_tipo_prazo_comparecimento   = planos_tipo_prazo_comparecimento
        self.data_inativacao                    = data_inativacao
        self.distribuicao_forma_contagem_prazos = distribuicao_forma_contagem_prazos
        self.entrega_forma_contagem_prazos      = entrega_forma_contagem_prazos
        self.autoedicao_subordinadas            = autoedicao_subordinadas
        self.etiquetas      = etiquetas
        self.checklist      = checklist
        self.notificacoes   = notificacoes
        self.expediente     = expediente
        self.cidade_id      = cidade_id
        self.unidade_pai_id = unidade_pai_id
        self.entidade_id    = entidade_id
        self.informal       = informal

    def __repr__ (self):
        return f"{self.codigo};{self.sigla};{self.nome}"


# cidades

class cidades(db.Model):

    __tablename__ = 'cidades'
    # __table_args__ = {"schema": ""}

    id          = db.Column(db.String, primary_key = True)
    created_at  = db.Column(db.DateTime)
    updated_at  = db.Column(db.DateTime)
    deleted_at  = db.Column(db.DateTime)
    codigo_ibge = db.Column(db.String)
    nome        = db.Column(db.String)
    tipo        = db.Column(db.String)
    uf          = db.Column(db.String)
    timezone    = db.Column(db.Integer)

    
    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , codigo_ibge
                     , nome
                     , tipo
                     , uf
                     , timezone):
    
        self.id          = id
        self.created_at  = created_at
        self.updated_at  = updated_at
        self.deleted_at  = deleted_at
        self.codigo_ibge = codigo_ibge
        self.nome        = nome
        self.tipo        = tipo
        self.uf          = uf
        self.timezone    = timezone
        
    def __repr__ (self):
            return f"{self.nome};{self.uf}"    



# unidades_integrantes: relação unidade usuário

class unidades_integrantes(db.Model):

    __tablename__ = 'unidades_integrantes'
    # __table_args__ = {"schema": ""}

    id          = db.Column(db.String, primary_key = True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    unidade_id = db.Column(db.String)
    usuario_id = db.Column(db.String)
    
    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , unidade_id
                     , usuario_id):
    
        self.id         = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.unidade_id = unidade_id
        self.usuario_id = usuario_id
        
    def __repr__ (self):
            return f"{self.unidade_id};{self.usuario_id}"    


# unidades_integrantes_atribuicoes

class unidades_integrantes_atribuicoes(db.Model):

    __tablename__ = 'unidades_integrantes_atribuicoes'
    # __table_args__ = {"schema": ""}

    id                     = db.Column(db.String, primary_key = True)
    created_at             = db.Column(db.DateTime)
    updated_at             = db.Column(db.DateTime)
    deleted_at             = db.Column(db.DateTime)
    atribuicao             = db.Column(db.String)
    unidade_integrante_id  = db.Column(db.String)
    
    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , atribuicao
                     , unidade_integrante_id):
    
        self.id                    = id
        self.created_at            = created_at
        self.updated_at            = updated_at
        self.deleted_at            = deleted_at
        self.atribuicao            = atribuicao
        self.unidade_integrante_id = unidade_integrante_id
        
    def __repr__ (self):
            return f"{self.atribuicao};{self.unidade_integrante_id}"    


# perfis

class perfis(db.Model):

    __tablename__ = 'perfis'
    # __table_args__ = {"schema": ""}
    
    id         = db.Column(db.String, primary_key = True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    nivel      = db.Column(db.Integer)
    nome       = db.Column(db.String)
    descricao  = db.Column(db.String)

    
    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , nivel
                     , nome
                     , descricao):
    
        self.id         = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.nivel      = nivel
        self.nome       = nome
        self.descricao  = descricao
        
    def __repr__ (self):
            return f"{self.nivel};{self.nome};{self.descricao}"

# usuarios

class Pessoas(db.Model, UserMixin):

    __tablename__ = 'usuarios'
    # __table_args__ = {"schema": ""}
    
    id                       = db.Column(db.String, primary_key = True)
    created_at               = db.Column(db.DateTime)
    updated_at               = db.Column(db.DateTime)
    deleted_at               = db.Column(db.DateTime)
    remember_token           = db.Column(db.String)
    nome                     = db.Column(db.String)
    email                    = db.Column(db.String)
    password                 = db.Column(db.String)
    cpf                      = db.Column(db.String)
    matricula                = db.Column(db.String)
    apelido                  = db.Column(db.String)
    telefone                 = db.Column(db.String)
    data_nascimento          = db.Column(db.DateTime)
    id_google                = db.Column(db.String)
    url_foto                 = db.Column(db.String)
    texto_complementar_plano = db.Column(db.String)
    foto_perfil              = db.Column(db.String)
    foto_google              = db.Column(db.String)
    foto_microsoft           = db.Column(db.String)
    foto_firebase            = db.Column(db.String)
    id_sei                   = db.Column(db.String)
    uf                       = db.Column(db.String)
    email_verified_at        = db.Column(db.DateTime)
    sexo                     = db.Column(db.String)
    situacao_funcional       = db.Column(db.String)
    config                   = db.Column(db.JSON)
    notificacoes             = db.Column(db.JSON)
    metadados                = db.Column(db.JSON)
    perfil_id                = db.Column(db.String)
    data_modificacao         = db.Column(db.DateTime)
    is_admin                 = db.Column(db.Integer)
    data_envio_api_pgd       = db.Column(db.DateTime)
    data_inicial_pedagio     = db.Column(db.DateTime)
    data_final_pedagio       = db.Column(db.DateTime)
    tipo_pedagio             = db.Column(db.Integer)

    # nome_jornada             = db.Column(db.String)
    # cod_jornada              = db.Column(db.Integer)
    

    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , remember_token
                     , email
                     , nome
                     , password
                     , cpf
                     , matricula
                     , apelido
                     , data_nascimento
                     , telefone
                     , id_google
                     , url_foto
                     , texto_complementar_plano
                     , foto_perfil
                     , foto_google
                     , foto_microsoft
                     , foto_firebase
                     , id_sei
                     , uf
                     , email_verified_at
                     , sexo
                     , situacao_funcional
                     , config
                     , notificacoes
                     , metadados
                     , perfil_id
                     , data_modificacao
                     , is_admin
                     , data_envio_api_pgd
                     , data_inicial_pedagio
                     , data_final_pedagio
                     , tipo_pedagio):

        self.id                       = id
        self.created_at               = created_at
        self.updated_at               = updated_at
        self.deleted_at               = deleted_at
        self.remember_token           = remember_token
        self.email                    = email
        self.nome                     = nome
        self.password                 = password
        self.cpf                      = cpf
        self.matricula                = matricula
        self.apelido                  = apelido
        self.data_nascimento          = data_nascimento
        self.telefone                 = telefone
        self.id_google                = id_google
        self.url_foto                 = url_foto
        self.texto_complementar_plano = texto_complementar_plano
        self.foto_perfil              = foto_perfil
        self.foto_google              = foto_google
        self.foto_microsoft           = foto_microsoft
        self.foto_firebase            = foto_firebase
        self.id_sei                   = id_sei
        self.uf                       = uf
        self.email_verified_at        = email_verified_at
        self.sexo                     = sexo
        self.situacao_funcional       = situacao_funcional
        self.config                   = config
        self.notificacoes             = notificacoes
        self.metadados                = metadados
        self.perfil_id                = perfil_id
        self.data_modificacao         = data_modificacao
        self.is_admin                 = is_admin
        self.data_envio_api_pgd       = data_envio_api_pgd
        self.data_inicial_pedagio     = data_inicial_pedagio
        self.data_final_pedagio       = data_final_pedagio
        self.tipo_pedagio             = tipo_pedagio

    @staticmethod
    def conecta_ldap(username, password, str_DN):

        ldap_url = os.environ.get('LDAP_URL')
        server = Server(ldap_url)
        user_str_DN = 'uid='+username.strip()+','+str_DN.strip()
        conn = Connection(server, user_str_DN, password)
        status = conn.bind()
        if status:
            print('*** Conexão LDAP '+ldap_url+' ok. ***')
            return conn 
        else:
            print('*** Conexão LDAP '+ldap_url+' NÃO ok. ***')
            return 'sem_credencial'   
            
    def get_id(self):
        """Return id no lugar do Id do UserMixin """
        return self.id 
    
    
    def __repr__ (self):
            return f"{self.matricula};{self.nome};{self.email}"


# tipos_modalidades

class tipos_modalidades(db.Model):

    __tablename__ = 'tipos_modalidades'
    # __table_args__ = {"schema": ""}

    id                           = db.Column(db.String, primary_key = True)
    created_at                   = db.Column(db.DateTime)
    updated_at                   = db.Column(db.DateTime)
    deleted_at                   = db.Column(db.DateTime)
    nome                         = db.Column(db.String)
    plano_trabalho_calcula_horas = db.Column(db.Integer)
    atividade_tempo_despendido   = db.Column(db.Integer)
    atividade_esforco            = db.Column(db.Integer)
    
    def __init__(self, id    
                     , created_at
                     , updated_at
                     , deleted_at
                     , nome
                     , plano_trabalho_calcula_horas
                     , atividade_tempo_despendido
                     , atividade_esforco):
        
        self.id                           = id
        self.created_at                   = created_at
        self.updated_at                   = updated_at
        self.deleted_at                   = deleted_at
        self.nome                         = nome
        self.plano_trabalho_calcula_horas = plano_trabalho_calcula_horas
        self.atividade_tempo_despendido   = atividade_tempo_despendido
        self.atividade_esforco            = atividade_esforco
        
    def __repr__ (self):
            return f"{self.nome}"    
      

# programas (regramento)

class programas(db.Model):

    __tablename__ = 'programas'
    # __table_args__ = {"schema": ""}

    id                                           = db.Column(db.String, primary_key = True)
    created_at                                   = db.Column(db.DateTime)
    updated_at                                   = db.Column(db.DateTime)
    deleted_at                                   = db.Column(db.DateTime)
    nome                                         = db.Column(db.String)
    normativa                                    = db.Column(db.String)
    prazo_max_plano_entrega                      = db.Column(db.Integer)
    termo_obrigatorio                            = db.Column(db.Integer)
    config                                       = db.Column(db.String)
    data_inicio                                  = db.Column(db.DateTime)
    data_fim                                     = db.Column(db.DateTime)
    periodicidade_consolidacao                   = db.Column(db.String)
    periodicidade_valor                          = db.Column(db.Integer)
    dias_tolerancia_consolidacao                 = db.Column(db.Integer)
    dias_tolerancia_avaliacao                    = db.Column(db.Integer)
    dias_tolerancia_recurso_avaliacao            = db.Column(db.Integer)
    nota_padrao_avaliacao                        = db.Column(db.String)
    checklist_avaliacao_entregas_plano_entrega   = db.Column(db.String)
    checklist_avaliacao_entregas_plano_trabalho  = db.Column(db.String)
    registra_comparecimento                      = db.Column(db.Integer)
    plano_trabalho_assinatura_participante       = db.Column(db.Integer)
    plano_trabalho_assinatura_gestor_lotacao     = db.Column(db.Integer)
    documento_id                                 = db.Column(db.String)
    tipo_documento_tcr_id                        = db.Column(db.String)
    template_tcr_id                              = db.Column(db.String)
    unidade_id                                   = db.Column(db.String)
    tipo_justificativa_id                        = db.Column(db.String)
    tipo_avaliacao_plano_entrega_id              = db.Column(db.String)
    tipo_avaliacao_plano_trabalho_id             = db.Column(db.String)
    plano_trabalho_assinatura_gestor_entidade    = db.Column(db.Integer)
    plano_trabalho_assinatura_gestor_unidade     = db.Column(db.Integer)
    plano_trabalho_criterios_avaliacao           = db.Column(db.String)
    link_normativa                               = db.Column(db.String)


    def __init__(self, id    
                    , created_at
                    , updated_at
                    , deleted_at
                    , nome
                    , normativa
                    , prazo_max_plano_entrega
                    , termo_obrigatorio
                    , config
                    , data_inicio
                    , data_fim
                    , periodicidade_consolidacao
                    , periodicidade_valor
                    , dias_tolerancia_consolidacao
                    , dias_tolerancia_avaliacao
                    , dias_tolerancia_recurso_avaliacao
                    , nota_padrao_avaliacao
                    , checklist_avaliacao_entregas_plano_entrega
                    , checklist_avaliacao_entregas_plano_trabalho
                    , registra_comparecimento
                    , plano_trabalho_assinatura_participante
                    , plano_trabalho_assinatura_gestor_lotacao
                    , documento_id
                    , tipo_documento_tcr_id
                    , template_tcr_id
                    , unidade_id
                    , tipo_justificativa_id
                    , tipo_avaliacao_plano_entrega_id
                    , tipo_avaliacao_plano_trabalho_id
                    , plano_trabalho_assinatura_gestor_entidade
                    , plano_trabalho_assinatura_gestor_unidade
                    , plano_trabalho_criterios_avaliacao
                    , link_normativa):

        self.id                                          = id
        self.created_at                                  = created_at
        self.updated_at                                  = updated_at
        self.deleted_at                                  = deleted_at
        self.nome                                        = nome
        self.normativa                                   = normativa
        self.prazo_max_plano_entrega                     = prazo_max_plano_entrega
        self.termo_obrigatorio                           = termo_obrigatorio
        self.config                                      = config
        self.data_inicio                                 = data_inicio
        self.data_fim                                    = data_fim
        self.periodicidade_consolidacao                  = periodicidade_consolidacao
        self.periodicidade_valor                         = periodicidade_valor
        self.dias_tolerancia_consolidacao                = dias_tolerancia_consolidacao
        self.dias_tolerancia_avaliacao                   = dias_tolerancia_avaliacao
        self.dias_tolerancia_recurso_avaliacao           = dias_tolerancia_recurso_avaliacao
        self.nota_padrao_avaliacao                       = nota_padrao_avaliacao
        self.checklist_avaliacao_entregas_plano_entrega  = checklist_avaliacao_entregas_plano_entrega
        self.checklist_avaliacao_entregas_plano_trabalho = checklist_avaliacao_entregas_plano_trabalho
        self.registra_comparecimento                     = registra_comparecimento
        self.plano_trabalho_assinatura_participante      = plano_trabalho_assinatura_participante
        self.plano_trabalho_assinatura_gestor_lotacao    = plano_trabalho_assinatura_gestor_lotacao
        self.documento_id                                = documento_id
        self.tipo_documento_tcr_id                       = tipo_documento_tcr_id
        self.template_tcr_id                             = template_tcr_id
        self.unidade_id                                  = unidade_id
        self.tipo_justificativa_id                       = tipo_justificativa_id
        self.tipo_avaliacao_plano_entrega_id             = tipo_avaliacao_plano_entrega_id
        self.tipo_avaliacao_plano_trabalho_id            = tipo_avaliacao_plano_trabalho_id
        self.plano_trabalho_assinatura_gestor_entidade   = plano_trabalho_assinatura_gestor_entidade
        self.plano_trabalho_assinatura_gestor_unidade    = plano_trabalho_assinatura_gestor_unidade
        self.plano_trabalho_criterios_avaliacao          = plano_trabalho_criterios_avaliacao
        self.link_normativa                              = link_normativa
        

    def __repr__ (self):
        return f"{self.nome};{self.data_inicio};{self.data_fim}"
    
# programas_participantes (relação de regramentos com pessoas)

class programas_participantes(db.Model):

    __tablename__ = 'programas_participantes'
    # __table_args__ = {"schema": ""}

    id           = db.Column(db.String, primary_key = True)
    created_at   = db.Column(db.DateTime)
    updated_at   = db.Column(db.DateTime)
    deleted_at   = db.Column(db.DateTime)
    habilitado   = db.Column(db.Integer)
    programa_id  = db.Column(db.String)
    usuario_id   = db.Column(db.String)
    documento_id = db.Column(db.String)

    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , habilitado
                     , programa_id
                     , usuario_id
                     , documento_id):
         
        self.id           = id
        self.created_at   = created_at
        self.updated_at   = updated_at
        self.deleted_at   = deleted_at
        self.habilitado   = habilitado
        self.programa_id  = programa_id
        self.usuario_id   = usuario_id
        self.documento_id = documento_id 

    def __repr__ (self):
        return f"{self.habilitado}"

# Planos de Entregas

class planos_entregas(db.Model):

    __tablename__ = 'planos_entregas'
    # __table_args__ = {"schema": ""}

    id                  = db.Column(db.String, primary_key = True)
    created_at          = db.Column(db.DateTime)
    updated_at          = db.Column(db.DateTime)
    deleted_at          = db.Column(db.DateTime)
    numero              = db.Column(db.Integer)
    data_inicio         = db.Column(db.DateTime)
    data_fim            = db.Column(db.DateTime)
    data_arquivamento   = db.Column(db.DateTime) 
    nome                = db.Column(db.String)
    status              = db.Column(db.String)
    planejamento_id     = db.Column(db.String)
    cadeia_valor_id     = db.Column(db.String)
    unidade_id          = db.Column(db.String)
    plano_entrega_id    = db.Column(db.String)
    programa_id         = db.Column(db.String)
    criacao_usuario_id  = db.Column(db.String)
    avaliacao_id        = db.Column(db.String)
    okr_id              = db.Column(db.String)

    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , numero
                     , data_inicio
                     , data_fim
                     , data_arquivamento
                     , nome
                     , status
                     , planejamento_id
                     , cadeia_valor_id
                     , unidade_id
                     , plano_entrega_id
                     , programa_id
                     , criacao_usuario_id
                     , avaliacao_id
                     , okr_id):

        
        self.id                 = id
        self.created_at         = created_at
        self.updated_at         = updated_at
        self.deleted_at         = deleted_at
        self.numero             = numero
        self.data_arquivamento  = data_arquivamento
        self.data_inicio        = data_inicio
        self.data_fim           = data_fim 
        self.nome               = nome
        self.status             = status
        self.planejamento_id    = planejamento_id
        self.cadeia_valor_id    = cadeia_valor_id
        self.unidade_id         = unidade_id
        self.plano_entrega_id   = plano_entrega_id
        self.programa_id        = programa_id
        self.criacao_usuario_id = criacao_usuario_id
        self.avaliacao_id       = avaliacao_id
        self.okr_id             = okr_id
        
    def __repr__ (self):
        return f"{self.numero};{self.nome};{self.data_inicio};{self.data_fim};{self.status}"


# Avaliações

class avaliacoes(db.Model):

    __tablename__ = 'avaliacoes'
    # __table_args__ = {"schema": ""}

    id                             = db.Column(db.String, primary_key = True)
    created_at                     = db.Column(db.DateTime)
    updated_at                     = db.Column(db.DateTime)
    deleted_at                     = db.Column(db.DateTime)
    data_avaliacao                 = db.Column(db.DateTime)
    nota                           = db.Column(db.String)
    justificativa                  = db.Column(db.String)
    justificativas                 = db.Column(db.String)
    recurso                        = db.Column(db.String)
    avaliador_id                   = db.Column(db.String)
    plano_trabalho_consolidacao_id = db.Column(db.String)
    plano_entrega_id               = db.Column(db.String)
    tipo_avaliacao_id              = db.Column(db.String)
    tipo_avaliacao_nota_id         = db.Column(db.String)

    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , data_avaliacao
                     , nota
                     , justificativa
                     , justificativas
                     , recurso
                     , avaliador_id
                     , plano_trabalho_consolidacao_id
                     , plano_entrega_id
                     , tipo_avaliacao_id
                     , tipo_avaliacao_nota_id):

        self.id                             = id
        self.created_at                     = created_at
        self.updated_at                     = updated_at
        self.deleted_at                     = deleted_at
        self.data_avaliacao                 = data_avaliacao
        self.nota                           = nota
        self.justificativa                  = justificativa
        self.justificativas                 = justificativas
        self.recurso                        = recurso
        self.avaliador_id                   = avaliador_id
        self.plano_trabalho_consolidacao_id = plano_trabalho_consolidacao_id
        self.plano_entrega_id               = plano_entrega_id
        self.tipo_avaliacao_id              = tipo_avaliacao_id
        self.tipo_avaliacao_nota_id         = tipo_avaliacao_nota_id

    def __repr__ (self):
        return f"{self.data_avaliacao};{self.nota};{self.avaliador_id};{self.tipo_avaliacao_id}"             
                 
                 
# Entregas dos planos de entregas

class planos_entregas_entregas(db.Model):

    __tablename__ = 'planos_entregas_entregas'
    # __table_args__ = {"schema": ""}

    id                  = db.Column(db.String, primary_key = True)
    created_at          = db.Column(db.DateTime)
    updated_at          = db.Column(db.DateTime)
    deleted_at          = db.Column(db.DateTime)
    homologado          = db.Column(db.Integer)
    progresso_esperado  = db.Column(db.Integer)
    progresso_realizado = db.Column(db.Integer)
    data_inicio         = db.Column(db.DateTime)
    data_fim            = db.Column(db.DateTime)
    descricao           = db.Column(db.String)
    destinatario        = db.Column(db.String)
    meta                = db.Column(db.String)
    realizado           = db.Column(db.String)
    plano_entrega_id    = db.Column(db.String)
    entrega_id          = db.Column(db.String)
    entrega_pai_id      = db.Column(db.String)
    unidade_id          = db.Column(db.String)
    checklist           = db.Column(db.String)
    etiquetas           = db.Column(db.String)
    descricao_entrega   = db.Column(db.String)
    descricao_meta      = db.Column(db.String)

    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , homologado
                     , progresso_esperado
                     , progresso_realizado
                     , data_inicio
                     , data_fim
                     , descricao
                     , destinatario
                     , meta
                     , realizado
                     , plano_entrega_id
                     , entrega_id
                     , entrega_pai_id
                     , unidade_id
                     , checklist
                     , etiquetas
                     , descricao_meta
                     , descricao_entrega):

        self.id                  = id
        self.created_at          = created_at
        self.updated_at          = updated_at
        self.deleted_at          = deleted_at
        self.homologado          = homologado
        self.progresso_esperado  = progresso_esperado
        self.progresso_realizado = progresso_realizado
        self.data_inicio         = data_inicio
        self.data_fim            = data_fim
        self.descricao           = descricao
        self.destinatario        = destinatario
        self.meta                = meta
        self.realizado           = realizado
        self.plano_entrega_id    = plano_entrega_id
        self.entrega_id          = entrega_id
        self.entrega_pai_id      = entrega_pai_id
        self.unidade_id          = unidade_id
        self.checklist           = checklist
        self.etiquetas           = etiquetas
        self.descricao_entrega   = descricao_entrega
        self.descricao_meta      = descricao_meta

    def __repr__ (self):
        return f"{self.data_inicio};{self.data_fim};{self.meta};{self.descricao}"


# Planos de trabalho

class planos_trabalhos(db.Model):

    __tablename__ = 'planos_trabalhos'
    # __table_args__ = {"schema": ""}

    id                           = db.Column(db.String, primary_key = True)
    created_at                   = db.Column(db.DateTime)
    updated_at                   = db.Column(db.DateTime)
    deleted_at                   = db.Column(db.DateTime)
    carga_horaria                = db.Column(db.Float)
    tempo_total                  = db.Column(db.Float)
    tempo_proporcional           = db.Column(db.Float)
    numero                       = db.Column(db.Integer)
    data_inicio                  = db.Column(db.DateTime)
    data_fim                     = db.Column(db.DateTime)
    data_arquivamento            = db.Column(db.DateTime)
    forma_contagem_carga_horaria = db.Column(db.String)
    status                       = db.Column(db.String)
    programa_id                  = db.Column(db.String)
    usuario_id                   = db.Column(db.String)
    unidade_id                   = db.Column(db.String)
    tipo_modalidade_id           = db.Column(db.String)
    criacao_usuario_id           = db.Column(db.String)
    documento_id                 = db.Column(db.String)
    criterios_avaliacao          = db.Column(db.String)
    data_envio_api_pgd           = db.Column(db.DateTime)

    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , carga_horaria
                     , tempo_total
                     , tempo_proporcional
                     , numero
                     , data_inicio
                     , data_fim
                     , data_arquivamento
                     , forma_contagem_carga_horaria
                     , status
                     , programa_id
                     , usuario_id
                     , unidade_id
                     , tipo_modalidade_id
                     , criacao_usuario_id
                     , data_envio_api_pgd
                     , documento_id
                     , criterios_avaliacao):

        self.id                           = id
        self.created_at                   = created_at
        self.updated_at                   = updated_at
        self.deleted_at                   = deleted_at
        self.carga_horaria                = carga_horaria
        self.tempo_total                  = tempo_total
        self.tempo_proporcional           = tempo_proporcional
        self.numero                       = numero
        self.data_inicio                  = data_inicio
        self.data_fim                     = data_fim
        self.data_arquivamento            = data_arquivamento
        self.forma_contagem_carga_horaria = forma_contagem_carga_horaria
        self.status                       = status
        self.programa_id                  = programa_id
        self.usuario_id                   = usuario_id
        self.unidade_id                   = unidade_id
        self.tipo_modalidade_id           = tipo_modalidade_id
        self.criacao_usuario_id           = criacao_usuario_id
        self.data_envio_api_pgd           = data_envio_api_pgd
        self.documento_id                 = documento_id
        self.criterios_avaliacao          = criterios_avaliacao

    def __repr__ (self):
        return f"{self.numero};{self.data_inicio};{self.data_fim};{self.status}"

# Relação de Planos de trabalho com entregas

class planos_trabalhos_entregas(db.Model):

    __tablename__ = 'planos_trabalhos_entregas'
    # __table_args__ = {"schema": ""}

    id                       = db.Column(db.String, primary_key = True)
    created_at               = db.Column(db.DateTime)
    updated_at               = db.Column(db.DateTime)
    deleted_at               = db.Column(db.DateTime)
    forca_trabalho           = db.Column(db.Integer)  
    meta                     = db.Column(db.String)
    orgao                    = db.Column(db.String)
    descricao                = db.Column(db.String)
    plano_trabalho_id        = db.Column(db.String)
    plano_entrega_entrega_id = db.Column(db.String)
    
    def __init__(self, id
                     , created_at
                     , updated_at
                     , deleted_at
                     , forca_trabalho
                     , meta
                     , orgao
                     , descricao
                     , plano_trabalho_id
                     , plano_entrega_entrega_id):
        
        self.id                       = id
        self.created_at               = created_at
        self.updated_at               = updated_at
        self.deleted_at               = deleted_at
        self.forca_trabalho           = forca_trabalho
        self.meta                     = meta
        self.orgao                    = orgao
        self.descricao                = descricao
        self.plano_trabalho_id        = plano_trabalho_id
        self.plano_entrega_entrega_id = plano_entrega_entrega_id
        
    def __repr__ (self):
        return f"{self.plano_trabalho_id};{self.plano_entrega_entrega_id}"    


# planos_trabalhos_consolidacoes

class planos_trabalhos_consolidacoes(db.Model):

    __tablename__ = 'planos_trabalhos_consolidacoes'
    # __table_args__ = {"schema": ""}

    id                = db.Column(db.String, primary_key = True)
    created_at        = db.Column(db.DateTime)
    updated_at        = db.Column(db.DateTime)
    deleted_at        = db.Column(db.DateTime)
    data_inicio      = db.Column(db.DateTime)
    data_fim          = db.Column(db.DateTime)
    data_conclusao    = db.Column(db.DateTime)
    avaliacao_id      = db.Column(db.String)
    status            = db.Column(db.String)
    plano_trabalho_id = db.Column(db.String) 
    
    def __init__(self, id    
                     , created_at
                     , updated_at
                     , deleted_at
                     , data_inicio
                     , data_fim
                     , data_conclusao
                     , avaliacao_id
                     , status
                     , plano_trabalho_id):
        
        self.id                 = id
        self.created_at         = created_at
        self.updated_at         = updated_at
        self.deleted_at         = deleted_at
        self.data_inicio        = data_inicio
        self.data_fim           = data_fim
        self.data_conclusao     = data_conclusao
        self.avaliacao_id       = avaliacao_id
        self.status             = status
        self.plano_trabalho_id  = plano_trabalho_id
        
    def __repr__ (self):
            return f"{self.data_inicio};{self.data_fim};{self.status}"    


# atividades relacionada a planos de trabalho

class atividades(db.Model):

    __tablename__ = 'atividades'
    # __table_args__ = {"schema": ""}

    id                             = db.Column(db.String, primary_key = True)
    created_at                     = db.Column(db.DateTime)
    updated_at                     = db.Column(db.DateTime)
    deleted_at                     = db.Column(db.DateTime)
    numero                         = db.Column(db.Integer) 
    descricao                      = db.Column(db.String)
    data_distribuicao              = db.Column(db.DateTime)
    carga_horaria                  = db.Column(db.Float) 
    tempo_planejado                = db.Column(db.Float)
    data_estipulada_entrega        = db.Column(db.DateTime)
    data_inicio                    = db.Column(db.DateTime)
    data_entrega                   = db.Column(db.DateTime)
    esforco                        = db.Column(db.Float)
    tempo_despendido               = db.Column(db.Float)
    data_arquivamento              = db.Column(db.DateTime)
    etiquetas                      = db.Column(db.String)
    checklist                      = db.Column(db.String)
    prioridade                     = db.Column(db.Integer)
    progresso                      = db.Column(db.Float)
    status                         = db.Column(db.String)
    plano_trabalho_id              = db.Column(db.String)
    plano_trabalho_entrega_id      = db.Column(db.String)
    plano_trabalho_consolidacao_id = db.Column(db.String)
    tipo_atividade_id              = db.Column(db.String)
    demandante_id                  = db.Column(db.String)
    usuario_id                     = db.Column(db.String)
    unidade_id                     = db.Column(db.String)
    documento_requisicao_id        = db.Column(db.String)
    documento_entrega_id           = db.Column(db.String)

    def __init__(self, id    
                     , created_at
                     , updated_at
                     , deleted_at
                     , numero
                     , descricao
                     , data_distribuicao
                     , carga_horaria
                     , tempo_planejado
                     , data_estipulada_entrega
                     , data_inicio
                     , data_entrega
                     , esforco
                     , tempo_despendido
                     , data_arquivamento
                     , etiquetas
                     , checklist
                     , prioridade
                     , progresso
                     , status
                     , plano_trabalho_id
                     , plano_trabalho_entrega_id
                     , plano_trabalho_consolidacao_id
                     , documento_entrega_id
                     , documento_requisicao_id
                     , unidade_id
                     , usuario_id
                     , tipo_atividade_id
                     , demandante_id):
                     
        self.id                             = id
        self.created_at                     = created_at
        self.updated_at                     = updated_at
        self.deleted_at                     = deleted_at 
        self.numero                         = numero 
        self.descricao                      = descricao
        self.data_distribuicao              = data_distribuicao
        self.carga_horaria                  = carga_horaria 
        self.tempo_planejado                = tempo_planejado
        self.data_estipulada_entrega        = data_estipulada_entrega
        self.data_inicio                    = data_inicio
        self.data_entrega                   = data_entrega 
        self.esforco                        = esforco
        self.tempo_despendido               = tempo_despendido
        self.data_arquivamento              = data_arquivamento
        self.etiquetas                      = etiquetas
        self.checklist                      = checklist
        self.prioridade                     = prioridade
        self.progresso                      = progresso
        self.status                         = status
        self.plano_trabalho_id              = plano_trabalho_id
        self.plano_trabalho_entrega_id      = plano_trabalho_entrega_id
        self.plano_trabalho_consolidacao_id = plano_trabalho_consolidacao_id
        self.tipo_atividade_id              = tipo_atividade_id
        self.demandante_id                  = demandante_id
        self.usuario_id                     = usuario_id
        self.unidade_id                     = unidade_id
        self.documento_requisicao_id        = documento_requisicao_id
        self.documento_entrega_id           = documento_entrega_id                


    def __repr__ (self):
            return f"{self.descricao};{self.data_inicio};{self.data_entrega};{self.status}"

                              
class envio_itens(db.Model):

    __tablename__ = 'envio_itens'

    id          = db.Column(db.String, primary_key = True)
    created_at  = db.Column(db.DateTime)
    updated_at  = db.Column(db.DateTime)
    deleted_at  = db.Column(db.DateTime)
    envio_id    = db.Column(db.String)
    tipo        = db.Column(db.String)
    uid         = db.Column(db.String)
    fonte       = db.Column(db.Integer)
    sucesso     = db.Column(db.Integer)
    erros       = db.Column(db.String)


    def __init__(self, id    
                     , created_at
                     , updated_at
                     , deleted_at
                     , envio_id
                     , tipo
                     , uid
                     , fonte
                     , sucesso
                     , erros):

        self.id         = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.envio_id   = envio_id
        self.tipo       = tipo
        self.uid        = uid
        self.fonte      = fonte
        self.sucesso    = sucesso
        self.erros      = erros

    def __repr__(self):

        return f"{self.uid};{self.tipo};{self.erros}"                              
