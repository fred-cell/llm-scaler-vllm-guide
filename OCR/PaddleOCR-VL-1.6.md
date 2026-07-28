## Download DeepSeek-OCR-2 from Huggingface or other model Repository
```
intel/
├──LLM-Models/
│  └──PaddleOCR-VL-1.6/
└──llm-serving/
   ├──start-docker.sh
   └──vllm-paddleocr-vl-1.6-openapikey.sh
```
## Startup vllm serving container
start-docker.sh script is as below:
```bash
#!/bin/bash

sudo docker run -td --privileged --net=host \
        --device=/dev/dri \
        --name=ocr-serving \
        -v /home/intel/LLM-Models:/llm/models/ \
        -v /home/intel/llm-serving:/llm/scripts \
        -e no_proxy=localhost,127.0.0.1 \
        --shm-size="32g" \
        --entrypoint /bin/bash \
        intel/llm-scaler-vllm:0.21.0-b1
```
## Deploy DeepSeek-OCR-2 Serving
```bash
docker exec -it ocr-serving bash
```
```bash
cd /llm
mkdir media
```
