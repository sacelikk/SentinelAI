# SentinelAI 🛡️
**Multi-Layered AI-Powered Malware Detection Engine**

SentinelAI is an advanced, hybrid malware analysis and detection engine. Instead of relying solely on traditional signature-based scanning or generic API calls, SentinelAI combines a **Custom Deep Neural Network (PyTorch)** trained on the EMBER dataset with **YARA rule-based static analysis** to evaluate Windows PE (Portable Executable) files.

## 🧠 Architecture & Core Modules

The system is built with a modular architecture and exposed via a REST API (FastAPI) to allow seamless integration with any frontend (e.g., C# Desktop App, Web Dashboard).

1. **AI Engine (`ai_engine/`)**:
   - A Deep Neural Network (DNN) built from scratch using **PyTorch**.
   - Trained locally on the **EMBER 2018 Dataset** (extracting 2381 structural features from PE files).
   - Utilizes `LIEF` (Library to Instrument Executable Formats) for real-time reverse engineering and feature extraction of unseen `.exe` and `.dll` files.
2. **YARA Engine (`yara_engine/`)**:
   - Performs traditional, signature-based static analysis.
   - Detects packed executables (e.g., UPX) and suspicious hardcoded strings (`cmd.exe`, `powershell bypass`, etc.).
3. **Decision Engine (`core/`)**:
   - The central brain that aggregates results from both the AI and YARA modules.
   - Reduces false positives by balancing rule-based strictness with machine learning probability scores, generating a final `Risk Score` and `Threat Level`.
4. **API Layer (`api/`)**:
   - Built with **FastAPI** to serve the Decision Engine as a microservice.

## 🚀 Key Features
- **Real-Time Feature Extraction**: Parses PE headers, sections, imports, and strings dynamically using LIEF.
- **Explainable AI**: The decision engine doesn't just return "Malicious"; it details *why* (AI Score + YARA Matches).
- **High Performance**: Vectorized data processing using `numpy.memmap` and multi-processing for handling gigabytes of dataset files.

## 🛠️ Tech Stack
- **Machine Learning**: PyTorch, Scikit-learn, Numpy
- **Reverse Engineering / Security**: LIEF, YARA-Python
- **Backend / API**: Python, FastAPI, Uvicorn

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/SentinelAI.git
   cd SentinelAI
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   *(Ensure you have CUDA-enabled PyTorch installed if you plan to train on GPU)*
   ```bash
   pip install -r requirements.txt
   pip install lief yara-python fastapi uvicorn
   ```

4. **Run the API Server:**
   ```bash
   python api/server.py
   ```
   The API will be available at `http://127.0.0.1:8000/`.

## 🔬 How to Use (API Endpoint)
You can test the engine by sending a POST request to `/scan` with a file:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/scan' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@suspicious_file.exe'
```

## 📜 Dataset Information
The model was trained using the [EMBER 2018 Dataset](https://github.com/elastic/ember), an open-source collection of features extracted from 1.1 million benign and malicious Windows executable files.

---
*Developed as a comprehensive showcase of Machine Learning, Cybersecurity, and Software Engineering integration.*
