# Consultas SQL do Sistema ApoioPet

Este documento lista todas as consultas SQL realizadas pelo sistema ApoioPet, organizadas por módulo e funcionalidade.

## Índice

- [1. Módulo Planejamento](#1-módulo-planejamento)
- [2. Módulo Pessoas](#2-módulo-pessoas)
- [3. Módulo Unidades](#3-módulo-unidades)
- [4. Módulo Entregas](#4-módulo-entregas)
- [5. Módulo Trabalhos](#5-módulo-trabalhos)
- [6. Módulo Envios](#6-módulo-envios)

---

## 1. Módulo Planejamento

### 1.1 Consulta Planejamento Vigente
**Arquivo:** `project/planejamento/views.py`  
**Função:** `mapa_estrategico()`  
**Descrição:** Busca o planejamento institucional vigente na data atual

```sql
SELECT 
    planejamentos.id,
    planejamentos.nome,
    planejamentos.missao,
    planejamentos.visao,
    planejamentos.data_inicio,
    planejamentos.data_fim,
    unidades.sigla,
    planejamentos.valores,
    planejamentos.resultados_institucionais
FROM planejamentos 
JOIN unidades ON unidades.id = planejamentos.unidade_id
WHERE planejamentos.deleted_at IS NULL
  AND planejamentos.data_inicio <= CURRENT_DATE
  AND planejamentos.data_fim >= CURRENT_DATE;
```

### 1.2 Consulta Objetivos por Eixo Temático
**Arquivo:** `project/planejamento/views.py`  
**Função:** `mapa_estrategico()`  
**Descrição:** Busca objetivos do planejamento agrupados por eixo temático

```sql
SELECT 
    planejamentos_objetivos.id,
    planejamentos_objetivos.planejamento_id,
    planejamentos_objetivos.nome,
    planejamentos_objetivos.fundamentacao,
    planejamentos_objetivos.eixo_tematico_id,
    eixos_tematicos.nome AS eixo_nome,
    eixos_tematicos.cor AS eixo_cor,
    eixos_tematicos.descricao AS eixo_desc
FROM planejamentos_objetivos
JOIN eixos_tematicos ON eixos_tematicos.id = planejamentos_objetivos.eixo_tematico_id
WHERE planejamentos_objetivos.planejamento_id = ?
ORDER BY planejamentos_objetivos.nome;
```

---

## 2. Módulo Pessoas

### 2.1 Lista Geral de Pessoas
**Arquivo:** `project/pessoas/views.py`  
**Função:** `lista_pessoas()`  
**Descrição:** Lista todas as pessoas com informações básicas e contagem de planos de trabalho

```sql
SELECT 
    usuarios.id,
    usuarios.nome,
    usuarios.cpf,
    usuarios.data_nascimento,
    usuarios.matricula,
    usuarios.email,
    unidades.sigla,
    unidades_integrantes_atribuicoes.atribuicao,
    usuarios.situacao_funcional,
    perfis.nome AS perfil,
    COUNT(DISTINCT planos_trabalhos.id) AS qtd_planos_trab
FROM usuarios
LEFT JOIN unidades_integrantes ON unidades_integrantes.usuario_id = usuarios.id
LEFT JOIN unidades_integrantes_atribuicoes ON unidades_integrantes_atribuicoes.unidade_integrante_id = unidades_integrantes.id
LEFT JOIN unidades ON unidades.id = unidades_integrantes.unidade_id
JOIN perfis ON perfis.id = usuarios.perfil_id
LEFT JOIN planos_trabalhos ON planos_trabalhos.usuario_id = usuarios.id
WHERE usuarios.deleted_at IS NULL
GROUP BY usuarios.id, unidades.sigla, unidades_integrantes_atribuicoes.atribuicao
ORDER BY usuarios.nome;
```

### 2.2 Busca de Pessoas com Filtros
**Arquivo:** `project/pessoas/views.py`  
**Função:** `lista_pessoas_filtro()`  
**Descrição:** Busca pessoas aplicando filtros por nome, unidade, situação, perfil e atribuição

```sql
SELECT 
    usuarios.id,
    usuarios.nome,
    usuarios.cpf,
    usuarios.data_nascimento,
    usuarios.matricula,
    usuarios.email,
    unidades.sigla,
    unidades_integrantes_atribuicoes.atribuicao,
    usuarios.situacao_funcional,
    perfis.nome AS perfil,
    perfis.id AS perfil_id,
    COUNT(DISTINCT planos_trabalhos.id) AS qtd_planos_trab
FROM usuarios
LEFT JOIN unidades_integrantes ON unidades_integrantes.usuario_id = usuarios.id
LEFT JOIN unidades_integrantes_atribuicoes ON unidades_integrantes_atribuicoes.unidade_integrante_id = unidades_integrantes.id
LEFT JOIN unidades ON unidades.id = unidades_integrantes.unidade_id
JOIN perfis ON perfis.id = usuarios.perfil_id
LEFT JOIN planos_trabalhos ON planos_trabalhos.usuario_id = usuarios.id
WHERE usuarios.deleted_at IS NULL
  AND usuarios.nome LIKE ?
  AND unidades.id LIKE ?
  AND usuarios.situacao_funcional LIKE ?
  AND perfis.id LIKE ?
  AND unidades_integrantes_atribuicoes.atribuicao LIKE ?
GROUP BY usuarios.id, unidades.sigla, unidades_integrantes_atribuicoes.atribuicao
ORDER BY usuarios.nome;
```

### 2.3 Consulta Planos de Trabalho por Pessoa
**Arquivo:** `project/pessoas/views.py`  
**Função:** `consulta_pts_pessoa()`  
**Descrição:** Lista todos os planos de trabalho de uma pessoa específica

```sql
-- Subquery para contar avaliações
SELECT 
    planos_trabalhos_consolidacoes.plano_trabalho_id,
    COUNT(avaliacoes.id) AS qtd_aval
FROM planos_trabalhos_consolidacoes
JOIN avaliacoes ON avaliacoes.plano_trabalho_consolidacao_id = planos_trabalhos_consolidacoes.id
GROUP BY planos_trabalhos_consolidacoes.plano_trabalho_id;

-- Query principal
SELECT DISTINCT
    planos_trabalhos.id AS pt_id,
    planos_trabalhos.data_inicio,
    planos_trabalhos.data_fim,
    planos_trabalhos.carga_horaria,
    planos_trabalhos.forma_contagem_carga_horaria,
    planos_trabalhos.status,
    usuarios.nome,
    unidades.sigla,
    tipos_modalidades.nome AS forma,
    avaliacoes_pt.qtd_aval
FROM planos_trabalhos
JOIN usuarios ON usuarios.id = planos_trabalhos.usuario_id
LEFT JOIN planos_trabalhos_entregas ON planos_trabalhos_entregas.plano_trabalho_id = planos_trabalhos.id
LEFT JOIN planos_entregas_entregas ON planos_entregas_entregas.id = planos_trabalhos_entregas.plano_entrega_entrega_id
LEFT JOIN unidades ON unidades.id = planos_trabalhos.unidade_id
LEFT JOIN tipos_modalidades ON tipos_modalidades.id = planos_trabalhos.tipo_modalidade_id
LEFT JOIN avaliacoes_pt ON avaliacoes_pt.plano_trabalho_id = planos_trabalhos.id
WHERE planos_trabalhos.usuario_id = ?
ORDER BY planos_trabalhos.data_inicio;
```

### 2.4 Consultas Auxiliares - Pessoas
**Descrição:** Consultas para popular listas de seleção nos formulários

```sql
-- Busca unidades para filtro
SELECT DISTINCT sigla FROM unidades 
WHERE deleted_at IS NULL 
ORDER BY sigla;

-- Busca perfis para filtro
SELECT id, nome FROM perfis 
ORDER BY nome;

-- Busca situações funcionais distintas
SELECT DISTINCT situacao_funcional AS situ 
FROM usuarios 
ORDER BY situacao_funcional;

-- Busca atribuições distintas
SELECT DISTINCT atribuicao AS atrib 
FROM unidades_integrantes_atribuicoes 
ORDER BY atribuicao;
```

---

## 3. Módulo Unidades

### 3.1 Lista Geral de Unidades
**Arquivo:** `project/unidades/views.py`  
**Função:** `lista_unidades()`  
**Descrição:** Lista todas as unidades com informações de gestores

```sql
-- Subqueries para gestores
SELECT 
    pessoas.id,
    pessoas.nome,
    unidades_integrantes.unidade_id,
    unidades_integrantes_atribuicoes.atribuicao
FROM pessoas
JOIN unidades_integrantes ON unidades_integrantes.usuario_id = pessoas.id
JOIN unidades_integrantes_atribuicoes ON unidades_integrantes_atribuicoes.unidade_integrante_id = unidades_integrantes.id
WHERE unidades_integrantes_atribuicoes.deleted_at IS NULL
  AND unidades_integrantes_atribuicoes.atribuicao = 'GESTOR';

-- Query principal das unidades
SELECT 
    unidades.id,
    unidades.sigla,
    unidades.nome,
    unidades.unidade_pai_id,
    cidades.uf,
    unidades.path,
    unidades.codigo,
    chefes_s.nome AS titular,
    COUNT(DISTINCT substitutos_s.nome) AS substituto,
    COUNT(DISTINCT delegados_s.nome) AS delegado
FROM unidades
LEFT JOIN cidades ON cidades.id = unidades.cidade_id
LEFT JOIN chefes_s ON chefes_s.unidade_id = unidades.id
LEFT JOIN substitutos_s ON substitutos_s.unidade_id = unidades.id
LEFT JOIN delegados_s ON delegados_s.unidade_id = unidades.id
WHERE unidades.deleted_at IS NULL
GROUP BY unidades.id, chefes_s.nome
ORDER BY unidades.sigla;
```

### 3.2 Busca de Unidades com Filtros
**Arquivo:** `project/unidades/views.py`  
**Função:** `lista_unidades_filtro()`  
**Descrição:** Busca unidades aplicando filtros por sigla, unidade pai, nome e UF

```sql
SELECT 
    unidades.id,
    unidades.sigla,
    unidades.nome,
    unidades.unidade_pai_id,
    cidades.uf,
    unidades.path,
    unidades.codigo,
    chefes_s.nome AS titular,
    COUNT(DISTINCT substitutos_s.nome) AS substituto,
    COUNT(DISTINCT delegados_s.nome) AS delegado
FROM unidades
LEFT JOIN cidades ON cidades.id = unidades.cidade_id
LEFT JOIN chefes_s ON chefes_s.unidade_id = unidades.id
LEFT JOIN substitutos_s ON substitutos_s.unidade_id = unidades.id
LEFT JOIN delegados_s ON delegados_s.unidade_id = unidades.id
WHERE unidades.sigla LIKE ?
  AND unidades.unidade_pai_id LIKE ?
  AND unidades.nome LIKE ?
  AND cidades.uf LIKE ?
GROUP BY unidades.id, chefes_s.nome
ORDER BY unidades.sigla;
```

### 3.3 Consulta Hierarquia de Unidades
**Arquivo:** `project/unidades/views.py`  
**Função:** `lista_unidades()`  
**Descrição:** Constrói a hierarquia organizacional das unidades

```sql
SELECT path, sigla, id 
FROM unidades;

-- Para cada unidade, busca a sigla das unidades pais
SELECT sigla 
FROM unidades 
WHERE id = ?;
```

---

## 4. Módulo Entregas

### 4.1 Lista Geral de Planos de Entrega
**Arquivo:** `project/entregas/views.py`  
**Função:** `lista_pe()`  
**Descrição:** Lista todos os planos de entrega com estatísticas

```sql
-- Subquery para contar entregas por plano
SELECT 
    plano_entrega_id,
    COUNT(id) AS qtd_entregas
FROM planos_entregas_entregas
GROUP BY plano_entrega_id;

-- Subquery para contar planos de trabalho vinculados
SELECT DISTINCT 
    planos_trabalhos_entregas.plano_trabalho_id AS pt_id,
    planos_trabalhos_entregas.plano_entrega_entrega_id,
    planos_entregas_entregas.plano_entrega_id
FROM planos_trabalhos_entregas
JOIN planos_entregas_entregas ON planos_entregas_entregas.id = planos_trabalhos_entregas.plano_entrega_entrega_id;

-- Query principal dos planos de entrega
SELECT 
    planos_entregas.id,
    planos_entregas.status,
    planos_entregas.data_inicio,
    planos_entregas.data_fim,
    planos_entregas.deleted_at,
    entregas.qtd_entregas,
    planos_trab.qtd_planos_trab,
    unidades.sigla,
    unidades_pai.sigla AS sigla_pai,
    planos_entregas.unidade_id,
    unidades.unidade_pai_id,
    CASE WHEN planos_entregas.data_fim < CURRENT_DATE THEN 's' ELSE 'n' END AS vencido,
    avaliacoes.nota,
    avaliacoes.data_avaliacao,
    avaliacoes.justificativas AS just_avalia,
    avaliacoes.justificativa AS parecer_avalia
FROM planos_entregas
JOIN unidades ON unidades.id = planos_entregas.unidade_id
LEFT JOIN unidades AS unidades_pai ON unidades_pai.id = unidades.unidade_pai_id
LEFT JOIN entregas ON entregas.plano_entrega_id = planos_entregas.id
LEFT JOIN planos_trab ON planos_trab.pe_id = planos_entregas.id
LEFT JOIN avaliacoes ON avaliacoes.plano_entrega_id = planos_entregas.id
WHERE planos_entregas.deleted_at IS NULL
ORDER BY planos_entregas.status, unidades.sigla, planos_entregas.data_inicio;
```

### 4.2 Consulta Entregas de um Plano de Entrega
**Arquivo:** `project/entregas/views.py`  
**Função:** `consulta_entregas()`  
**Descrição:** Lista as entregas de um plano de entrega específico

```sql
-- Dados do plano de entrega
SELECT 
    planos_entregas.status,
    planos_entregas.data_inicio,
    planos_entregas.data_fim,
    unidades.sigla
FROM planos_entregas
JOIN unidades ON unidades.id = planos_entregas.unidade_id
WHERE planos_entregas.id = ?;

-- Entregas do plano
SELECT * 
FROM planos_entregas_entregas 
WHERE plano_entrega_id = ?;
```

### 4.3 Consulta Planos de Trabalho por Plano de Entrega
**Arquivo:** `project/entregas/views.py`  
**Função:** `consulta_pts()`  
**Descrição:** Lista os planos de trabalho vinculados a um plano de entrega

```sql
-- Subquery para contar avaliações
SELECT 
    planos_trabalhos_consolidacoes.plano_trabalho_id,
    COUNT(avaliacoes.id) AS qtd_aval
FROM planos_trabalhos_consolidacoes
JOIN avaliacoes ON avaliacoes.plano_trabalho_consolidacao_id = planos_trabalhos_consolidacoes.id
GROUP BY planos_trabalhos_consolidacoes.plano_trabalho_id;

-- Query principal dos planos de trabalho
SELECT DISTINCT
    planos_trabalhos.id,
    planos_trabalhos.data_inicio,
    planos_trabalhos.data_fim,
    planos_trabalhos.carga_horaria,
    planos_trabalhos.forma_contagem_carga_horaria,
    planos_trabalhos.status,
    planos_trabalhos.tempo_total,
    planos_trabalhos.tempo_proporcional,
    planos_trabalhos_entregas.plano_trabalho_id,
    planos_entregas_entregas.plano_entrega_id,
    pessoas.nome,
    unidades.sigla,
    tipos_modalidades.nome AS forma,
    avaliacoes_pt.qtd_aval
FROM planos_trabalhos
JOIN usuarios ON usuarios.id = planos_trabalhos.usuario_id
JOIN planos_trabalhos_entregas ON planos_trabalhos_entregas.plano_trabalho_id = planos_trabalhos.id
JOIN planos_entregas_entregas ON planos_entregas_entregas.id = planos_trabalhos_entregas.plano_entrega_entrega_id
JOIN unidades ON unidades.id = planos_trabalhos.unidade_id
JOIN tipos_modalidades ON tipos_modalidades.id = planos_trabalhos.tipo_modalidade_id
LEFT JOIN avaliacoes_pt ON avaliacoes_pt.plano_trabalho_id = planos_trabalhos.id
WHERE planos_entregas_entregas.plano_entrega_id = ?
ORDER BY usuarios.nome;
```

---

## 5. Módulo Trabalhos

### 5.1 Lista Geral de Planos de Trabalho
**Arquivo:** `project/trabalhos/views.py`  
**Função:** `lista_pts()`  
**Descrição:** Lista todos os planos de trabalho com estatísticas

```sql
-- Subquery para contar trabalhos (atividades) por plano
SELECT 
    plano_trabalho_id,
    COUNT(id) AS qtd_trabalhos
FROM atividades
WHERE deleted_at IS NULL
GROUP BY plano_trabalho_id;

-- Subquery para contar avaliações por plano
SELECT 
    planos_trabalhos_consolidacoes.plano_trabalho_id,
    COUNT(avaliacoes.id) AS qtd_aval
FROM planos_trabalhos_consolidacoes
JOIN avaliacoes ON avaliacoes.plano_trabalho_consolidacao_id = planos_trabalhos_consolidacoes.id
WHERE avaliacoes.data_avaliacao <= CURRENT_DATE
GROUP BY planos_trabalhos_consolidacoes.plano_trabalho_id;

-- Query principal dos planos de trabalho
SELECT 
    planos_trabalhos.id,
    planos_trabalhos.data_inicio,
    planos_trabalhos.data_fim,
    planos_trabalhos.carga_horaria,
    planos_trabalhos.forma_contagem_carga_horaria,
    planos_trabalhos.status,
    tipos_modalidades.nome AS forma,
    planos_trabalhos.data_envio_api_pgd,
    usuarios.nome,
    unidades.sigla,
    planos_trabalhos.status AS situacao,
    CASE WHEN planos_trabalhos.data_fim < CURRENT_DATE THEN 's' ELSE 'n' END AS vencido,
    trabalhos.qtd_trabalhos,
    avaliacoes_pt.qtd_aval
FROM planos_trabalhos
JOIN usuarios ON usuarios.id = planos_trabalhos.usuario_id
JOIN unidades ON unidades.id = planos_trabalhos.unidade_id
JOIN tipos_modalidades ON tipos_modalidades.id = planos_trabalhos.tipo_modalidade_id
LEFT JOIN trabalhos ON trabalhos.plano_trabalho_id = planos_trabalhos.id
LEFT JOIN avaliacoes_pt ON avaliacoes_pt.plano_trabalho_id = planos_trabalhos.id
WHERE planos_trabalhos.deleted_at IS NULL
  AND planos_trabalhos.status LIKE ?
ORDER BY planos_trabalhos.status, unidades.sigla, usuarios.nome, planos_trabalhos.data_inicio;
```

### 5.2 Consulta Trabalhos (Atividades) de um Plano
**Arquivo:** `project/trabalhos/views.py`  
**Função:** `consulta_trabalhos()`  
**Descrição:** Lista os trabalhos/atividades de um plano de trabalho específico

```sql
SELECT 
    atividades.descricao,
    planos_entregas_entregas.descricao AS entrega,
    atividades.status,
    atividades.carga_horaria,
    atividades.progresso,
    atividades.data_inicio,
    atividades.data_entrega
FROM atividades
LEFT JOIN planos_trabalhos_entregas ON planos_trabalhos_entregas.id = atividades.plano_trabalho_entrega_id
LEFT JOIN planos_entregas_entregas ON planos_entregas_entregas.id = planos_trabalhos_entregas.plano_entrega_entrega_id
WHERE atividades.deleted_at IS NULL
  AND atividades.plano_trabalho_id = ?;
```

### 5.3 Consulta Avaliações de um Plano de Trabalho
**Arquivo:** `project/trabalhos/views.py`  
**Função:** `consulta_avaliacoes()`  
**Descrição:** Lista as avaliações realizadas em um plano de trabalho

```sql
SELECT 
    planos_trabalhos_consolidacoes.plano_trabalho_id,
    avaliacoes.data_avaliacao,
    avaliacoes.nota,
    pessoas.nome AS avaliador,
    avaliados.nome AS avaliado,
    planos_trabalhos.data_inicio,
    planos_trabalhos.data_fim,
    avaliacoes.recurso
FROM planos_trabalhos_consolidacoes
JOIN avaliacoes ON avaliacoes.plano_trabalho_consolidacao_id = planos_trabalhos_consolidacoes.id
JOIN planos_trabalhos ON planos_trabalhos.id = planos_trabalhos_consolidacoes.plano_trabalho_id
LEFT JOIN usuarios AS pessoas ON pessoas.id = avaliacoes.avaliador_id
JOIN usuarios AS avaliados ON avaliados.id = planos_trabalhos.usuario_id
WHERE avaliacoes.data_avaliacao <= CURRENT_DATE
  AND avaliacoes.deleted_at IS NULL
  AND planos_trabalhos_consolidacoes.plano_trabalho_id = ?;
```

---

## 6. Módulo Envios

### 6.1 Envios Mal Sucedidos - Planos de Entrega
**Arquivo:** `project/envios/views.py`  
**Função:** `envios_insucesso_pe()`  
**Descrição:** Lista planos de entrega com falha no envio

```sql
SELECT 
    envio_itens.id,
    envio_itens.tipo,
    envio_itens.uid,
    envio_itens.sucesso,
    envio_itens.erros,
    envio_itens.created_at,
    planos_entregas.nome,
    planos_entregas.status
FROM envio_itens
LEFT JOIN planos_entregas ON planos_entregas.id = envio_itens.uid
WHERE envio_itens.sucesso = 0
  AND envio_itens.tipo = 'entrega'
ORDER BY CAST(envio_itens.created_at AS DATE) DESC, planos_entregas.nome;
```

### 6.2 Envios Mal Sucedidos - Planos de Trabalho
**Arquivo:** `project/envios/views.py`  
**Função:** `envios_insucesso_pt()`  
**Descrição:** Lista planos de trabalho com falha no envio

```sql
SELECT 
    envio_itens.id,
    envio_itens.tipo,
    envio_itens.uid,
    envio_itens.sucesso,
    envio_itens.erros,
    envio_itens.created_at,
    planos_trabalhos.numero,
    usuarios.nome AS pt_dono,
    planos_trabalhos.status AS status_pt
FROM envio_itens
LEFT JOIN planos_trabalhos ON planos_trabalhos.id = envio_itens.uid
LEFT JOIN usuarios ON usuarios.id = planos_trabalhos.usuario_id
WHERE envio_itens.sucesso = 0
  AND envio_itens.tipo = 'trabalho'
ORDER BY CAST(envio_itens.created_at AS DATE) DESC, usuarios.nome;
```

### 6.3 Envios Mal Sucedidos - Participantes
**Arquivo:** `project/envios/views.py`  
**Função:** `envios_insucesso_par()`  
**Descrição:** Lista participantes com falha no envio

```sql
SELECT 
    envio_itens.id,
    envio_itens.tipo,
    envio_itens.uid,
    envio_itens.sucesso,
    envio_itens.erros,
    envio_itens.created_at,
    usuarios.nome AS participante_nome,
    usuarios.matricula
FROM envio_itens
LEFT JOIN usuarios ON usuarios.id = envio_itens.uid
WHERE envio_itens.sucesso = 0
  AND envio_itens.tipo = 'participante'
ORDER BY CAST(envio_itens.created_at AS DATE) DESC, usuarios.nome;
```

---

## Observações Técnicas

### Convenções Utilizadas
- **Soft Delete**: Todas as tabelas principais utilizam o campo `deleted_at` para exclusão lógica
- **UUIDs**: As chaves primárias são strings (UUIDs) em vez de inteiros
- **Timestamps**: Campos `created_at` e `updated_at` para auditoria
- **Relacionamentos**: Uso extensivo de JOINs e LEFT JOINs para relacionar dados

### Otimizações Implementadas
- **Subqueries**: Uso de subqueries para contagens e cálculos complexos
- **Paginação**: Implementada em listas com muitos registros (SQLAlchemy paginate)
- **Índices**: Recomendado criar índices nos campos mais consultados (id, deleted_at, datas)

### Principais Tabelas do Sistema
- `usuarios` - Usuários/servidores do sistema
- `unidades` - Estrutura organizacional
- `planos_entregas` - Planos de entrega institucionais
- `planos_trabalhos` - Planos de trabalho individuais
- `planos_entregas_entregas` - Entregas específicas dos planos
- `atividades` - Atividades/trabalhos realizados
- `avaliacoes` - Avaliações dos planos de trabalho
- `envio_itens` - Log de envios para sistemas externos

---

*Documento gerado automaticamente baseado na análise do código fonte do sistema ApoioPet.*