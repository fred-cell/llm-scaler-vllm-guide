import os, tempfile, asyncio
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from funasr import AutoModel
from fastapi.security import OAuth2PasswordBearer
import traceback
import torch
import logging
import time

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("sensevoice-api")

app = FastAPI()
lock = asyncio.Lock()

asr_model = AutoModel(
    model="/home/intel/LLM-Models/SenseVoiceSmall",
    device="xpu"
)

# 自检：打印模型真实设备
logger.info("==== XPU 设备检测 ====")
logger.info(f"torch.xpu.is_available(): {torch.xpu.is_available()}")
try:
    param_device = next(asr_model.model.model.parameters()).device
    logger.info(f"SenseVoiceSmall 模型权重所在设备: {param_device}")
except Exception as e:
    logger.warning(f"获取模型设备失败: {str(e)}")

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
    start_time = time.time()
    logger.info(f"收到识别请求 | 文件名:{file.filename}, model_name:{model_name}, language:{language}")

    audio_bytes = await file.read()
    suffix = os.path.splitext(file.filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(audio_bytes)
        tmp_path = f.name
    logger.info(f"临时音频文件: {tmp_path}")

    try:
        async with lock:
            # 将同步funasr推理丢入线程池，不阻塞uvicorn事件循环
            res = await asyncio.to_thread(asr_model.generate, input=tmp_path)
        text = res[0]["text"] if isinstance(res, list) else res["text"]
        cost = round(time.time() - start_time, 3)
        logger.info(f"识别完成 | 耗时:{cost}s |识别结果: {text}")
    except Exception as e:
        err_msg = traceback.format_exc()
        logger.error(f"识别异常:\n{err_msg}")
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
    logger.info("SenseVoice ASR 服务启动, 监听0.0.0.0:8005")
    uvicorn.run(app, host="0.0.0.0", port=8005)
