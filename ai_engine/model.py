import torch
import torch.nn as nn

class MalwareClassifier(nn.Module):
    def __init__(self, input_dim=2381):
        super(MalwareClassifier, self).__init__()
        
        # EMBER veri setinde çıkarılan özellik (feature) sayısı varsayılan olarak 2381'dir.
        
        # 1. Katman (Giriş)
        self.layer1 = nn.Linear(input_dim, 1024)
        self.bn1 = nn.BatchNorm1d(1024)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3) # Ezberlemeyi (Overfitting) önlemek için nöronların %30'unu rastgele kapatırız
        
        # 2. Katman (Gizli Katman - Hidden Layer)
        self.layer2 = nn.Linear(1024, 512)
        self.bn2 = nn.BatchNorm1d(512)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.3)
        
        # 3. Katman (Gizli Katman)
        self.layer3 = nn.Linear(512, 256)
        self.bn3 = nn.BatchNorm1d(256)
        self.relu3 = nn.ReLU()
        self.dropout3 = nn.Dropout(0.2)
        
        # 4. Katman (Çıkış)
        self.output_layer = nn.Linear(256, 1)
        self.sigmoid = nn.Sigmoid() # Çıktıyı 0 (Temiz) ile 1 (Zararlı) arasına sıkıştırır

    def forward(self, x):
        # Verinin (x) katmanlardan geçiş (İleri yayılım) adımları
        x = self.layer1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        x = self.layer2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        x = self.layer3(x)
        x = self.bn3(x)
        x = self.relu3(x)
        x = self.dropout3(x)
        
        x = self.output_layer(x)
        x = self.sigmoid(x)
        return x

if __name__ == "__main__":
    # Modeli oluştur ve mimariyi ekrana yazdır
    model = MalwareClassifier()
    print("Model Mimarisi:")
    print(model)
    
    # Dummy (Sahte) veri ile test edelim (Örn: 5 adet PE dosyası, her biri 2381 özellikli)
    dummy_input = torch.randn(5, 2381) 
    output = model(dummy_input)
    
    print("\nSahte 5 dosya için modelin ürettiği ham tahmin skorları:")
    print(output.detach().numpy())
