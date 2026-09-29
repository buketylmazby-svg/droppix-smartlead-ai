from config import Config

print("\n--- ORTAM KURULUM KONTROLÜ ---")
print("AI Saglayici : " + str(Config.AI_PROVIDER))
print("Veritabani   : " + str(Config.DATABASE_URL))
print("--- BUSINESS CONTEXT OZETI ---")
print(Config.BUSINESS_CONTEXT[:300])
print("-------------------------------")
print("TEBRİKLER! Droppix konfigürasyonu ve ortam kurulumu başarıyla okundu.\n")