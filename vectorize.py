import numpy as np

# Eski EMBER kütüphanesinin çökmemesi için yeni numpy sürümüne uyumluluk yaması
np.int = int
np.float = np.float64
np.bool = np.bool_

import sklearn.feature_extraction
_original_transform = sklearn.feature_extraction.FeatureHasher.transform

# Eski EMBER kütüphanesinin çökmemesi için yeni scikit-learn sürümüne uyumluluk yaması
def patched_transform(self, raw_X):
    if getattr(self, 'input_type', None) == 'string':
        raw_X = [[x] if isinstance(x, str) else x for x in raw_X]
    return _original_transform(self, raw_X)

sklearn.feature_extraction.FeatureHasher.transform = patched_transform

import ember

if __name__ == '__main__':
    print("1. Aşama: .jsonl dosyaları taranıyor ve .dat matrislerine dönüştürülüyor...")
    print("Bu işlem sisteminin hızına göre 10-30 dakika sürebilir (Tüm çekirdekler kullanılıyor).")
    
    try:
        ember.create_vectorized_features("data/ember2018/")
        print("\n[BASARILI] Vektörizasyon başarıyla tamamlandı! X_train.dat ve y_train.dat dosyaları hazır.")
    except Exception as e:
        print(f"\n[HATA] Bir hata oluştu: {e}")
