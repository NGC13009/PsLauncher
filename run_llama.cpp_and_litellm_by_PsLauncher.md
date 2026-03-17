# 如何通过PsLauncher配置本地大模型服务

> Please scroll down the page to view the **English version**

## 引言

我想在自己电脑上本地运行大模型, 并且一直使用[ollama](https://github.com/ollama/ollama). 偶然, 我发现相较于[llama.cpp](https://github.com/ggml-org/llama.cpp), ollama总是占用更多的显存, 因此我决定使用llama.cpp作为本地大模型部署后端(不可思议,因为ollama其实也是llama.cpp套了一层而已). 但是llama.cpp自身不支持多进程, 什么都得手工管理. 因此我考虑能不能自己造一个ollama类似的玩意帮我管理的更好一些.

我在之前写过一个项目: [ollama-launcher](https://github.com/NGC13009/ollama-launcher). 它的目的就是纯粹的一个后端管理软件, 并且要求轻量化且迅速. 因此我考虑能不能搞一个类似的东西去实现我的需求?

调研后, 我发现[litellm](https://github.com/BerriAI/litellm)是一个非常好的东西, 轻量化并且启动迅速, 这使得我没必要自己做一个网关去集散不同llama.cpp后端, 方便多了. 而且它不仅能管理本地模型并提供统一接口api, 而且还能把要钱的api也放到一起, 像是openrouter一样十分省事. 这样就不用来回配置多个程序的api了.

最开始, 我直接使用PowerShell的多个标签页, 通过启动写好配置的PowerShell脚本来手工启动litellm以及多个模型的llama.cpp. 我可以手工管理`GGUF`模型文件, 我觉得这无妨. 因此这个方案其实就能用了.

但是启动几个终端实在是不方便并且不够优雅, 并且我无法很方便的把他们扔到托盘后台去. 因此, 整合一下我们的目的....就诞生了这个程序.

因此, 这里我将介绍如何使用新的方法去配置本地大模型.

## 方法概览

事实上, 如果使用这个程序, 你有两种方式可以配置本地大模型.

1. 更方便的方式: 继续配置ollama, 方便的修改ollama的启动参数并在一处管理模型服务, 就像之前的[ollama-launcher](https://github.com/NGC13009/ollama-launcher)一样.
2. 性能更高, 自由度更高的方式: 使用性能更好, 但是自动化程度更低(自由度更高的)组合方式, 即我提到的 [llama.cpp](https://github.com/ggml-org/llama.cpp)+[litellm](https://github.com/BerriAI/litellm)模式

下面分开介绍两种方式.

## 更方便的ollama方式

我在最新版本的[ollama-launcher](https://github.com/NGC13009/ollama-launcher)中, 支持了一个菜单栏的功能, 允许你导出当前配置的启动参数与环境变量为一个脚本.

你需要把这个脚本放到某个文件夹下.

之后, 使用PsLauncher打开这个文件夹, 然后你应该能看见生成的脚本, `.ps1`或者`.bat`,随你所愿.

然后, 直接启动它, 就可以管理了. 并且假如你是从[ollama-launcher](https://github.com/NGC13009/ollama-launcher)迁移过来的, 那么操作仍然比较符合之前的习惯, 支持最小化到托盘, 以及启动停止守护进程.

不同的一点, 现在没有图像配置能让你快速配置ollama的选项了. 不过你可以编辑这个脚本, 然后该怎么配置就怎么配置, 自由度更高, 而且实际上并不会变得更麻烦.

即使你完全不知道脚本的语法, 靠着照猫画虎也能很好的应付.

## litellm网关 + llama.cpp 后端的方式

[llama.cpp](https://github.com/ggml-org/llama.cpp)和[ollama](https://github.com/ollama/ollama)最大的不同是, 它一次只能启动一个模型.

然而, ollama虽然是基于llama.cpp开发的, 但是开发团队对此进行了一些改进, 导致相较于llama.cpp, ollama需要更大的显存.

[litellm](https://github.com/BerriAI/litellm)是一个轻量化的项目, 可以在你的设备启动一个本地网关, 自动路由并转发各种模型的api接口, 就像openrouter一样. 它兼容llama.cpp, ollama, 甚至[openrouter](https://openrouter.ai/models?order=most-popular)以及openai格式的api提供商(例如[硅基流动](https://cloud.siliconflow.cn/me/models)).

因此使用这个方案, 你可以把多个api(本地的或者外地的)全部用litellm转发, 然后在自己电脑上从一个地方方便的调用所有各类模型. 我也更推荐这种方法(本地模型的性能..用过的都懂)

这个稍微复杂点, 不过你可以跟着我的方案走.

### 1. 安装uv

[uv](https://github.com/astral-sh/uv)是一个rust写的轻量化环境管理器(甚至比这个程序都小). uv可以安装一个完全独立于系统环境或者conda环境的Python. 请自行安装uv并确保它被配置到环境变量.

### 2. 安装litellm

使用 `uv` 来管理 Python 虚拟环境非常迅速且干净。为了达到你的要求，我们将在指定目录创建一个**独立的虚拟环境**，将 LiteLLM 安装在里面，并通过一个批处理脚本（`.bat`）直接调用该环境中的可执行文件。

以下是完整的图文/代码步骤，你可以直接打开 **PowerShell** 或 **CMD**（如果你没有 `C:\` 根目录的写入权限，请**以管理员身份运行**）来执行：

#### 2.1.创建目录并进入

在终端中依次输入以下命令，创建目标文件夹并进入：

```bash
mkdir C:\application\litellm
cd C:\application\litellm
```

#### 2.2. 使用 `uv` 创建专属环境并安装 LiteLLM

LiteLLM 作为路由服务（Proxy Server）运行时，需要一些额外的 Web 依赖（如 FastAPI 和 Uvicorn），因此我们安装带有 `[proxy]` 后缀的完整版：

```bash
# 1. 在当前目录创建一个专属的虚拟环境 (会生成一个 .venv 文件夹)
uv venv

# 2. 使用 uv 极速安装 litellm 代理服务到这个虚拟环境中
uv pip install "litellm[proxy]"
```

#### 2.3.创建一个默认配置文件

这个需要你自行查阅litellm的配置文件是怎么弄的. 或者, 快速开始, 用我的这个例子:

```yaml
# config.yaml
model_list:
  # llama.cpp
  - model_name: llama.cpp/qwen-vl-3.5-27b-nt
    litellm_params:
      model: openai/qwen-vl-3.5-27b-nt
      api_base: "http://127.0.0.1:13080/v1"
      api_key: "sk-123"
    model_info:
      max_tokens: 65536
      max_input_tokens: 65536
      max_output_tokens: 8192
      mode: "chat"
      supports_function_calling: true
      supports_reasoning: false
      supports_response_schema: true
      supports_system_messages: true
      supports_prompt_caching: true
      supports_vision: true

litellm_settings:
  drop_params: true
  telemetry: false
```

#### 2.4. 创建一键启动的脚本

受限于编码问题，如果有中文, 该脚本必须是 `GBK` 编码，如果用utf8大概率会乱码

```PowerShell
# 将当前工作目录切换到脚本所在的目录 (等同于 cd /d "%~dp0")
$ErrorActionPreference = 'Continue'

# [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 # Set console output encoding to UTF-8

Set-Location -Path $PSScriptRoot

# Write-Host 可以顺便加点颜色，看起来更直观
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "        正在启动 LiteLLM 路由服务...      " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 强制使用 host 127.0.0.1 保证安全性，并绑定端口 13043
if (Test-Path -Path "config.yaml") {
    Write-Host "[INFO] 找到 config.yaml，正在加载..." -ForegroundColor Green
    
    # 在 PowerShell 中运行外部可执行文件，推荐使用 "&" (调用操作符)
    & ".\.venv\Scripts\litellm.exe" --config config.yaml --host 127.0.0.1 --port 13043
} else {
    Write-Host "[ERROR] 找不到 config.yaml，请检查目录！" -ForegroundColor Red
}
```

如果你讨厌`PowerShell`, 那么使用`command`也可以:

```Batch
@echo off
:: cd to current path
cd /d "%~dp0"

echo ==========================================
echo          LiteLLM autostart ...
echo ==========================================

:: http://127.0.0.1:13043
if exist config.yaml (
    echo [INFO] get config.yaml ...
    .\.venv\Scripts\litellm.exe --config config.yaml --host 127.0.0.1 --port 13043
) else (
    echo [ERROR] No config.yaml here, check it!
)
```

litellm这就算准备好了.

#### 更新

如果你想更新litellm, 那么在当前位置运行:

```PowerShell
uv pip install --upgrade "litellm[proxy]"
```

### 3. 下载模型的gguf文件

很遗憾llama.cpp不支持管理模型, 因此你得自己去[modelscope](https://www.modelscope.cn/my/overview)或者[huggingface](https://huggingface.co/huggingface)下载模型的gguf文件.

比如对于这个例子, 是[unsloth/Qwen3.5-27B-GGUF](https://www.modelscope.cn/models/unsloth/Qwen3.5-27B-GGUF).

或者[点击这里](https://www.modelscope.cn/models/unsloth/Qwen3.5-27B-GGUF/file/view/master/Qwen3.5-27B-Q4_K_M.gguf?status=2)直接下载q4量化的版本.

这个模型支持视觉, 如果你希望添加视觉多模态, 还需要下载对应的[mmproj](https://www.modelscope.cn/models/unsloth/Qwen3.5-27B-GGUF/file/view/master/mmproj-BF16.gguf?status=2).

下载下来找个位置放下就行.

### 4. 安装llama.cpp

项目位置: [llama.cpp](https://github.com/ggml-org/llama.cpp)

进去直接release找个对应架构的zip, 下载, 解压到一个地方即可.

> llama.cpp 非常活跃, 一天能更新几十次, 不建议频繁跟随更新.

然后, 参考下面的启动脚本:

```PowerShell
# q3.5vl-27b.ps1
$ErrorActionPreference = 'Continue' # 遇见错误继续运行

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8 # 注意编码

# 如果你使用PsLauncher这个其实不是必要的, 因为本程序会自动按脚本路径执行脚本
$OLDPWD = $PWD
Set-Location -Path $PSScriptRoot
Write-Host "workpath change to: $PWD"

# 我有很多个显卡, 我只想用一个
Write-Host "Setting CUDA_VISIBLE_DEVICES=0" -ForegroundColor DarkCyan
$env:CUDA_VISIBLE_DEVICES = "0"

Write-Host "Launching llama.cpp-server..." -ForegroundColor Green # 一条提示信息

# 启动命令. 此处是我认为比较全的一种配置方案, 其他配置应该也不太改了吧. 需要修改参数, 从这里修改就行
# 请注意启动的llama-server.exe的路径, 你下载的版本不一定和我是一个版本!
& "./llama-b8267-bin-win-cuda-12.4-x64/llama-server.exe" `
    "-m" "E:\LLM\GGUF\Qwen3.5-27B-Q4_K_M.gguf" `
    "--mmproj" "E:\LLM\GGUF\q3.5-27b-mmproj-BF16.gguf" `
    "--threads" "1" `
    "--threads-batch" "1" `
    "-c" "8192" `
    "--temp" "0.7" `
    "--n-gpu-layers" "9999" `
    "-ctk" "f16" `
    "-ctv" "f16" `
    "--batch-size" "2048" `
    "--ubatch-size" "512" `
    "--flash-attn" "on" `
    "--fit" "off" `
    "--no-mmap" `
    "--mlock" `
    "--port" "13080" `
    "--reasoning-budget" "-1" # 加上视觉头只有0和-1

# 参数解释, 使用 llama-server.exe -h 可查看.
# -m                            # 启动的gguf路径
# --mmproj                      # 视觉头的路径, 如果你没下载视觉头, 请将它删除
# --threads" "1" `              # 线程数目. 我的电脑上线程数大于1反而变慢了(可能核间通信开销更大)
# --threads-batch" "1" `        # 批量数据预处理线程数目, 比如文本需要tokenizer之类的
# -c" "65536" `                 # 上下文长度
# --temp" "0.7" `               # 大模型温度系数
# --n-gpu-layers" "9999" `      # 加载进GPU的层数, 给大一些, 不然可能用cpu推理
# -ctk" "f16" `                 # kvcache 数据精度
# -ctv" "f16" `                 # kvcache 数据精度
# --batch-size" "2048" `        # 上下文切分长度, 以优化 kvcache 所需内存
# --ubatch-size" "512" `        # 上下文切分长度, 以优化 flash attention 所需内存
# --flash-attn" "on" `          # 开启 flash attention
# --fit" "off" `                # 不会进行任何显存妥协操作
# --no-mmap" `                  # 不进行磁盘映射 (会减速)
# --mlock" `                    # 内存锁页
# --port" "13080" `             # 暴露端口, 注意和litellm配置的要一样
# --reasoning-budget" "-1"      # 思考类模型的思考过程预算. 对于这个模型, 加上视觉头只有0(不思考)和-1(不设预算)可用

# 运行完了恢复之前的路径
Set-Location -Path $OLDPWD
```

把这个脚本找个文件夹存了即可.

如果你有多个本地模型, 那么参考这个, 多写几个启动llama.cpp的脚本, **注意监听端口号不要一样**.

### 5. 启动PsLauncher

把上面的这些脚本的位置载入, 然后运行, 启动litellm, 一个或者多个llama.cpp后端.

### 6. 其他程序接入方式

使用openai格式的api接入即可.

其实litellm不是必要的, 因为llama.cpp自己暴露的api其实就是openai格式的api, 同时也可以浏览器直接打开, 就是对话界面.

使用llama.cpp的api (其实就是兼容openai格式的):

```Bash
curl http://127.0.0.1:13080/v1
```

从litellm调用的话, 一个v1接口, 可以调用不同模型

```Bash
curl http://127.0.0.1:13043/v1/model/info   # 查看配置的模型
```

详细使用方法与功能说明, 参考litellm自己的文档即可.

------------------

## (English) How to Configure Local Large Model Services via PsLauncher

## Introduction

I want to run large models **locally** on my own computer and have been using [ollama](https://github.com/ollama/ollama). By chance, I found that ollama always consumes more video RAM (vRAM) compared to [llama.cpp](https://github.com/ggml-org/llama.cpp). So I decided to use llama.cpp as the backend for local large model deployment (surprising, since ollama is essentially just a wrapper around llama.cpp).

However, llama.cpp itself **does not support multi-processing**, and everything has to be managed manually. Therefore, I wondered if I could build something similar to ollama to help manage services more elegantly.

I previously wrote a project: [ollama-launcher](https://github.com/NGC13009/ollama-launcher). It is purely a backend management tool, designed to be lightweight and fast. So I considered building a similar tool to meet my needs.

After research, I found that [litellm](https://github.com/BerriAI/litellm) is an excellent choice — lightweight and fast to start. This saved me from building my own gateway to dispatch different llama.cpp backends. It not only manages local models and provides a unified API interface but also integrates paid APIs like OpenRouter, making it very convenient. No more switching API configurations across multiple applications.

At first, I used multiple tabs in PowerShell and manually started litellm and multiple llama.cpp instances via pre-configured PowerShell scripts. I was fine with managing `GGUF` model files myself, so this setup worked.

But launching several terminals was inconvenient and inelegant, and I could not easily minimize them to the system tray.

Thus, after combining all my goals… this program was born.

This article explains how to configure local large models using this new approach.

## Method Overview

With this program, you can configure local large models in two ways:

1. **Easier method**: Continue using ollama, conveniently modify ollama startup parameters, and manage model services from one place — just like the original [ollama-launcher](https://github.com/NGC13009/ollama-launcher).
2. **Higher performance & flexibility**: Use the more performant but less automated (more flexible) combination: [llama.cpp](https://github.com/ggml-org/llama.cpp) + [litellm](https://github.com/BerriAI/litellm).

We will cover both methods below.

## Easier Method: ollama

In the latest version of [ollama-launcher](https://github.com/NGC13009/ollama-launcher), I added a menu bar feature that lets you **export current startup parameters and environment variables as a script**.

You need to save this script to a folder.

Then open that folder with PsLauncher — you should see the generated script (`.ps1` or `.bat`, whichever you prefer).

Simply launch it to manage the service. If you are migrating from [ollama-launcher](https://github.com/NGC13009/ollama-launcher), the workflow will feel familiar: support for minimizing to the system tray, starting/stopping, and daemon processes.

The difference is that there is no longer a GUI for quickly configuring ollama options. However, you can edit the script directly to configure everything — with **greater freedom**, and it is actually not more complicated.

Even if you know nothing about scripting syntax, you can manage fine by following examples.

## Advanced Method: litellm Gateway + llama.cpp Backend

The biggest difference between [llama.cpp](https://github.com/ggml-org/llama.cpp) and [ollama](https://github.com/ollama/ollama) is that **llama.cpp can only run one model at a time**.

Although ollama is built on llama.cpp, the development team made modifications that cause ollama to require more vRAM than raw llama.cpp.

[litellm](https://github.com/BerriAI/litellm) is a lightweight project that runs a local gateway on your device, automatically routing and forwarding APIs for various models — much like OpenRouter. It is compatible with llama.cpp, ollama, and even OpenAI-compatible API providers (such as [SiliconFlow](https://cloud.siliconflow.cn/me/models)).

With this setup, you can route **all APIs (local or remote)** through litellm and access every model from a single endpoint on your computer. **I highly recommend this method** (local model performance speaks for itself).

This method is slightly more complex, but you can follow step by step.

### 1. Install uv

[uv](https://github.com/astral-sh/uv) is a lightweight environment manager written in Rust (even smaller than this program). uv can install a fully isolated Python environment, independent of system or Conda environments.

Please install uv yourself and ensure it is added to your system `PATH`.

### 2. Install litellm

Using `uv` to manage Python virtual environments is fast and clean. To meet your needs, we will create an **isolated virtual environment** in a specified directory, install LiteLLM inside it, and call the executable directly via a batch script (`.bat`).

Below are complete steps you can run directly in **PowerShell** or **CMD** (run as Administrator if you lack write access to `C:\`):

#### 2.1 Create and enter directory

```bash
mkdir C:\application\litellm
cd C:\application\litellm
```

#### 2.2 Create a dedicated environment and install LiteLLM

When running LiteLLM as a proxy server, it requires extra web dependencies (like FastAPI and Uvicorn), so we install the full version with the `[proxy]` suffix:

```bash
# Create a virtual environment in the current directory (generates a .venv folder)
uv venv

# Install litellm proxy into the virtual environment
uv pip install "litellm[proxy]"
```

#### 2.3 Create a default config file

You can check litellm’s documentation for details. Or use my quick-start example:

```yaml
# config.yaml
model_list:
  # llama.cpp
  - model_name: llama.cpp/qwen-vl-3.5-27b-nt
    litellm_params:
      model: openai/qwen-vl-3.5-27b-nt
      api_base: "http://127.0.0.1:13080/v1"
      api_key: "sk-123"
    model_info:
      max_tokens: 65536
      max_input_tokens: 65536
      max_output_tokens: 8192
      mode: "chat"
      supports_function_calling: true
      supports_reasoning: false
      supports_response_schema: true
      supports_system_messages: true
      supports_prompt_caching: true
      supports_vision: true

litellm_settings:
  drop_params: true
  telemetry: false
```

#### 2.4 Create a one-click startup script

Due to encoding limitations, if the script contains Chinese characters, it **must be saved in GBK**; UTF-8 will likely cause garbled text.

```PowerShell
# Switch working directory to the script's location (same as cd /d "%~dp0")
$ErrorActionPreference = 'Continue'

# [Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Set-Location -Path $PSScriptRoot

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host"        Starting LiteLLM Gateway...        " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Force host 127.0.0.1 for security, bind to port 13043
if (Test-Path -Path "config.yaml") {
    Write-Host "[INFO] Found config.yaml, loading..." -ForegroundColor Green

    # Use & (call operator) to run external executables in PowerShell
    & ".\.venv\Scripts\litellm.exe" --config config.yaml --host 127.0.0.1 --port 13043
} else {
    Write-Host "[ERROR] config.yaml not found! Please check the directory." -ForegroundColor Red
}
```

If you prefer `CMD` over PowerShell:

```Batch
@echo off
:: cd to current script directory
cd /d "%~dp0"

echo ==========================================
echo          LiteLLM autostart ...
echo ==========================================

:: http://127.0.0.1:13043
if exist config.yaml (
    echo [INFO] Found config.yaml ...
    .\.venv\Scripts\litellm.exe --config config.yaml --host 127.0.0.1 --port 13043
) else (
    echo [ERROR] No config.yaml here, check it!
)
```

litellm is now ready.

#### Updating litellm

To update litellm, run in the same directory:

```PowerShell
uv pip install --upgrade "litellm[proxy]"
```

### 3. Download GGUF model files

Unfortunately, llama.cpp does not manage models automatically. You must download GGUF files yourself from [ModelScope](https://www.modelscope.cn/my/overview) or [Hugging Face](https://huggingface.co/huggingface).

For this example, use [unsloth/Qwen3.5-27B-GGUF](https://www.modelscope.cn/models/unsloth/Qwen3.5-27B-GGUF).

Or download the Q4 quantized version directly:
[Qwen3.5-27B-Q4_K_M.gguf](https://www.modelscope.cn/models/unsloth/Qwen3.5-27B-GGUF/file/view/master/Qwen3.5-27B-Q4_K_M.gguf?status=2)

This model supports vision. If you want multimodal capabilities, also download the corresponding [mmproj](https://www.modelscope.cn/models/unsloth/Qwen3.5-27B-GGUF/file/view/master/mmproj-BF16.gguf?status=2) file.

Save them anywhere you like.

### 4. Install llama.cpp

Repository: [llama.cpp](https://github.com/ggml-org/llama.cpp)

Go to Releases, download a ZIP for your architecture, extract it somewhere.

> llama.cpp is updated very frequently — dozens of times a day. Frequent updates are not recommended.

Then use a startup script like this:

```PowerShell
# q3.5vl-27b.ps1
$ErrorActionPreference = 'Continue'

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Not strictly required in PsLauncher, since it runs scripts from their own path
$OLDPWD = $PWD
Set-Location -Path $PSScriptRoot
Write-Host "workpath changed to: $PWD"

# Use only one GPU if you have multiple
Write-Host "Setting CUDA_VISIBLE_DEVICES=0" -ForegroundColor DarkCyan
$env:CUDA_VISIBLE_DEVICES = "0"

Write-Host "Launching llama.cpp-server..." -ForegroundColor Green

# Startup command — this is a complete, optimized config
# Adjust paths and parameters to match your setup
& "./llama-b8267-bin-win-cuda-12.4-x64/llama-server.exe" `
    "-m" "E:\LLM\GGUF\Qwen3.5-27B-Q4_K_M.gguf" `
    "--mmproj" "E:\LLM\GGUF\q3.5-27b-mmproj-BF16.gguf" `
    "--threads" "1" `
    "--threads-batch" "1" `
    "-c" "8192" `
    "--temp" "0.7" `
    "--n-gpu-layers" "9999" `
    "-ctk" "f16" `
    "-ctv" "f16" `
    "--batch-size" "2048" `
    "--ubatch-size" "512" `
    "--flash-attn" "on" `
    "--fit" "off" `
    "--no-mmap" `
    "--mlock" `
    "--port" "13080" `
    "--reasoning-budget" "-1"

# Parameter explanations (run llama-server.exe -h for full list)
# -m                            # Path to GGUF model
# --mmproj                      # Path to multimodal projector (remove if not used)
# --threads" "1" `              # Number of threads ( >1 may slow down on some CPUs )
# --threads-batch" "1" `        # Threads for batch tokenization
# -c" "65536" `                 # Context length
# --temp" "0.7" `               # Temperature
# --n-gpu-layers" "9999" `      # Layers to offload to GPU (set high to maximize GPU usage)
# -ctk" "f16" `                 # K-cache data type
# -ctv" "f16" `                 # V-cache data type
# --batch-size" "2048" `        # Context chunk size for KV-cache memory optimization
# --ubatch-size" "512" `        # Context chunk size for Flash Attention
# --flash-attn" "on" `          # Enable Flash Attention
# --fit" "off" `                # Disable VRAM compromise
# --no-mmap" `                  # Disable memory mapping (slower, but stable)
# --mlock" `                    # Lock model in memory
# --port" "13080" `             # Listening port — must match litellm config
# --reasoning-budget" "-1"      # Reasoning budget for thought models. With vision, only 0 (disable) or -1 (unlimited) work here

# Restore previous directory
Set-Location -Path $OLDPWD
```

Save this script in a folder.

If you want multiple local models, write multiple similar llama.cpp startup scripts — **just use different ports**.

### 5. Launch PsLauncher

Load the folder containing your scripts, then run:

- litellm gateway
- one or more llama.cpp backends

### 6. Connect from other applications

Use the **OpenAI-compatible API**.

litellm is not strictly required, because llama.cpp already exposes an OpenAI-compatible API and even includes a web chat UI.

Direct llama.cpp API (OpenAI-compatible):

```Bash
curl http://127.0.0.1:13080/v1
```

Via litellm (one API for all models):

```Bash
curl http://127.0.0.1:13043/v1/model/info   # List configured models
```

For full usage and features, refer to the official litellm documentation.
