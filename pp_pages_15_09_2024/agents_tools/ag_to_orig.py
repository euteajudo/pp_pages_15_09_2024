from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent

def criar_agente_dataframe(df, model_choice):
    chat = ChatOpenAI(temperature=0, model=model_choice)
    agent = create_pandas_dataframe_agent(
        chat,
        df,
        verbose=True,
        agent_type='tool-calling',
        max_iterations=None,
        allow_dangerous_code=True,
        prefix="Você é um assistente de análise de dados que responde sempre em português. Sua tarefa é analisar os dados fornecidos e responder às perguntas do usuário de forma clara e concisa em português."
    )
    return agent

# Aqui você pode adicionar mais funções para criar outros tipos de agentes ou ferramentas
