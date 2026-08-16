# Deploy FunASR model with offline mode based intel GPU
## 1. Download model SenseVoiceSmall from Huggingface or ModelScope
```
intel/
├──LLM-Models/
   └──SenseVoiceSmall/
```
## 2. Install Server-side Packages
```bash
# pip3 install torch==2.13.0+xpu torchvision==0.28.0+xpu torchaudio==2.11.0+xpu --index-url https://download.pytorch.org/whl/xpu
# pip3 install fastapi==0.141.1 funasr==1.4.2 python-multipart==0.0.32 uvicorn==0.52.3
```
## 3. Start ASR serving 
```bash
python funasr_server.py
```
Serving log is as below:
<img width="1336" height="442" alt="image" src="https://github.com/user-attachments/assets/c1659a48-2905-4ff2-99fd-e758975bc6a6" />

