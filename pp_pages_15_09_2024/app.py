import streamlit as st
import pandas as pd
import os
import sys
from dotenv import load_dotenv
from utils.config import COLUMN_CONFIG, get_column_config
from utils.utils import aplicar_mascara, calcular_estatisticas
from utils.apis import consultar_api_governo_async
from agents_tools.ag_to import criar_agente_dataframe, get_or_create_agent, update_agent
import time
import asyncio
import plotly.express as px
import numpy as np
import altair as alt

# Adicionar o diretório pai ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def limpar_e_converter(valor):
    if isinstance(valor, str):
        # Remove caracteres não numéricos, exceto ponto e vírgula
        valor = ''.join(c for c in valor if c.isdigit() or c in ['.', ','])
        # Substitui vírgula por ponto
        valor = valor.replace(',', '.')
    try:
        return float(valor)
    except ValueError:
        return None

# Configuração da página
st.set_page_config(
    page_title="Pesquisa de Preços",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar variáveis de ambiente
load_dotenv()

# Configurar a chave da API
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configuração do Streamlit
st.title("Pesquisa de Preços")

# Inicialização do estado da conversa
if "messages" not in st.session_state:
    st.session_state.messages = []
if "df" not in st.session_state:
    st.session_state.df = None
if "tempos_resposta" not in st.session_state:
    st.session_state.tempos_resposta = []
if "progress_bar" not in st.session_state:
    st.session_state.progress_bar = st.progress(0)

# Função para limpar os dados e reiniciar a aplicação
def limpar_dados():
    st.session_state.df = None
    st.session_state.tempos_resposta = []
    st.session_state.messages = []
    if "agent" in st.session_state:
        del st.session_state.agent
    st.session_state.agent = None  # Garante que o agente seja None após a limpeza

# Sidebar para input de parâmetros, seleção de modelo e botão de limpar histórico
with st.sidebar:
    st.header("Parâmetros de Consulta")
    codigo_item = st.text_input("Código do Item")
    data_inicial = st.date_input("Data Inicial")
    data_final = st.date_input("Data Final")
    st.session_state.model_choice = st.selectbox("Escolha o Modelo", ["gpt-3.5-turbo-0125", "gpt-4o", "gpt-4o-mini"])
    
    if st.button("Buscar Dados"):
        with st.spinner("Buscando dados..."):
            try:
                resultados = asyncio.run(consultar_api_governo_async(codigo_item, data_inicial.strftime("%Y-%m-%d"), data_final.strftime("%Y-%m-%d")))
                if resultados['df'] is not None and not resultados['df'].empty:
                    st.session_state.df = resultados['df']
                    st.session_state.total_registros = resultados['total_registros']
                    st.session_state.total_paginas = resultados['total_paginas']
                    
                    tempo_resposta = time.time() - time.time()
                    st.session_state.tempos_resposta.append(tempo_resposta)
                    
                    st.success(f"Dados carregados com sucesso! Total de registros: {st.session_state.total_registros}")
                else:
                    st.warning("Não foram encontrados dados para os parâmetros fornecidos.")
            except Exception as e:
                st.error(f"Erro ao buscar dados: {str(e)}")
    
    if st.button("Limpar Dados"):
        limpar_dados()
        if "df" in st.session_state and isinstance(st.session_state.df, pd.DataFrame):
            update_agent(st.session_state.df, st.session_state.model_choice)
        st.success("Dados limpos e agente atualizado com sucesso!")

# Criação das tabs
tab1, tab2, tab3 = st.tabs(["Dados", "Parâmetros", "Gráficos"])

# Função para obter o nome amigável de uma coluna
def get_friendly_name(col):
    config = COLUMN_CONFIG.get(col, {})
    if isinstance(config, dict) and 'label' in config:
        return config['label']
    elif hasattr(config, 'label'):
        return config.label or col
    else:
        return col.replace('_', ' ').title()

# Função para aplicar formatações ao DataFrame
def aplicar_formatacoes(df):
    for coluna in df.columns:
        if coluna == 'niFornecedor':
            df[coluna] = df[coluna].apply(lambda x: aplicar_mascara(x, 'cnpj'))
        elif coluna == 'precoUnitario':
            df[coluna] = df[coluna].apply(lambda x: aplicar_mascara(x, 'preco'))
        elif coluna == 'quantidade':
            df[coluna] = df[coluna].apply(lambda x: aplicar_mascara(x, 'quantidade'))
        elif coluna == 'codigoItemCatalogo':
            df[coluna] = df[coluna].apply(lambda x: aplicar_mascara(x, 'catmat'))
        elif coluna == 'dataResultado':
            df[coluna] = df[coluna].apply(lambda x: aplicar_mascara(x, 'data'))
    return df

with tab1:
    st.header("Dados brutos")
    if isinstance(st.session_state.df, pd.DataFrame):
        df_formatado = aplicar_formatacoes(st.session_state.df.copy())
        agent = get_or_create_agent(df_formatado, st.session_state.model_choice)
        
        st.dataframe(
            df_formatado,
            use_container_width=True,
            hide_index=True,
            column_config={col: get_column_config(col) for col in df_formatado.columns}
        )
        
        # Container para o histórico de mensagens
        chat_container = st.container()
        
        # Container para o campo de input fixo no rodapé
        input_container = st.container()
        
        # Exibir mensagens no container de chat
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Campo de input fixo no rodapé
        with input_container:
            prompt = st.chat_input("Faça uma pergunta sobre os dados")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    with st.spinner("Analisando..."):
                        response = agent.invoke({'input': prompt})
                        full_response = response['output']
                    message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()
    else:
        st.info("Nenhum dado carregado. Use o painel lateral para buscar dados.")

with tab2:
    st.header("Parâmetros")
    
    if isinstance(st.session_state.df, pd.DataFrame) and 'precoUnitario' in st.session_state.df.columns:
        # Processar a coluna de Preço Unitário
        preco_unitario = pd.to_numeric(st.session_state.df['precoUnitario'], errors='coerce')
        
        # Cálculo das estatísticas
        media, limite_inferior, limite_superior = calcular_estatisticas(preco_unitario)
        desvio_padrao = preco_unitario.std()
        cv = (desvio_padrao / media) * 100 if media != 0 else 0

        # Exibição das estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Média do Preço Unitário", value=f"R$ {media:.2f}")
            st.metric(label="Mediana do Preço Unitário", value=f"R$ {preco_unitario.median():.2f}")
        with col2:
            st.metric(label="Menor Preço Unitário", value=f"R$ {preco_unitario.min():.2f}")
            st.metric(label="Limite Inferior", value=f"R$ {limite_inferior:.2f}")
        with col3:
            st.metric(label="Maior Preço Unitário", value=f"R$ {preco_unitario.max():.2f}")
            st.metric(label="Limite Superior", value=f"R$ {limite_superior:.2f}")
        
        # Métrica para o Coeficiente de Variação
        cv_delta = "OK" if cv <= 25 else f"{cv - 25:.2f}% acima do limite"
        cv_delta_color = "normal" if cv <= 25 else "inverse"
        st.metric(
            label="Coeficiente de Variação",
            value=f"{cv:.2f}%",
            delta=cv_delta,
            delta_color=cv_delta_color
        )

        # Instrução para o usuário sobre o CV
        if cv > 25:
            st.warning("O Coeficiente de Variação está acima de 25%. Considere analisar os dados para identificar possíveis outliers.")
        else:
            st.success("O Coeficiente de Variação está dentro do limite desejado (25% ou menos).")
    else:
        st.warning("A coluna 'precoUnitario' não foi encontrada nos dados carregados ou nenhum dado foi carregado.")

with tab3:
    st.header("Gráficos")
    
    if isinstance(st.session_state.df, pd.DataFrame):
        if 'quantidade' in st.session_state.df.columns and 'precoUnitario' in st.session_state.df.columns:
            # Converter as colunas para numérico
            quantidade = st.session_state.df['quantidade'].apply(limpar_e_converter)
            preco_unitario = st.session_state.df['precoUnitario'].apply(limpar_e_converter)
            
            # Criar DataFrame com dados válidos
            dados_validos = pd.DataFrame({'quantidade': quantidade, 'preco_unitario': preco_unitario})
            dados_validos = dados_validos.replace([np.inf, -np.inf], np.nan).dropna()
            
            if not dados_validos.empty:
                # Gráfico de dispersão
                fig_correlacao = px.scatter(dados_validos, x='quantidade', y='preco_unitario', 
                                            labels={'quantidade': 'Quantidade', 'preco_unitario': 'Preço Unitário'},
                                            title="Correlação entre Quantidade e Preço Unitário")
                st.plotly_chart(fig_correlacao, use_container_width=True)
                
                # Cálculo e exibição da correlação
                correlacao = dados_validos['quantidade'].corr(dados_validos['preco_unitario'])
                st.write(f"Coeficiente de correlação: {correlacao:.2f}")
                
                # Interpretação da correlação
                if correlacao < -0.5:
                    st.success("Há uma forte correlação negativa.")
                elif correlacao > 0.5:
                    st.warning("Há uma forte correlação positiva.")
                else:
                    st.info("Não há uma correlação forte entre quantidade e preço unitário.")

                # Gráfico com linha de tendência
                try:
                    fig_correlacao_tendencia = px.scatter(dados_validos, x='quantidade', y='preco_unitario', 
                                                          labels={'quantidade': 'Quantidade', 'preco_unitario': 'Preço Unitário'},
                                                          title="Correlação com Linha de Tendência",
                                                          trendline="ols")
                    st.plotly_chart(fig_correlacao_tendencia, use_container_width=True)
                except Exception as e:
                    st.warning(f"Erro ao gerar gráfico com linha de tendência: {str(e)}")

                # Histograma de preço unitário
                hist_preco = alt.Chart(dados_validos).mark_bar().encode(
                    alt.X('preco_unitario', bin=alt.Bin(maxbins=30), title='Preço Unitário (R$)'),
                    alt.Y('count()', title='Contagem'),
                    tooltip=['count()']
                ).properties(
                    title='Distribuição do Preço Unitário',
                    width=600,
                    height=400
                )
                
                # Exibir o gráfico
                st.altair_chart(hist_preco, use_container_width=True)

                # Explicação adicional sobre o histograma
                st.info("O histograma acima mostra a distribuição dos preços unitários. " 
                        "Cada barra representa um intervalo de preços, e a altura da barra indica quantos itens estão nesse intervalo.")
            else:
                st.warning("Não há dados válidos para criar os gráficos após a limpeza e conversão.")
        else:
            st.warning("As colunas 'quantidade' e 'precoUnitario' são necessárias para esta análise.")
    else:
        st.info("Nenhum dado carregado. Use o painel lateral para buscar dados.")


