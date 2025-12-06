# test_connection.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carregar variáveis de ambiente
load_dotenv()

# Configurar API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env")

genai.configure(api_key=api_key)

# Testar conexão
print("🔍 Testando conexão com Google AI...")

try:
    # Listar modelos disponíveis
    print("\n📋 Modelos disponíveis:")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name[7:]}")
    
    # Testar geração simples
    print("\nTestando geração de texto...")
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Diga 'Olá, mundo!' em português")
    print(f"✅ Resposta: {response.text}")
    
    print("\n✅ Conexão estabelecida com sucesso!")
    
except Exception as e:
    print(f"\n❌ Erro na conexão: {e}")