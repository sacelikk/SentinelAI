import sys
import os
import shutil
from fastapi import FastAPI, UploadFile, File
import uvicorn

# Ana klasörü yola ekliyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.decision_engine import DecisionEngine

# FastAPI uygulamasını ve Karar Motorunu başlatıyoruz
app = FastAPI(title="SentinelAI Antivirus API")
engine = DecisionEngine(ai_model_path="sentinel_ai_model.pth")

# Geçici dosyaların kaydedileceği klasör
TEMP_DIR = "temp_scans"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"mesaj": "SentinelAI API Çalışıyor. Tarama için /scan uç noktasına POST isteği atın."}

@app.post("/scan")
async def scan_file(file: UploadFile = File(...)):
    """
    Kullanıcıdan (veya C# arayüzünden) gelen dosyayı alır, 
    Karar Motoruna sokar ve raporu JSON olarak geri döndürür.
    """
    # Dosyayı geçici olarak sisteme kaydediyoruz
    temp_file_path = os.path.join(TEMP_DIR, file.filename)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Karar Motorunu çalıştır
        rapor = engine.analyze_file(temp_file_path)
        
    except Exception as e:
        rapor = {"error": f"Tarama sırasında hata oluştu: {str(e)}"}
        
    finally:
        # Tarama bittikten sonra güvenlik için geçici dosyayı siliyoruz
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
    return rapor

if __name__ == "__main__":
    # API sunucusunu 8000 portunda başlat
    print("API Sunucusu http://localhost:8000 adresinde başlatılıyor...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
