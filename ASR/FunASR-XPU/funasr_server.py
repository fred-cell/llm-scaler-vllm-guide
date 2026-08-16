import os, tempfile, asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from funasr import AutoModel
from fastapi.security import OAuth2PasswordBearer
import traceback

app = FastAPI()
lock = asyncio.Lock()

asr_model = AutoModel(
    model="/home/intel/LLM-Models/SenseVoiceSmall",
    device="XPU"
)

VALID_API_KEY="intel123"
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

async def verify_api_key(token: str = Depends(oauth2_scheme)):
    if token != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token

@app.post("/v1/audio/transcriptions")
async def transcriptions(
    file: UploadFile = File(...),
    model_name: str = Form("sensevoice"),
    language: str = Form(None),
    response_format: str = Form("json"),
    prompt: str = Form(None),
    temperature: float = Form(0),
    _auth = Depends(verify_api_key)
):
    audio_bytes = await file.read()
    suffix = os.path.splitext(file.filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    try:
        async with lock:
            # 将同步funasr推理丢入线程池，不阻塞uvicorn事件循环
            res = await asyncio.to_thread(asr_model.generate, input=tmp_path)
        text = res[0]["text"] if isinstance(res, list) else res["text"]
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.unlink(tmp_path)

    if response_format == "verbose_json":
        return {
            "task": "transcription",
            "language": language or "zh",
            "duration": 0.0,
            "text": text,
        }
    return {"text": text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
