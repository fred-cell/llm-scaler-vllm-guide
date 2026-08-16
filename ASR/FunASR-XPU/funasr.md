# Deploy FunASR model based intel GPU
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
