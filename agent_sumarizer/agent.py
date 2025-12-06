from google.adk.agents.llm_agent import Agent
from src.call_agent import call_agent
from .PROMPT import AGENT_SUMARIZER_PROMPT

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
    name='agent_summarizer',
    description='Um assistente que resume políticas de compliance da Dunder Mifflin Paper Company.',
    instruction=AGENT_SUMARIZER_PROMPT,
    tools=get_tools()
)

##if __name__ == "__main__":
##    import asyncio
##
##    async def main():
##        from google.adk.sessions import InMemorySessionService
##        session_service = InMemorySessionService()
##        query = "Me diga todos os itens proibidos na política de compliance da dunder mifflin."
##        response = await call_agent(question=query, agent=root_agent, app_name="agent_summarizer_app", session_service=session_service)
##        print("Resposta do Agente de Resumo:")
##        print(response)
##
##    asyncio.run(main())
