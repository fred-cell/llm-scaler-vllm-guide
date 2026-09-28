# Intel Arc B70 + llama.cpp Vulkan 后端运行指南

> 适用平台：Windows 11 | GPU：Intel Arc B70 | 后端：Vulkan

---

## 目录

1. 准备工作
2. 安装 Intel Arc B70 驱动
3. 下载并配置 llama.cpp（Vulkan 版）
4. 下载模型文件
5. 启动 llama-server（推理服务）
6. 运行 llama-bench（性能基准测试）
7. 运行 llama-completion（命令行补全测试）
8. 常见问题排查
9. 参数说明速查表

---

## 1. 准备工作

在开始之前，请确认以下环境已就绪：

- Windows 11
- Intel Arc B70 显卡已正确安装
- 至少 **16 GB 系统内存**（运行 35B 模型时建议 32 GB+）
- 模型文件（`.gguf` 格式），本指南以 `Qwen3.6-35B-A3B-Q4_K_M.gguf` 为例
- 网络连接（下载驱动和 llama.cpp）

---

## 2. 安装 Intel Arc B70 驱动

**必须安装最新驱动**，旧版驱动可能导致 Vulkan 后端无法识别 GPU 或性能低下。

### 2.1 下载驱动

访问官方下载页面：

```
https://www.intel.com/content/www/us/en/download/785597/intel-arc-graphics-windows.html
```

点击页面上的 **Download** 按钮，下载最新版 `.exe` 安装包。

### 2.2 安装驱动

1. 双击安装包
2. 按照向导完成安装，安装过程中屏幕可能短暂变黑，属正常现象
3. 安装完成后**重启电脑**

### 2.3 验证驱动安装

重启后，打开 **设备管理器**（Win + X → 设备管理器），在 **显示适配器** 下应看到：

```
Intel(R) Arc(TM) B70 Graphics
```

同时，验证 Vulkan 支持：

```powershell
# 在 PowerShell 中运行（需要先安装 Vulkan SDK 或使用随驱动安装的工具）
vulkaninfo | findstr "deviceName"
```

或直接跳到第 3 步，运行 llama.cpp 时若能正常调用 GPU 即说明 Vulkan 工作正常。

---

## 3. 下载并配置 llama.cpp（Vulkan 版）

### 3.1 下载 llama.cpp Release 包

访问 GitHub Releases 页面下载最新 Vulkan 版本：

```
https://github.com/ggml-org/llama.cpp/releases
```

**示例下载链接（b9222 版本）：**

```
https://github.com/ggml-org/llama.cpp/releases/download/b9222/llama-b9222-bin-win-vulkan-x64.zip
```

> **提示：** 建议前往 Releases 页面查找最新版本号替换 `b9222`，以获得最新修复和性能优化。

### 3.2 解压文件

1. 将下载的 `.zip` 文件解压到一个**路径不含中文或空格**的目录，例如：

```
C:\llama\
```

解压后目录结构大致如下：

```
C:\llama\
├── llama-server.exe
├── llama-bench.exe
├── llama-cli.exe
├── llama-run.exe
├── vulkan-1.dll
├── ggml.dll
└── ... (其他 DLL 文件)
```

### 3.3 将模型文件放置到合适位置

将 `.gguf` 模型文件放入 llama.cpp 同级目录或子目录，例如：

```
C:\llama\models\Qwen3.6-35B-A3B-Q4_K_M.gguf
```

---

## 4. 启动 llama-server（推理服务）

`llama-server` 提供兼容 OpenAI API 格式的 HTTP 服务，方便与各类客户端（如 Open WebUI、Chatbox 等）对接。

### 4.1 打开命令行

按 `Win + R`，输入 `cmd`，进入命令提示符，切换到 llama.cpp 目录：

```cmd
cd C:\llama
```

### 4.2 启动命令

```cmd
llama-server.exe -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf -ngl 999 -rea off -c 66560 -fa on
```

**参数说明：**

| 参数 | 值 | 说明 |
|------|----|------|
| `-m` | `models\Qwen3.6-35B-A3B-Q4_K_M.gguf` | 模型文件路径 |
| `-ngl` | `999` | 将尽可能多的层卸载到 GPU（B70 显存允许范围内自动适配） |
| `-rea` | `off` | 关闭reasoning |
| `-c` | `66560` | 上下文长度（约 64K token，适合长文本任务） |
| `-fa` | `on` | 启用 Flash Attention，减少显存占用，提升长上下文推理速度 |

可选：--cache-type-k q8_0 --cache-type-v q8_0  kv cache int8量化，减少显存消耗

### 4.3 成功启动的标志

看到如下输出即表示服务已正常运行：

```
llama_prepare_model_devices: using device Vulkan1 (Intel(R) Arc(TM) Pro B70 Graphics) (unknown id) - 31787 MiB free
...
srv          init: init: chat template, thinking = 0
main: model loaded
main: server is listening on http://127.0.0.1:8080
```

### 4.4 访问 Web UI

打开浏览器，访问：

```
http://127.0.0.1:8080
```

也可通过 API 进行调用：

```
http://127.0.0.1:8080/v1/chat/completions
```



---

## 5. 运行 llama-bench（性能基准测试）

`llama-bench` 用于测量模型的推理吞吐量（token/s），是评估 B70 实际性能的最直接工具。但`llama-bench`测试出来的解码速率是估计的理想值，在长上下文的场景中不适用。

### 5.1 基础测试

```cmd
llama-bench.exe -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf -ngl 999 -fa 1
```

### 5.2 完整测试（测试不同 prompt/生成长度组合）

```cmd
llama-bench.exe ^
  -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf ^
  -ngl 999 ^
  -fa 1 ^
  -p 512,1024 ^
  -n 128,256 ^
  -r 3
```

**参数说明：**

| 参数 | 说明 |
|------|------|
| `-p 512,1024` | 测试 512 和 1024 token 的 prompt 处理（prefill）速度 |
| `-n 128,256` | 测试生成 128 和 256 token 的速度（decode） |
| `-r 3` | 每个组合重复测试 3 次取平均值，结果更稳定 |

### 5.3 输出结果示例

```
| model                          |       size | backend  | ngl |   test |         t/s |
| ------------------------------ | ---------: | -------- | --: | -----: | ----------: |
| qwen3 35B Q4_K_M               |  21.56 GiB | Vulkan   | 999 | pp 512 |   xxx.xx ± x.xx |
| qwen3 35B Q4_K_M               |  21.56 GiB | Vulkan   | 999 | tg 128 |   xx.xx ± x.xx |
```

- **pp**（prompt processing）：prefill 速度，越高越好
- **tg**（token generation）：生成速度，直接影响用户体验，越高越好

---

## 6. 运行 llama-completion（命令行补全测试）

 `llama-completion.exe`用于快速在命令行中测试模型的单次补全输出。

> **注意：** 在不同版本的 llama.cpp 中，该工具可能名为 `llama-cli.exe` 或 `llama-run.exe`，请根据解压后实际文件名调整。

### 6.1 基础补全测试

```cmd
llama-completion.exe ^
  -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf ^
  -ngl 999 ^
  -fa on^
  -p "Hello, please introduce yourself." ^
  -n 200
```



### 6.3 常用参数说明

| 参数 | 说明 |
|------|------|
| `-p "文本"` | 指定 prompt 内容 |
| `-n 200` | 最多生成 200 个 token |
| `-i` | 进入交互（对话）模式 |
| `--temp 0.7` | 设置采样温度（0.0 = 确定性输出） |
| `--top-p 0.9` | Top-P 采样参数 |

---

## 7. 常见问题排查

### Q1：启动时提示找不到 Vulkan 设备

**症状：** 输出 `No Vulkan devices found` 或 `ggml_vulkan: no devices`

**解决方法：**
1. 确认驱动已重新安装并重启
2. 以管理员身份运行命令提示符
3. 检查设备管理器中 B70 是否显示正常（无感叹号）
4. 确认下载的是 `vulkan` 版本的 llama.cpp，而非 CUDA 或 CPU 版本

---

### Q2：显存不足（Out of Memory）

**症状：** 报错 `VRAM: not enough memory` 或程序崩溃

**解决方法：**
1. 降低 `-ngl` 值（如改为 `-ngl 40`），减少卸载到 GPU 的层数
2. 降低上下文长度（如 `-c 32768` 或 `-c 16384`）
3. 确认已开启 Flash Attention（`-fa on`）以节省显存或者kv cache量化
4. 关闭其他占用显存的程序

---

### Q3：推理速度很慢，接近 CPU 速度

**症状：** token 生成速度 < 1 token/s 或 `offloaded 0 layers to GPU`

**解决方法：**
1. 查看输出中是否有 `offloading XX layers to GPU` 的提示
2. 确认 `-ngl` 参数已正确传入
3. 重新安装驱动，确保 Vulkan 运行时已正确注册

---

### Q4：llama-server 启动后立即退出

**症状：** 服务启动后不到 1 秒退出，无报错

**解决方法：**
1. 检查模型文件路径是否正确，路径中不要有中文
2. 验证 `.gguf` 文件完整性（下载时可能中断）
3. 尝试添加 `--verbose` 参数查看详细日志

---

### Q5：API 无响应或返回错误

**症状：** 访问 `http://127.0.0.1:8080` 无法打开

**解决方法：**
1. 确认服务仍在运行（终端窗口未关闭）
2. 检查 Windows 防火墙是否阻止了 8080 端口
3. 尝试使用 `--port 8081` 换一个端口

---

## 8. 参数说明速查表

### llama-server / llama-cli 通用参数

| 参数 | 含义 | 推荐值 |
|------|------|--------|
| `-m <路径>` | 模型文件路径 | 填写实际路径 |
| `-ngl <N>` | GPU 层数卸载 | `999`（全部） |
| `-c <N>` | 上下文窗口大小 | `66560` / `32768` |
| `-fa` / `-fa on` | 启用 Flash Attention | 推荐开启 |
| `-rea off` | 关闭 RoPE 自适应 | 部分模型需关闭 |
| `-t <N>` | CPU 线程数 | 保持默认 |
| `--temp <F>` | 采样温度 | `0.7` |
| `-n <N>` | 最大生成长度 | `-1`（无限制） |

### llama-bench 专用参数

| 参数 | 含义 |
|------|------|
| `-p <N,...>` | Prompt 长度列表 |
| `-n <N,...>` | 生成长度列表 |
| `-r <N>` | 每组测试重复次数 |
| `-o csv` | 输出 CSV 格式结果 |

---

## 附录：快速命令参考

```cmd
:: 启动推理服务（完整命令）
llama-server.exe -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf -ngl 999 -rea off -c 66560 -fa on

:: 性能基准测试
llama-bench.exe -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf -ngl 999 -fa 1 -p 512 -n 128 -r 3


:: 单次补全测试
llama-completion.exe -m models\Qwen3.6-35B-A3B-Q4_K_M.gguf -ngl 999 -fa -p "你好，请介绍一下自己。" -n 200
```

---

*指南版本：2025 | 适配 llama.cpp b9222+ | Intel Arc B70*
