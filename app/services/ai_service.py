
import os
import logging

from groq import Groq

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Yapay zekâ servisi kaynaklı hatalar."""
    pass


class AIService:

    def yanit_uret(self, mesaj, gecmis=None):
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            raise AIServiceError(
                "GROQ_API_KEY sistemde tanımlı değil."
            )

        # Render Environment üzerinden değiştirilebilir.
        model_name = os.environ.get(
            "GROQ_MODEL",
            "openai/gpt-oss-120b"
        )

        try:
            client = Groq(api_key=api_key)

            system_prompt = (
                "Sen Droppix platformunun samimi, enerjik ve "
                "ilham verici yapay zekâ asistanısın.\n\n"

                "DROPPIX NEDİR:\n"
                "Droppix, kullanıcıların fotoğraflarını, "
                "düşüncelerini, notlarını, müziklerini ve "
                "gittikleri mekânları kaydettiği kişisel "
                "yaşam arşivi platformudur. Bu içerikler "
                "haftalık hikâyeleştirilmiş dijital kolajlara "
                "dönüştürülür. Bu kolajlara Drop denir.\n\n"

                "LIVE IT ÖZELLİĞİ:\n"
                "Live it, diğer kullanıcıların Drop'larından "
                "ve yaşam arşivlerinden ilham almayı sağlayan "
                "keşif özelliğidir.\n\n"

                "SOHBET KURALLARI:\n"
                "1. Türkçe, samimi ve doğal konuş.\n"
                "2. Kısa ve akıcı yanıtlar ver.\n"
                "3. En fazla iki kısa paragraf kullan.\n"
                "4. Gereksiz teknik ifadelerden kaçın.\n"
                "5. Markdown tabloları, büyük başlıklar ve "
                "yatay çizgiler kullanma.\n"
                "6. Droppix özellikleri hakkında sorularda "
                "platformun amacına uygun yanıt ver.\n"
            )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                }
            ]
<<<<<<< HEAD
        except Exception:
            aktif_modeller = ["openai/gpt-oss-120b"]
=======
>>>>>>> 57eb89721e1e8501e73f32963b10d7881e347049

            # Geçmiş varsa yalnızca geçerli mesajları ekle.
            if gecmis:
                for item in gecmis:
                    if not isinstance(item, dict):
                        continue

                    role = item.get("role")
                    content = item.get("content")

                    if (
                        role in ("user", "assistant")
                        and isinstance(content, str)
                        and content.strip()
                    ):
                        messages.append({
                            "role": role,
                            "content": content
                        })

            messages.append({
                "role": "user",
                "content": mesaj
            })

            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=350,
                timeout=30
            )

            if not completion.choices:
                raise AIServiceError(
                    "Yapay zekâ yanıt oluşturamadı."
                )

            cevap = completion.choices[0].message.content

            if not cevap or not cevap.strip():
                raise AIServiceError(
                    "Yapay zekâ boş yanıt döndürdü."
                )

            return cevap.strip()

        except AIServiceError:
            raise

        except Exception as e:
            # API anahtarını loglara yazdırma.
            logger.exception(
                "Groq API isteği başarısız. Model: %s",
                model_name
            )

            raise AIServiceError(
                f"Yapay zekâ servisi hata verdi: "
                f"{type(e).__name__}: {e}"
            ) from e


ai_service = AIService()
