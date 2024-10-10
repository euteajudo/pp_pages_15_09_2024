import requests
from datetime import datetime
import pandas as pd
import sqlite3
import concurrent.futures
import streamlit as st
import aiohttp
import asyncio

@st.cache_data(ttl=3600)
def fetch_page(url, params):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def obter_mapeamento_modalidades():
    conn = sqlite3.connect('data/info.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, modalidade FROM modalidades")
    mapeamento = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    print("Mapeamento de modalidades:", mapeamento)  # Para debug
    return mapeamento

async def consultar_api_governo_async(codigo_item, data_inicial, data_final):
    url = "https://dadosabertos.compras.gov.br/modulo-pesquisa-preco/1_consultarMaterial"
    data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d").strftime("%d-%m-%Y")
    data_final = datetime.strptime(data_final, "%Y-%m-%d").strftime("%d-%m-%Y")
    
    params = {
        "codigoItemCatalogo": codigo_item,
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": 1
    }

    async with aiohttp.ClientSession() as session:
        # Primeira requisição para obter o total de registros
        first_page = await fetch_page_async(session, url, params)
        if not first_page or 'totalRegistros' not in first_page:
            print("Erro na primeira requisição ou 'totalRegistros' não encontrado")
            return {"df": None, "total_registros": 0, "total_paginas": 0}

        total_registros = first_page['totalRegistros']
        total_paginas = (total_registros - 1) // 20 + 1  # Assumindo 20 registros por página
        print(f"Total de registros: {total_registros}, Total de páginas: {total_paginas}")

        # Função para processar uma página
        async def process_page(page_num):
            page_params = params.copy()
            page_params['pagina'] = page_num
            async with session.get(url, params=page_params) as response:
                if response.status == 200:
                    page_data = await response.json()
                    if 'resultado' in page_data:
                        return page_data['resultado']
            return []

        all_results = []
        tasks = [process_page(i) for i in range(1, total_paginas + 1)]
        for result in asyncio.as_completed(tasks):
            data = await result
            all_results.extend(data)
            # Atualizar o progresso
            progress = len(all_results) / total_registros
            if 'progress_bar' in st.session_state:
                st.session_state.progress_bar.progress(progress)

        print(f"Total de resultados coletados: {len(all_results)}")

        if all_results:
            df = pd.DataFrame(all_results)
            
            # Converter colunas de data para datetime
            date_columns = ['dataCompra', 'dataHoraAtualizacaoCompra', 'dataHoraAtualizacaoItem', 'dataResultado', 'dataHoraAtualizacaoUasg']
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
            
            return {"df": df, "total_registros": total_registros, "total_paginas": total_paginas}
        else:
            return {"df": None, "total_registros": 0, "total_paginas": 0}

async def fetch_page_async(session, url, params):
    async with session.get(url, params=params) as response:
        if response.status == 200:
            return await response.json()
    return None

def update_partial_dataframe(results):
    if 'partial_df' not in st.session_state:
        st.session_state.partial_df = pd.DataFrame()
    
    new_df = pd.DataFrame(results)
    st.session_state.partial_df = pd.concat([st.session_state.partial_df, new_df]).drop_duplicates()
    
    # Atualizar o data_editor com os dados parciais
    if 'data_editor' in st.session_state:
        st.session_state.data_editor.dataframe(st.session_state.partial_df)