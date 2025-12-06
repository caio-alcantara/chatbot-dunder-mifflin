
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import uuid
import asyncio
import warnings

# Suprimir warnings de contexto do OpenTelemetry
warnings.filterwarnings('ignore', category=RuntimeWarning, module='opentelemetry')

async def call_agent(question: str, session_service: InMemorySessionService, app_name: str, agent: Agent) -> str:
    """
    Chama um agente ADK de forma assíncrona.
    
    Args:
        question: Pergunta para o agente
        session_service: Serviço de sessão
        app_name: Nome da aplicação
        agent: Agente ADK a ser chamado
        
    Returns:
        Resposta do agente como string
    """
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    
    # Criar sessão
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    runner = Runner(
        agent=agent,
        app_name=app_name,
        session_service=session_service
    )
    
    content = types.Content(role='user', parts=[types.Part(text=question)])
    
    final_response_text = "Investigação concluída sem resposta."
    
    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Erro na investigação: {event.error_message or 'Erro desconhecido'}"
                break
    except GeneratorExit:
        # Ignora erro de contexto quando o generator é fechado prematuramente
        pass
    except Exception as e:
        final_response_text = f"Erro ao processar requisição: {str(e)}"
    
    return final_response_text

if __name__ == "__main__":
    ## Exemplo de uso com um agente de compliance

    from agent_compliance.agent import root_agent as compliance_agent

    async def main():
        session_service = InMemorySessionService()
        question = "Posso gastar US$ 75 em almoço com cliente?"
        response = await call_agent(
            question=question,
            session_service=session_service,
            app_name="compliance_app",
            agent=compliance_agent
        )
        print("Resposta do Agente de Compliance:")
        print(response)

    asyncio.run(main())
