import re
import numpy as np
import locale
from datetime import datetime
import pandas as pd

# Configurar a localização para usar vírgula como separador decimal
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def aplicar_mascara(valor, tipo):
    """
    Aplica uma máscara específica baseada no tipo de dado.
    
    :param valor: O valor a ser formatado
    :param tipo: O tipo de formatação (ex: 'cnpj', 'cpf', 'cep', 'preco', 'quantidade', 'catmat', 'data', etc.)
    :return: O valor formatado
    """
    if pd.isna(valor):
        return ''  # Retorna uma string vazia para valores nulos

    if tipo == 'preco':
        try:
            if isinstance(valor, str):
                # Remove caracteres não numéricos, exceto ponto e vírgula
                valor_limpo = re.sub(r'[^\d.,]', '', valor)
                # Substitui vírgula por ponto para conversão
                valor_numerico = float(valor_limpo.replace(',', '.'))
            else:
                valor_numerico = float(valor)
            return valor_numerico
        except ValueError:
            return valor

    if tipo == 'quantidade':
        try:
            numero = float(str(valor).replace('.', '').replace(',', '.'))
            return locale.format_string('%.0f', numero, grouping=True)
        except ValueError:
            return str(valor)

    if tipo == 'catmat':
        try:
            return str(int(float(valor)))
        except ValueError:
            return str(valor)

    if tipo == 'data':
        try:
            if isinstance(valor, (datetime, pd.Timestamp)):
                return valor.strftime("%d/%m/%Y")
            elif isinstance(valor, str):
                return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
            else:
                return str(valor)
        except ValueError:
            return str(valor)

    if tipo == 'cnpj':
        valor_limpo = re.sub(r'\D', '', str(valor))
        if len(valor_limpo) != 14:
            return str(valor)
        return f"{valor_limpo[:2]}.{valor_limpo[2:5]}.{valor_limpo[5:8]}/{valor_limpo[8:12]}-{valor_limpo[12:]}"

    return str(valor)  # Retorna o valor original como string se o tipo não for reconhecido

def calcular_estatisticas(serie):
    media = serie.mean()
    desvio_padrao = serie.std()
    limite_inferior = media - 2 * desvio_padrao
    limite_superior = media + 2 * desvio_padrao
    return media, limite_inferior, limite_superior

def aplicar_formatacoes(df):
    # Aqui você pode adicionar formatações específicas se necessário
    return df

def get_column_config(col):
    # Configuração padrão
    config = {"format": None}
    
    # Adicione configurações específicas para colunas aqui
    if "preco" in col.lower():
        config["format"] = "R$ {:.2f}"
    elif "data" in col.lower():
        config["format"] = "%d/%m/%Y"
    
    return config

# Adicione esta função ao arquivo utils.py
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