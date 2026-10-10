import sys
import os
import torch
import numpy as np

# Projenin ana klasörünü yola ekliyoruz ki diğer klasörlerdeki kodları çağırabilelim
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yara_engine.scanner import YaraScanner
from ai_engine.model import MalwareClassifier

class DecisionEngine:
    def __init__(self, ai_model_path="sentinel_ai_model.pth"):
        print("Karar Motoru başlatılıyor...")
        
        # 1. YARA Motorunu Başlat (Parametre vermeye gerek yok, kendisi bulur)
        self.yara_scanner = YaraScanner()
        
        # 2. Eğitilmiş AI Modelini Başlat
        self.ai_model = MalwareClassifier()
        if os.path.exists(ai_model_path):
            # Eğitilmiş ağırlıkları (.pth) yüklüyoruz
            self.ai_model.load_state_dict(torch.load(ai_model_path, weights_only=True))
            print("AI Modeli başarıyla yüklendi.")
        else:
            print(f"Uyarı: {ai_model_path} bulunamadı, AI rastgele sonuçlar üretecek!")
        
        self.ai_model.eval() # Modeli 'kullanım' (tahmin) moduna alıyoruz, her halükarda çağrılmalı

    def _extract_features_for_ai(self, filepath):
        """
        LIEF kütüphanesi ve EMBER'in resmi özellik çıkarıcısını (PEFeatureExtractor)
        kullanarak dosyanın gerçek 2381 adet yapısal özelliğini çıkarır.
        """
        try:
            from ai_engine.ember_features import PEFeatureExtractor
            extractor = PEFeatureExtractor()
            
            with open(filepath, "rb") as f:
                bytez = f.read()
                
            features = extractor.feature_vector(bytez)
            # Yapay zekâ modelimiz [1, 2381] boyutunda bir tensör bekliyor
            return torch.FloatTensor(np.array([features]))
        except Exception as e:
            print(f"Özellik çıkarma hatası (Dosya geçerli bir PE/EXE olmayabilir): {e}")
            # Hata durumunda modelin çökmemesi için sıfırlardan oluşan boş bir özellik dönüyoruz
            return torch.zeros(1, 2381)

    def analyze_file(self, filepath):
        if not os.path.exists(filepath):
            return {"error": "Dosya bulunamadı."}

        print(f"\n[{os.path.basename(filepath)}] Analizi Başladı...")
        
        # --- 1. ADIM: YARA Taraması ---
        yara_result = self.yara_scanner.scan_file(filepath)
        yara_suspicious = yara_result.get("is_suspicious", False)
        
        # --- 2. ADIM: AI Sınıflandırması ---
        # Dosyayı matematiksel özelliklere çevir
        features = self._extract_features_for_ai(filepath) 
        
        # Yapay zekâdan tahmin al (Skor 0 ile 1 arasında olacak)
        with torch.no_grad(): # Tahmin yaparken gradyan hesaplamaya (öğrenmeye) gerek yok, RAM tasarrufu
            ai_score_tensor = self.ai_model(features)
            ai_score = float(ai_score_tensor.numpy()[0][0])
            
        ai_suspicious = ai_score > 0.70 # Eğer skor %70'ten büyükse şüpheli diyelim

        # --- 3. ADIM: Karar Mekanizması ---
        # Burada farklı kaynaklardan gelen bilgileri birleştiriyoruz
        final_risk = "Güvenli"
        risk_level = 0
        
        if yara_suspicious and ai_suspicious:
            final_risk = "KRİTİK TEHDİT"
            risk_level = 100
        elif yara_suspicious:
            final_risk = "Şüpheli (Kural Eşleşmesi)"
            risk_level = 80
        elif ai_suspicious:
            final_risk = "Şüpheli (AI Tespiti)"
            risk_level = round(ai_score * 100)
        else:
            final_risk = "Temiz"
            risk_level = round(ai_score * 100)

        # Raporu Oluştur
        report = {
            "dosya_adi": os.path.basename(filepath),
            "genel_karar": final_risk,
            "risk_skoru": f"%{risk_level}",
            "detaylar": {
                "ai_modulu": {
                    "skor": f"{ai_score:.4f}",
                    "karar": "Şüpheli" if ai_suspicious else "Temiz"
                },
                "yara_modulu": {
                    "karar": "Şüpheli" if yara_suspicious else "Temiz",
                    "eslesmeler": yara_result.get("matches", [])
                }
            }
        }
        return report

if __name__ == "__main__":
    import json
    
    engine = DecisionEngine()
    
    # Test için gerçek bir dosya (calc.exe) tarayalım
    test_file = r"C:\Windows\System32\calc.exe"
        
    rapor = engine.analyze_file(test_file)
    print("\n--- SONUÇ RAPORU ---")
    print(json.dumps(rapor, indent=4, ensure_ascii=False))
