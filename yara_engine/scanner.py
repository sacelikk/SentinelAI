import yara
import os
import json

class YaraScanner:
    def __init__(self, rules_dir="rules"):
        self.rules_dir = os.path.join(os.path.dirname(__file__), rules_dir)
        self.rules = self._compile_rules()

    def _compile_rules(self):
        """Klasördeki tüm .yar dosyalarını derler."""
        rule_files = {}
        if not os.path.exists(self.rules_dir):
            print(f"Uyarı: Kurallar klasörü bulunamadı -> {self.rules_dir}")
            return None

        for filename in os.listdir(self.rules_dir):
            if filename.endswith(".yar") or filename.endswith(".yara"):
                filepath = os.path.join(self.rules_dir, filename)
                # YARA, dosyaları { 'namespace': 'filepath' } şeklinde derler
                rule_files[filename] = filepath
        
        if not rule_files:
            print("Uyarı: Hiç YARA kuralı bulunamadı.")
            return None
            
        try:
            print(f"{len(rule_files)} kural dosyası derleniyor...")
            compiled_rules = yara.compile(filepaths=rule_files)
            return compiled_rules
        except yara.SyntaxError as e:
            print(f"YARA Kural Sözdizimi Hatası: {e}")
            return None

    def scan_file(self, filepath):
        """Verilen dosyayı derlenmiş YARA kuralları ile tarar."""
        if not self.rules:
            return {"error": "Kurallar yüklenemedi."}
            
        if not os.path.exists(filepath):
            return {"error": "Taranacak dosya bulunamadı."}

        try:
            matches = self.rules.match(filepath)
            
            result = {
                "file": filepath,
                "matches": [],
                "is_suspicious": len(matches) > 0
            }
            
            for match in matches:
                match_data = {
                    "rule": match.rule,
                    "namespace": match.namespace,
                    "meta": match.meta,
                    # Hangi stringlerin eşleştiğini de görebiliriz
                    "strings_matched": list(set([s.identifier for s in match.strings])) 
                }
                result["matches"].append(match_data)
                
            return result
            
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    # Test etmek için küçük bir örnek
    scanner = YaraScanner()
    
    # Kendi dosyasını (scanner.py) tarasın (içinde zararlı bir şey yok, eşleşme beklemeyiz)
    # Ama test için 'cmd.exe /c' yazan sahte bir text dosyası oluşturalım:
    test_file = "test_malware.txt"
    with open(test_file, "w") as f:
        f.write("This is a normal file, but wait... cmd.exe /c format c:")
        
    print(f"\n--- {test_file} Taranıyor ---")
    report = scanner.scan_file(test_file)
    print(json.dumps(report, indent=4, ensure_ascii=False))
    
    # Test dosyasını temizleyelim
    if os.path.exists(test_file):
        os.remove(test_file)
