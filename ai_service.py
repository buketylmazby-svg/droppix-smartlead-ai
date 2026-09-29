from groq import Groq
from config import Config

def get_ai_response(user_message, chat_history=None):
    """
    Kullanıcı mesajını ve geçmiş sohbeti alarak Droppix B2B/B2C stratejisine uygun AI yanıtı üretir.
    """
    client = Groq(api_key=Config.GROQ_API_KEY)

    # Sistem kişiliğini (BUSINESS_CONTEXT) ekle
    messages = [
        {"role": "system", "content": Config.BUSINESS_CONTEXT}
    ]

    # Varsa geçmiş konuşmaları mesaj listesine dahil et
    if chat_history:
        for chat in chat_history:
            messages.append({
                "role": "assistant" if chat["sender"] == "assistant" else "user",
                "content": chat["message"]
            })

    # Güncel kullanıcı mesajını ekle
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ağ bağlantısı veya API hatası oluştu: {str(e)}"

if __name__ == '__main__':
    # Hızlı Test
    test_soru = "Merhaba! Kadıköy'de mekan işletmecisiyim, Droppix ile nasıl iş birliği yapabilirim?"
    print(f"\n--- TEST SORUSU ---\n{test_soru}\n")
    print("--- DROPPIX AI YANITI ---")
    print(get_ai_response(test_soru))