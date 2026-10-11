using System;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Media;
using Microsoft.Win32;
using Newtonsoft.Json.Linq;

namespace SentinelUI
{
    public partial class MainWindow : Window
    {
        private readonly HttpClient _client;

        public MainWindow()
        {
            InitializeComponent();
            _client = new HttpClient();
            _client.Timeout = TimeSpan.FromMinutes(2);
        }

        // Sürükle - Bırak (Drag & Drop) Olayları
        private void Window_DragEnter(object sender, DragEventArgs e)
        {
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                e.Effects = DragDropEffects.Copy;
                DropZoneBorder.BorderBrush = (SolidColorBrush)new BrushConverter().ConvertFrom("#38BDF8");
            }
        }

        private async void Window_Drop(object sender, DragEventArgs e)
        {
            DropZoneBorder.BorderBrush = (SolidColorBrush)new BrushConverter().ConvertFrom("#1E293B");
            if (e.Data.GetDataPresent(DataFormats.FileDrop))
            {
                string[] files = (string[])e.Data.GetData(DataFormats.FileDrop);
                if (files.Length > 0)
                {
                    await ScanFileAsync(files[0]);
                }
            }
        }

        // Butonla Dosya Seçme
        private async void BtnSelectFile_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Title = "Taranacak Dosyayı Seçin",
                Filter = "Desteklenen Dosyalar (*.exe, *.dll, *.*)|*.exe;*.dll;*.*"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                await ScanFileAsync(openFileDialog.FileName);
            }
        }

        private async Task ScanFileAsync(string filePath)
        {
            try
            {
                string fileName = Path.GetFileName(filePath);
                TxtDropTitle.Text = $"Analiz Ediliyor: {fileName}";
                TxtSelectedFilePath.Text = filePath;
                TxtStatusMessage.Text = "Dosya FastAPI motoruna aktarılıyor ve taranıyor...";
                
                BtnSelectFile.IsEnabled = false;

                // Yükleme Animasyonu / Geçici Durum
                TxtVerdictIcon.Text = "⏳";
                TxtVerdictTitle.Text = "Taranıyor...";
                TxtVerdictTitle.Foreground = Brushes.White;
                TxtRiskPercentage.Text = "Lütfen bekleyin...";
                VerdictBadge.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#1E293B");
                RiskProgressBar.Value = 25;
                RiskProgressBar.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#38BDF8");

                using (var multipartFormContent = new MultipartFormDataContent())
                {
                    var fileStreamContent = new StreamContent(File.OpenRead(filePath));
                    multipartFormContent.Add(fileStreamContent, name: "file", fileName: fileName);

                    // FastAPI sunucusuna istek gönder
                    HttpResponseMessage response = await _client.PostAsync("http://127.0.0.1:8000/scan", multipartFormContent);
                    response.EnsureSuccessStatusCode();

                    string responseJson = await response.Content.ReadAsStringAsync();
                    ParseAndDisplayResult(responseJson, fileName);
                }
            }
            catch (Exception ex)
            {
                TxtVerdictIcon.Text = "⚠️";
                TxtVerdictTitle.Text = "Bağlantı Hatası";
                TxtVerdictTitle.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#EF4444");
                VerdictBadge.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#450A0A");
                TxtStatusMessage.Text = "Python API (FastAPI) sunucusuna ulaşılamadı. Lütfen 'python api/server.py' komutunun çalıştığından emin olun.";
                TxtRiskPercentage.Text = "Hata";
                RiskProgressBar.Value = 0;
            }
            finally
            {
                BtnSelectFile.IsEnabled = true;
            }
        }

        private void ParseAndDisplayResult(string jsonResult, string fileName)
        {
            try
            {
                JObject result = JObject.Parse(jsonResult);

                string karar = result["genel_karar"]?.ToString() ?? "Bilinmiyor";
                string riskSkoruStr = result["risk_skoru"]?.ToString()?.Replace("%", "") ?? "0";
                int.TryParse(riskSkoruStr, out int riskSkoru);

                // Risk Skoru ve Progress Bar
                RiskProgressBar.Value = riskSkoru;
                TxtRiskPercentage.Text = $"Risk Skoru: %{riskSkoru}";
                TxtStatusMessage.Text = $"{fileName} başarıyla analiz edildi.";

                // 1. SOL PANEL: GENEL VERDICT
                if (karar.Contains("KRİTİK") || riskSkoru >= 80)
                {
                    TxtVerdictIcon.Text = "☣️";
                    TxtVerdictTitle.Text = "KRİTİK TEHDİT";
                    TxtVerdictTitle.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#EF4444"); // Kırmızı
                    VerdictBadge.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#450A0A");
                    RiskProgressBar.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#EF4444");
                }
                else if (karar.Contains("Şüpheli") || riskSkoru > 40)
                {
                    TxtVerdictIcon.Text = "⚠️";
                    TxtVerdictTitle.Text = "ŞÜPHELİ";
                    TxtVerdictTitle.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#F59E0B"); // Turuncu
                    VerdictBadge.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#451A03");
                    RiskProgressBar.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#F59E0B");
                }
                else
                {
                    TxtVerdictIcon.Text = "🛡️";
                    TxtVerdictTitle.Text = "GÜVENLİ / TEMİZ";
                    TxtVerdictTitle.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#10B981"); // Yeşil
                    VerdictBadge.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#064E3B");
                    RiskProgressBar.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#10B981");
                }

                // 2. SAĞ PANEL: AI MODÜLÜ BİLGİLERİ
                var aiModulu = result["detaylar"]?["ai_modulu"];
                if (aiModulu != null)
                {
                    string aiSkor = aiModulu["skor"]?.ToString() ?? "0.0000";
                    string aiKarar = aiModulu["karar"]?.ToString() ?? "Temiz";
                    TxtAiScoreValue.Text = aiSkor;

                    if (aiKarar == "Şüpheli")
                    {
                        AiPill.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#7F1D1D");
                        TxtAiPill.Text = "ŞÜPHELİ";
                        TxtAiPill.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#FCA5A5");
                    }
                    else
                    {
                        AiPill.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#064E3B");
                        TxtAiPill.Text = "TEMİZ";
                        TxtAiPill.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#6EE7B7");
                    }
                }

                // 3. SAĞ PANEL: YARA MODÜLÜ BİLGİLERİ
                var yaraModulu = result["detaylar"]?["yara_modulu"];
                if (yaraModulu != null)
                {
                    string yaraKarar = yaraModulu["karar"]?.ToString() ?? "Temiz";
                    var eslesmeler = yaraModulu["eslesmeler"] as JArray;

                    if (yaraKarar == "Şüpheli" && eslesmeler != null && eslesmeler.Count > 0)
                    {
                        YaraPill.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#7F1D1D");
                        TxtYaraPill.Text = $"{eslesmeler.Count} EŞLEŞME";
                        TxtYaraPill.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#FCA5A5");

                        string rulesSummary = "";
                        foreach (var match in eslesmeler)
                        {
                            rulesSummary += $"• Kural: {match["rule"]} (Ağırlık: {match["meta"]?["severity"]})\n";
                        }
                        TxtYaraDetails.Text = rulesSummary;
                        TxtYaraDetails.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#F87171");
                    }
                    else
                    {
                        YaraPill.Background = (SolidColorBrush)new BrushConverter().ConvertFrom("#064E3B");
                        TxtYaraPill.Text = "EŞLEŞME YOK";
                        TxtYaraPill.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#6EE7B7");
                        TxtYaraDetails.Text = "Herhangi bir şüpheli imza, komut veya paketleyici bulunamadı.";
                        TxtYaraDetails.Foreground = (SolidColorBrush)new BrushConverter().ConvertFrom("#64748B");
                    }
                }
            }
            catch (Exception ex)
            {
                TxtStatusMessage.Text = "Sonuç ayrıştırılırken hata oluştu: " + ex.Message;
            }
        }
    }
}