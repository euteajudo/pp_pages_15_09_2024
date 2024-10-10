import streamlit as st

# Lista de colunas a serem removidas
COLUNAS_PARA_REMOVER = [
    "idItemCompra",
    "forma",
    "criterioJulgamento",
    "dataHoraAtualizacaoUasg",
    "dataHoraAtualizacaoCompra",
    "dataHoraAtualizacaoItem",
    "nomeUnidadeMedida",
    "siglaUnidadeMedida",
    "nomeUnidadeFornecimento",
    "percentualMaiorDesconto",
    "codigoMunicipio",
    "codigoOrgao",
    # Adicione aqui outras colunas que deseja remover
]

# Configuração das colunas do dataframe
COLUMN_CONFIG = {
    "precoUnitario": st.column_config.NumberColumn(
        "Preço Unitário",
        help="Preço unitário do item",
        min_value=0,
        format="R$ %.2f",
    ),
    "numeroItemCompra": st.column_config.NumberColumn(
        "Número do Item",
        help="Número do item na compra",
        min_value=1,
        step=1,
    ),
    "modalidade": st.column_config.TextColumn(
        "Modalidade",
        help="Modalidade da compra",
    ),
    "idCompra": st.column_config.TextColumn(
        "ID da Compra",
        help="Identificador único da compra",
    ),
    "descricaoItem": st.column_config.TextColumn(
        "Descrição",
        help="Descrição detalhada do item",
    ),
    "codigoItemCatalogo": st.column_config.NumberColumn(
        "CATMAT",
        help="Código do item no catálogo de materiais",
        min_value=0,
        step=1,
    ),
    "siglaUnidadeFornecimento": st.column_config.TextColumn(
        "Unidade de Medida",
        help="Sigla da unidade de fornecimento",
    ),
    "capacidadeUnidadeFornecimento": st.column_config.TextColumn(
        "Capacidade",
        help="Capacidade da unidade de fornecimento",
    ),
    "niFornecedor": st.column_config.NumberColumn(
        "CNPJ",
        help="CNPJ do fornecedor",
        min_value=0,
        format="%d",
    ),
    "nomeFornecedor": st.column_config.TextColumn(
        "Fornecedor",
        help="Nome do fornecedor",
    ),
    "dataCompra": st.column_config.DateColumn(
        "Data da Compra",
        help="Data em que a compra foi realizada",
    ),
    "dataResultado": st.column_config.DateColumn(
        "Data do Resultado",
        help="Data do resultado da compra",
    ),
    "quantidade": st.column_config.NumberColumn(
        "Quantidade",
        help="Quantidade do item comprado",
        min_value=0,
        step=1,
    ),
    "marca": st.column_config.TextColumn(
        "Marca",
        help="Marca do produto",
    ),
    "codigoUasg": st.column_config.TextColumn(
        "UASG",
        help="Código da Unidade Administrativa de Serviços Gerais",
    ),
    "nomeUasg": st.column_config.TextColumn(
        "Nome do órgão",
        help="Nome da Unidade Administrativa de Serviços Gerais",
    ),
    "municipio": st.column_config.TextColumn(
        "Município",
        help="Município onde a compra foi realizada",
    ),
    "estado": st.column_config.TextColumn(
        "Estado",
        help="Estado onde a compra foi realizada",
    ),
    "nomeOrgao": st.column_config.TextColumn(
        "Nome da Entidade",
        help="Nome completo do órgão responsável pela compra",
    ),
    "poder": st.column_config.TextColumn(
        "Poder",
        help="Poder ao qual o órgão pertence",
    ),
    "esfera": st.column_config.TextColumn(
        "Esfera",
        help="Esfera administrativa do órgão",
    ),
}

# Função para obter a configuração de uma coluna específica
def get_column_config(column_name):
    return COLUMN_CONFIG.get(column_name, st.column_config.TextColumn(column_name))

# Função para obter o nome amigável de uma coluna
def get_friendly_name(column_name):
    config = COLUMN_CONFIG.get(column_name)
    return config.label if config else column_name.replace('_', ' ').title()