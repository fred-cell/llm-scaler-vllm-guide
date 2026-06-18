# B70 PP=2 / TP=2 256K 性能对比报告

## 1. 测试配置

| 项目 | 配置 |
|---|---|
| 测试日期 | 2026-06-16 |
| 测试服务器 | 192.168.10.13 |
| 模型 | `/llm/models/Qwen3.6-35B-A3B` |
| 服务模型名 | `qwen36_35b_fp8` |
| 推理镜像 | `intel/llm-scaler-vllm:0.14.0-b8.3.1` |
| vLLM / llm-scaler 版本 | `0.14.1.dev0+gb17039bcc.d20260605` |
| 测试工具 | `C:\Users\86186\Downloads\test-model v2.5.0\test_model.py` |
| 测试模式 | performance + concurrent + streaming + batch + temperature + long-output |
| 上下文长度 | 64 到 262144 tokens |
| 目标 max_model_len | 271360，满足 256K 输入 + 约 1K 输出测试要求 |

启动公共参数：

```bash
--max-model-len 271360
--max-num-batched-tokens 8192
--kv-cache-dtype fp8
--quantization fp8
--dtype=float16
--gpu-memory-utilization 0.88
--enforce-eager
--language-model-only
--skip-mm-profiling
--enable-auto-tool-choice
--tool-call-parser qwen3_xml
--disable-sliding-window
--disable-log-requests
```

PC 平台宏配置：

```bash
CCL_SYCL_ALLREDUCE_SIMPLE_THRESHOLD=4294967296
CCL_SYCL_REDUCE_SCATTER_SIMPLE_THRESHOLD=4294967296
CCL_SYCL_ALLGATHERV_SIMPLE_THRESHOLD=4294967296
CCL_SYCL_ALLTOALL_TMP_BUF=1
```

并行配置：

| 模式 | 参数 |
|---|---|
| PP=2 | `--pipeline-parallel-size 2` |
| TP=2 | `--tensor-parallel-size 2` |

## 2. 服务启动与 KV Cache

| 指标 | PP=2 | TP=2 |
|---|---:|---:|
| Tensor Parallel | 1 | 2 |
| Pipeline Parallel | 2 | 1 |
| GPU KV cache size | 393,216 tokens | 466,944 tokens |
| 271,360 tokens/request 最大并发 | 5.67x | 6.71x |
| 权重加载后显存峰值 | GPU0 18.96 GiB / GPU1 19.91 GiB | GPU0 17.96 GiB / GPU1 17.96 GiB |
| Model memory usage | GPU0 17.67 GB / GPU1 18.62 GB | GPU0 17.30 GB / GPU1 17.30 GB |

说明：`max_model_len=271360` 高于模型配置中的 `max_position_embeddings=262144`，服务日志有风险提示。本次 test-model 的实际最大输入上下文为 262144 tokens，额外长度用于保留输出空间。

## 3. 单路上下文性能

| Context | PP TTFT(s) | PP TPS | TP TTFT(s) | TP TPS | TP TPS 相对 PP | TP TTFT 相对 PP |
|---:|---:|---:|---:|---:|---:|---:|
| 64 | 0.815 | 73.35 | 0.516 | 67.78 | -7.6% | -36.7% |
| 128 | 0.203 | 74.76 | 0.118 | 67.67 | -9.5% | -41.9% |
| 256 | 0.269 | 73.48 | 0.172 | 67.77 | -7.8% | -36.1% |
| 512 | 0.123 | 73.22 | 0.115 | 67.46 | -7.9% | -6.5% |
| 1024 | 0.126 | 72.93 | 0.134 | 67.41 | -7.6% | +6.3% |
| 2048 | 0.162 | 72.74 | 0.225 | 67.32 | -7.5% | +38.9% |
| 4096 | 0.299 | 73.18 | 0.376 | 67.07 | -8.3% | +25.8% |
| 8192 | 2.323 | 71.36 | 2.621 | 66.97 | -6.2% | +12.8% |
| 16384 | 0.687 | 71.15 | 1.235 | 67.11 | -5.7% | +79.8% |
| 32768 | 1.242 | 66.80 | 2.424 | 66.51 | -0.4% | +95.2% |
| 65536 | 2.364 | 61.30 | 5.057 | 66.00 | +7.7% | +113.9% |
| 131072 | 5.467 | 52.69 | 11.281 | 63.45 | +20.4% | +106.3% |
| 262144 | 15.008 | 41.18 | 27.188 | 59.70 | +45.0% | +81.2% |

结论：短上下文 PP=2 的 decode TPS 更高；上下文达到 64K 以后 TP=2 的 TPS 开始反超，256K 时 TP=2 比 PP=2 高约 45%。但 TP=2 的长上下文 TTFT 明显更高，256K TTFT 为 27.188s，PP=2 为 15.008s。

## 4. 并发性能摘要

| Context | 并发 | PP TPS | PP TTFT(s) | TP TPS | TP TTFT(s) |
|---:|---:|---:|---:|---:|---:|
| 512 | 1 | 73.81 | 0.108 | 67.52 | 0.102 |
| 512 | 2 | 57.82 | 0.132 | 44.07 | 0.135 |
| 512 | 4 | 44.08 | 0.164 | 38.22 | 0.202 |
| 512 | 8 | 31.67 | 0.245 | 31.68 | 0.358 |
| 32768 | 1 | 67.18 | 1.220 | 66.74 | 2.409 |
| 32768 | 2 | 54.90 | 1.770 | 42.56 | 4.540 |
| 32768 | 4 | 41.98 | 2.642 | 33.63 | 7.200 |
| 32768 | 8 | 31.14 | 3.972 | 24.88 | 11.772 |
| 65536 | 1 | 62.11 | 2.351 | 66.11 | 5.060 |
| 65536 | 2 | 43.88 | 3.339 | 39.15 | 8.510 |
| 65536 | 4 | 30.20 | 4.982 | 29.35 | 13.512 |
| 65536 | 8 | 25.99 | 8.421 | 20.76 | 23.751 |
| 131072 | 1 | 52.73 | 5.449 | 63.59 | 11.288 |
| 131072 | 2 | 32.88 | 7.943 | 34.47 | 17.354 |
| 131072 | 4 | 27.11 | 12.707 | 22.88 | 28.866 |
| 131072 | 8 | 16.93 | 22.724 | 15.12 | 52.589 |
| 262144 | 1 | 40.47 | 14.984 | 59.78 | 27.247 |
| 262144 | 2 | 29.93 | 22.227 | 27.55 | 40.873 |
| 262144 | 4 | 16.14 | 36.992 | 16.17 | 68.813 |
| 262144 | 8 | 9.39 | 68.691 | 9.30 | 127.546 |

并发测试全部成功，成功率均为 100%。256K 场景下，TP=2 单路 TPS 优势明显；并发 4/8 时 PP 与 TP 的单路 TPS 接近，但 TP 的 TTFT 明显更高。

## 5. GPU 频率、显存与降频观察

| 模式 | GPU | 采样数 | 平均频率 | 频率范围 | 平均显存 | 峰值显存 | 平均功耗 | 峰值功耗 | Throttle |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| PP=2 | 0 | 963 | 1936.0 MHz | 0-2800 MHz | 27.97 GiB | 28.00 GiB | 130.3 W | 293.1 W | 857 次 Not Throttled，少量 Burst Power Excursion |
| PP=2 | 1 | 962 | 1949.3 MHz | 0-2800 MHz | 29.36 GiB | 29.36 GiB | 132.7 W | 287.3 W | 937 次 Not Throttled，少量 Burst Power Excursion |
| TP=2 | 0 | 830 | 2767.6 MHz | 400-2800 MHz | 30.01 GiB | 30.01 GiB | 158.3 W | 226.6 W | 823 次 Not Throttled，7 次 Burst Power Excursion |
| TP=2 | 1 | 829 | 2767.5 MHz | 517-2800 MHz | 29.30 GiB | 29.30 GiB | 153.9 W | 221.2 W | 829 次 Not Throttled |

观察：TP=2 测试期间 GPU 平均频率接近 2800 MHz，未看到持续降频。PP=2 平均频率较低，主要与 pipeline 并行阶段性空闲有关，非持续热/功耗降频特征；日志中出现少量 `Burst Power Excursion`，但主状态仍以 `Not Throttled` 为主。


## 6. 原始文件

| 类型 | 路径 |
|---|---|
| PP=2 test-model 报告 | `qwen36_35b_fp8_b70_pp2_mml271360_fp8kv_v25_perf_report_20260616.md` |
| PP=2 stdout | `qwen36_35b_fp8_b70_pp2_mml271360_fp8kv_v25_perf_stdout_20260616.log` |
| PP=2 服务与 xpu 日志 | `pp2_logs/` |
| TP=2 test-model 报告 | `qwen36_35b_fp8_b70_tp2_mml271360_fp8kv_v25_perf_report_20260616.md` |
| TP=2 stdout | `qwen36_35b_fp8_b70_tp2_mml271360_fp8kv_v25_perf_stdout_20260616.log` |
| TP=2 服务与 xpu 日志 | `tp2_logs/` |

