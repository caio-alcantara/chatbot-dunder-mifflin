from google.adk.agents.llm_agent import Agent
import pandas as pd
from .PROMPT import CSV_AGENT_PROMPT

CSV_PATH = "data/transacoes_bancarias.csv"


def infer_csv_schema(csv_path: str = CSV_PATH):
    df = pd.read_csv(csv_path)
    columns_info = {col: str(dtype) for col, dtype in zip(df.columns, df.dtypes)}
    return str(columns_info)

def execute_pandas_query(query: str):
    df = pd.read_csv(CSV_PATH)
    try:
        # Namespace restrito para maior segurança
        namespace = {
            'df': df,
            'pd': pd,
            '__builtins__': {}  # Remove funções built-in perigosas
        }
        
        result_df = eval(query, namespace)
        
        if not isinstance(result_df, pd.DataFrame):
            if isinstance(result_df, pd.Series):
                result_df = result_df.to_frame()
            else:
                return {"error": "A query não retornou um DataFrame válido"}
        
        return result_df.to_dict(orient='records')
    except Exception as e:
        return {"error": f"Erro ao executar a query: {str(e)}"}

def extract_keywords_from_input(user_input: str):
    """
    Extrai todas as palavras-chave de todos os campos 'keywords_found'
    dentro de 'emails_detectados' do JSON fornecido pelo usuário.
    """
    import json

    try:
        data = json.loads(user_input)

        emails = data.get("emails_detectados", [])
        all_keywords = []

        for email in emails:
            kws = email.get("keywords_found", [])
            if isinstance(kws, list):  # segurança
                all_keywords.extend(kws)

        return all_keywords

    except json.JSONDecodeError:
        return []

root_agent = Agent(
    model='gemini-2.5-flash',
    name='agent_csv',
    description='Um agente que interpreta arquivos CSV e responde perguntas baseadas nesses dados.',
    instruction=CSV_AGENT_PROMPT,
    tools=[infer_csv_schema, execute_pandas_query, extract_keywords_from_input]
)
