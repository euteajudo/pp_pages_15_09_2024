import streamlit as st
import pandas as pd
import numpy as np
from plotly import express as px
from utils.utils import calcular_estatisticas, aplicar_formatacoes, get_column_config, limpar_e_converter
import altair as alt

st.set_page_config(page_title="Análise Crítica", page_icon="📊", layout="wide")
st.title("Análise dos Preços Coletados")

# Definição da função atualizar_estatisticas
def atualizar_estatisticas():
    if 'df_analise' in st.session_state and isinstance(st.session_state.df_analise, pd.DataFrame):
        preco_unitario = st.session_state.df_analise['precoUnitario'].apply(limpar_e_converter)
        st.session_state.media, st.session_state.limite_inferior, st.session_state.limite_superior = calcular_estatisticas(preco_unitario)
        st.session_state.desvio_padrao = preco_unitario.std()
        st.session_state.cv = (st.session_state.desvio_padrao / st.session_state.media) * 100 if st.session_state.media != 0 else 0

# Verificar se há dados carregados
if "df" in st.session_state and isinstance(st.session_state.df, pd.DataFrame):
    if 'df_analise' not in st.session_state:
        st.session_state.df_analise = st.session_state.df.copy()
    
    # Chama a função para inicializar as estatísticas
    atualizar_estatisticas()

    # Sidebar para os botões (visíveis em todas as abas)
    with st.sidebar:
        st.header("Opções de Análise")
        filtrar_button = st.button('Filtrar pre-selecionadas')
        excluir_pre_selecionadas = st.button('Excluir pre-selecionadas')
        excluir_fora_limites = st.button('Excluir fora dos limites')

        # Lógica dos botões
        if filtrar_button:
            df_fora_limites = st.session_state.df_analise[st.session_state.df_analise['ForaLimites'] == True]
            df_dentro_limites = st.session_state.df_analise[st.session_state.df_analise['ForaLimites'] == False]
            st.session_state.df_analise = pd.concat([df_fora_limites, df_dentro_limites]).reset_index(drop=True)
            st.success('Linhas filtradas com sucesso!')
            atualizar_estatisticas()
            st.rerun()

        if excluir_pre_selecionadas:
            st.session_state.df_analise = st.session_state.df_analise[st.session_state.df_analise['ForaLimites'] == False].drop(columns=['ForaLimites', 'Desconsiderar'])
            st.success('Linhas pre-selecionadas excluídas')
            atualizar_estatisticas()
            st.rerun()

        if excluir_fora_limites:
            st.session_state.df_analise = st.session_state.df_analise[st.session_state.df_analise['Desconsiderar'] == 'Não'].drop(columns=['ForaLimites', 'Desconsiderar'])
            st.success('Dados atualizados')
            atualizar_estatisticas()
            st.rerun()

    # Criação das tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Análise Crítica", "Parâmetros", "Gráficos", "Dados Personalizados"])

    with tab1:
        st.header("Análise Crítica")
        if isinstance(st.session_state.df_analise, pd.DataFrame):
            df = st.session_state.df_analise.copy()
            
            # Marca as linhas fora dos limites
            df['ForaLimites'] = (df['precoUnitario'].apply(limpar_e_converter) < st.session_state.limite_inferior) | (df['precoUnitario'].apply(limpar_e_converter) > st.session_state.limite_superior)

            # Adiciona a coluna Desconsiderar se não existir
            if 'Desconsiderar' not in df.columns:
                df['Desconsiderar'] = 'Não'

            # Configuração do editor de dados
            config = {
                'Resultado': st.column_config.TextColumn("Resultado", width="medium"),
                'dataHoraAtualizacaoUasg': st.column_config.DatetimeColumn("Data Hora Atualização", format="DD/MM/YYYY HH:mm:ss"),
                'ForaLimites': st.column_config.CheckboxColumn(
                    'Fora dos Limites',
                    help='Indica se o valor está fora dos limites',
                    default=False,
                ),
                'Desconsiderar': st.column_config.SelectboxColumn(
                    'Desconsiderar',
                    help='Selecione para desconsiderar esta linha',
                    options=['Não', 'Sim'],
                    default='Não',
                )
            }

            edited_df = st.data_editor(
                df,
                column_config=config,
                hide_index=True,
                disabled=['ForaLimites'],
                use_container_width=True,
                key="data_editor"
            )

            # Atualiza df_analise com as edições
            st.session_state.df_analise = edited_df

        else:
            st.warning("Nenhum dado carregado para análise.")

    with tab2:
        st.header("Parâmetros")
        
        # Exibição das estatísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Média do Preço Unitário", value=f"R$ {st.session_state.media:.2f}")
            st.metric(label="Mediana do Preço Unitário", value=f"R$ {st.session_state.df_analise['precoUnitario'].apply(limpar_e_converter).median():.2f}")
        with col2:
            st.metric(label="Menor Preço Unitário", value=f"R$ {st.session_state.df_analise['precoUnitario'].apply(limpar_e_converter).min():.2f}")
            st.metric(label="Limite Inferior", value=f"R$ {st.session_state.limite_inferior:.2f}")
        with col3:
            st.metric(label="Maior Preço Unitário", value=f"R$ {st.session_state.df_analise['precoUnitario'].apply(limpar_e_converter).max():.2f}")
            st.metric(label="Limite Superior", value=f"R$ {st.session_state.limite_superior:.2f}")
        
        # Métrica para o Coeficiente de Variação
        cv_delta = "OK" if st.session_state.cv <= 25 else f"{st.session_state.cv - 25:.2f}% acima do limite"
        cv_delta_color = "normal" if st.session_state.cv <= 25 else "inverse"
        st.metric(
            label="Coeficiente de Variação",
            value=f"{st.session_state.cv:.2f}%",
            delta=cv_delta,
            delta_color=cv_delta_color
        )

    with tab3:
        st.header("Gráficos")
        if 'quantidade' in st.session_state.df_analise.columns and 'precoUnitario' in st.session_state.df_analise.columns:
            st.subheader("Correlação entre Quantidade e Preço Unitário")
            
            # Converter as colunas para numérico
            quantidade = st.session_state.df_analise['quantidade'].apply(limpar_e_converter)
            preco_unitario = st.session_state.df_analise['precoUnitario'].apply(limpar_e_converter)
            
            # Criar o gráfico de dispersão
            dados_grafico = pd.DataFrame({'quantidade': quantidade, 'preco_unitario': preco_unitario})
            dados_grafico = dados_grafico.dropna()  # Remover linhas com valores nulos
            
            grafico = alt.Chart(dados_grafico).mark_circle().encode(
                x='quantidade',
                y='preco_unitario',
                tooltip=['quantidade', 'preco_unitario']
            ).properties(
                width=600,
                height=400,
                title='Correlação entre Quantidade e Preço Unitário'
            )
            
            st.altair_chart(grafico, use_container_width=True)
            
            # Calcular e exibir o coeficiente de correlação
            correlacao = dados_grafico['quantidade'].corr(dados_grafico['preco_unitario'])
            st.write(f"Coeficiente de correlação: {correlacao:.2f}")
            
            # Interpretar a correlação
            if correlacao < -0.5:
                st.success("Há uma forte correlação negativa. Isso indica que, em geral, quanto maior a quantidade, menor o preço unitário.")
            elif correlacao > 0.5:
                st.warning("Há uma forte correlação positiva. Isso indica que, em geral, quanto maior a quantidade, maior o preço unitário.")
            else:
                st.info("Não há uma correlação forte entre quantidade e preço unitário.")
        else:
            st.warning("As colunas 'quantidade' e 'precoUnitario' são necessárias para esta análise.")

    with tab4:
        st.header("Dados Personalizados")
        
        # Inicializar colunas_selecionadas no estado da sessão se não existir
        if "colunas_selecionadas" not in st.session_state:
            st.session_state.colunas_selecionadas = []

        # Botão para resetar as seleções
        if st.button("Resetar Seleções"):
            st.session_state.colunas_selecionadas = []  # Limpa as seleções

        # Usar o multiselect para selecionar colunas
        colunas_selecionadas = st.multiselect("Selecione as colunas para visualizar:", st.session_state.df_analise.columns)

        # Atualizar o estado da sessão com as colunas selecionadas
        if colunas_selecionadas:
            st.session_state.colunas_selecionadas = colunas_selecionadas
        else:
            colunas_selecionadas = st.session_state.colunas_selecionadas  # Manter a seleção anterior se nada for selecionado

        if st.session_state.colunas_selecionadas:
            df_personalizado = st.session_state.df_analise[st.session_state.colunas_selecionadas]
            st.dataframe(
                aplicar_formatacoes(df_personalizado),
                use_container_width=True,
                hide_index=True,
                column_config={col: get_column_config(col) for col in st.session_state.colunas_selecionadas}
            )

else:
    st.info("Por favor, carregue os dados usando o painel lateral antes de visualizar o dashboard.")


