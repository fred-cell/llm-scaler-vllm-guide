## Download DeepSeek-OCR-2 from Huggingface or other model Repository
```
intel/
├──LLM-Models/
│  └──DeepSeek-OCR-2/
└──llm-serving/
   ├──start-docker.sh
   └──vllm-deepseek-ocr-2-openapikey.sh
```
## Startup vllm serving container
```bash
#!/bin/bash

sudo docker run -td --privileged --net=host \
        --device=/dev/dri \
        --name=llm-serving \
        -v /home/intel/LLM-Models:/llm/models/ \
        -v /home/intel/llm-serving:/llm/scripts \
        -e no_proxy=localhost,127.0.0.1 \
        --shm-size="32g" \
        --entrypoint /bin/bash \
        intel/llm-scaler-vllm:0.21.0-b1
```
## Deploy DeepSeek-OCR-2 Serving
```bash
docker exec -it llm-serving bash
```
```bash
cd /llm
mkdir media
```
通过脚本vllm-deepseek-ocr-2-openaikey.sh部署OCR服务
```bash
#!/bin/bash
#
model_name=DeepSeek-OCR-2

export VLLM_ALLOW_LONG_MAX_MODEL_LEN=1
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export VLLM_OFFLOAD_WEIGHTS_BEFORE_QUANT=1

vllm serve --model /llm/models/$model_name \
        --served-model-name $model_name \
        --port 8001 \
        --host 0.0.0.0 \
        --gpu-memory-util 0.9 \
        --max-model-len 8192 \
        --block-size 64 \
        --dtype float16 \
        --enforce-eager \
        --api-key intel123 \
        --trust-remote-code \
        --enable-prompt-tokens-details \
        --tensor-parallel-size 1 \
        --no-enable-prefix-caching \
        --mm-processor-cache-gb 0 \
        --max-num-seqs 10 \
        --quantization fp8 \
        --logits_processors vllm.model_executor.models.deepseek_ocr:NGramPerReqLogitsProcessor \
        --allowed-local-media-path /llm/media
```
在容器里启动脚本
```bash
cd /llm/scripts
bash vllm-deepseek-ocr-2-openapikey.sh
```
### Client request service



#### Common Prompt Template
|Task Mode|English Prompt|
|----|----|
|文档转 Markdown（带布局）|<image>\n<$#124;grounding &#124; >Convert the document to markdown.|
|无布局纯文本 OCR|```<image>\n10Free OCR.```|
|其他图像（带布局）|```<image>\n<|grounding|>OCR this image.```|
|解析图表|```<image>\nParse the figure.```|
|通用图像描述|```<image>\nDescribe this image in detail.```|
|目标定位|```<image>\nLocate <|ref|>xxxx<|/ref|> in the image.```|

