import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np

class EmberDataset(Dataset):
    def __init__(self, features, labels):
        """
        features: numpy array, boyut: (örnek_sayısı, 2381)
        labels: numpy array, boyut: (örnek_sayısı,)  -> 0: Temiz, 1: Zararlı
        """
        # Verileri PyTorch tensörlerine dönüştürüyoruz
        self.features = torch.FloatTensor(features)
        self.labels = torch.FloatTensor(labels).unsqueeze(1) # [n, 1] boyutuna getirir

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]

if __name__ == "__main__":
    # Test için rastgele veriler oluşturalım
    print("Test verisi oluşturuluyor...")
    dummy_features = np.random.randn(100, 2381) # 100 dosya, her biri 2381 özellik
    dummy_labels = np.random.randint(0, 2, 100) # 0 veya 1'lerden oluşan 100 etiket
    
    dataset = EmberDataset(dummy_features, dummy_labels)
    
    # DataLoader, eğitimi yaparken verileri batch (grup) halinde modele verir. 
    # Örneğin 100 veriyi, 16'şarlı gruplar halinde eğitiriz.
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    
    features_batch, labels_batch = next(iter(dataloader))
    print(f"Bir Batch'teki (Grup) Özellik Boyutu: {features_batch.shape}")
    print(f"Bir Batch'teki (Grup) Etiket Boyutu: {labels_batch.shape}")
