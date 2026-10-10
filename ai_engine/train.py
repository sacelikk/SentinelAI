import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
import os

from model import MalwareClassifier
from dataset import EmberDataset

def load_ember_data(data_dir):
    print("EMBER Veri Seti (Memmap) yükleniyor...")
    
    # 1. EMBER 2018 veri setinde toplam 600.000 eğitim verisi vardır
    # Bu devasa veriyi RAM'e doldurmamak için numpy 'memmap' (disk üzerinden okuma) kullanıyoruz.
    X_train_memmap = np.memmap(os.path.join(data_dir, "X_train.dat"), dtype=np.float32, mode="r", shape=(600000, 2381))
    y_train_memmap = np.memmap(os.path.join(data_dir, "y_train.dat"), dtype=np.float32, mode="r", shape=(600000,))
    
    # 2. EMBER'da etiketler şöyledir: 0 (Temiz), 1 (Zararlı), -1 (Bilinmiyor/Etiketsiz)
    # Biz -1'leri (bilinmeyenleri) filtreliyoruz ki modelin kafası karışmasın.
    print("Etiketsiz veriler temizleniyor...")
    valid_idx = (y_train_memmap != -1)
    
    # Gerçek eğitim verilerimiz (Sadece 0 ve 1 olanlar)
    X_train = np.array(X_train_memmap[valid_idx]) # RAM'e kopyalıyoruz (artık sadece etiketliler)
    y_train = np.array(y_train_memmap[valid_idx])
    
    print(f"Toplam {len(y_train)} adet etiketli gerçek dosya (Özellikleri) yüklendi!")
    return X_train, y_train

def train_model():
    data_dir = "data/ember2018" 
    
    if not os.path.exists(data_dir):
        print(f"HATA: {data_dir} klasörü bulunamadı! Lütfen verilerin çıkarıldığından emin olun.")
        return

    # Gerçek verileri yükle
    X_train, y_train = load_ember_data(data_dir)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n[{device.type.upper()}] üzerinden eğitim başlatılıyor...")

    # Verileri kargocuya (DataLoader) ver (Eskiden 32 idi, şimdi ekran kartımız güçlü olduğu için 256 yapıyoruz)
    dataset = EmberDataset(X_train, y_train)
    dataloader = DataLoader(dataset, batch_size=256, shuffle=True)

    # Modeli Başlat
    model = MalwareClassifier().to(device)
    criterion = nn.BCELoss()
    # Öğrenme hızı (Learning Rate) belirleme
    optimizer = optim.Adam(model.parameters(), lr=0.0001)

    epochs = 10 # 600 bin dosyayı tam 10 kez baştan sona görecek
    
    print("\n--- GERÇEK EMBER EĞİTİMİ BAŞLADI ---")
    for epoch in range(epochs):
        total_loss = 0
        
        for batch_idx, (features, labels) in enumerate(dataloader):
            features = features.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            predictions = model(features)
            loss = criterion(predictions, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            # Her 100 grupta bir ilerlemeyi göster
            if batch_idx % 100 == 0:
                print(f"Tur [{epoch+1}/{epochs}] - İlerleme: {batch_idx*256}/{len(y_train)} - Anlık Hata: {loss.item():.4f}")
                
        ortalama_hata = total_loss / len(dataloader)
        print(f"====== TUR {epoch+1} BİTTİ. Ortalama Hata: {ortalama_hata:.4f} ======\n")

    print("Eğitim başarıyla tamamlandı!")
    torch.save(model.state_dict(), "sentinel_ai_model.pth")
    print("Gerçek zekâlı model 'sentinel_ai_model.pth' olarak kaydedildi.")

if __name__ == "__main__":
    train_model()
