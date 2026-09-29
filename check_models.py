from groq import Groq
from config import Config

try:
    client = Groq(api_key=Config.GROQ_API_KEY)
    models = client.models.list()
    print("--- HESABINIZDA AKTİF MODEL LİSTESİ ---")
    for m in models.data:
        print(f"• {m.id}")
except Exception as e:
    print("Hata:", str(e))