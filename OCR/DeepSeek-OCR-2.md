## Download DeepSeek-OCR-2 from Huggingface or other model Repository
```
intel\
|----LLM-Models/
| |----DeepSeek-OCR-2/
|----llm-serving/
| |----start-docker.sh
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
