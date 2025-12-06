from google.adk.agents.llm_agent import Agent
from .PROMPT import AGENT_FINANCIAL_INTERPRETER_PROMPT

def get_tools():
    from src.tools import (
        search_compliance_policies, 
        search_by_keyword, 
        get_policy_summary,
    )
    return [
        search_compliance_policies,
        search_by_keyword,
        get_policy_summary,
    ]

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='Um assistente especializado em interpretar dados de transações financeiras para identificar violações de políticas de compliance da Dunder Mifflin.',
    instruction=AGENT_FINANCIAL_INTERPRETER_PROMPT,
    tools=get_tools()
)


