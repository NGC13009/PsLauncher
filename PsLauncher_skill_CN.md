
# PsLauncher HTTP API 技能（AI Agent 专用）

本说明书包含AI AGENT工作所需的所有配置，如果你是ai，那么本文档是完备的。

对于人类用户需要的GUI操作说明，如果人类需要，请提示人类查阅PsLauncher的[完整说明书](https://github.com/NGC13009/PsLauncher.git)。

## 1. 功能定位

PsLauncher 是本地脚本编排器，通过 HTTP API 对 PowerShell / Bash / Batch 脚本进行：

- 异步启动/终止/批量回收进程
- 查询实时输出与历史日志
- 向运行中的脚本注入输入
- 统一管理多个本地服务进程（llama.cpp / Ollama / LiteLLM 等）
AI Agent 通过 HTTP API 与 PsLauncher 交互，**不依赖 GUI，也不阻塞 Agent loop**。

## 2. 服务端点与认证

### 默认地址

- 启动后默认在 `127.0.0.1:13025` 提供 HTTP API。如果无法访问，请提示用户修改本skill.md的这里的说明，配置正确的路径。
- 可通过 `--headless` 启动纯 API 模式，不显示 GUI。

### 认证（可选）

配置文件 `config.json` 中 `api.auth_token` 非空时，所有请求需携带：

```http
Authorization: Bearer <your-token>
```

否则返回 `401 Unauthorized`。

如果需要鉴权，请提示用户修改本skill.md的这里的说明，配置正确的令牌。

### 美化输出（调试用）

所有端点支持查询参数 `?pretty=true`，返回格式化 JSON（适合人类查看）；不带 `pretty` 时为紧凑 JSON，便于程序解析。你应该根据当前任务类型使用正确的参数。

## 3. API 端点一览

> 所有端点支持 `POST`，查询类同时支持 `GET`。

### 状态与帮助

- `GET/POST /status`  
  - 查看服务整体状态  
  - 无请求体，无参数。
- `GET /help`  
  - 返回 HTML 形式帮助页面（人类用）。
- `POST /help`  
  - 返回所有可用端点的结构化列表（适合作为调用模板）。

### 路径管理（脚本目录）

- `GET/POST /folders`  
  - 获取当前扫描的所有脚本文件夹路径列表。
- `POST /folder/add`  
  - 请求体：`{"path": "C:/scripts"}`  
  - 将新文件夹加入扫描列表。
- `POST /folder/remove`  
  - 请求体：`{"path": "C:/scripts"}`  
  - 从扫描列表移除指定文件夹。

### 脚本列表与运行

- `GET/POST /scripts`  
  - 可选查询参数：`?folder=<绝对路径>`  
  - 返回该文件夹下可运行脚本列表（仅 `.ps1/.bat/.sh`）。
- `POST /script/run`  
  - 请求体：  

    ```json
    {
      "folder": "C:/scripts",
      "script": "test0.ps1"
    }
    ```  

  - 在新终端标签页运行脚本，返回终端信息（含 `id`）。

### 终端进程管理

- `GET/POST /terminals`  
  - 返回所有终端列表，每个终端包含：  
    - `id`：整数 ID  
    - `name`：脚本名称  
    - 状态等元数据。
- `POST /terminal/stop`  
  - 请求体：  

    ```json
    { "id": 0 }
    ```  

    或  

    ```json
    { "name": "test0.ps1" }
    ```  

  - 强制终止指定终端及其子进程树（强杀，无残留）。
- `POST /terminal/stop_all`  
  - 无请求体  
  - 终止所有运行中的终端进程。

### 输出与输入

- `GET/POST /terminal/output`  
  - 查询参数：`?id=0` 或 `?name=test0.ps1`  
  - 返回该终端的完整输出（累积日志）。
- `POST /terminal/clear`  
  - 请求体：`{ "id": 0 }`  
  - 清空该终端的输出缓冲（不影响进程）。
- `POST /terminal/input`  
  - 请求体：  

    ```json
    {
      "id": 0,
      "text": "hello\n"
    }
    ```  

  - 将字符串注入到运行脚本的标准输入（交互式脚本用）。

### 关闭 PsLauncher

- `GET/POST /shutdown`  
  - 无参数  
  - 安全关闭 PsLauncher（会先尝试停止所有运行中的脚本）。

## 4. 调用模式与示例（curl 模板）

以下为典型调用流程（AI Agent 可直接按此模式生成 HTTP 请求）。

### 4.1 基础调用模板（假设未配置 auth_token）

```bash
# 查看状态
curl http://127.0.0.1:13025/status
# 获取端点结构列表（便于生成请求体）
curl -X POST http://127.0.0.1:13025/help?pretty=true
```

### 4.2 管理脚本目录

```bash
# 添加脚本目录
curl -X POST http://127.0.0.1:13025/folder/add \
  -H "Content-Type: application/json" \
  -d '{"path":"C:/scripts"}'
# 查看已添加目录
curl http://127.0.0.1:13025/folders
# 列出某目录下可运行脚本
curl "http://127.0.0.1:13025/scripts?folder=C:/scripts"
```

### 4.3 启动并管理脚本进程

```bash
# 运行脚本（假设目录为 C:/scripts，脚本为 test0.ps1）
curl -X POST http://127.0.0.1:13025/script/run \
  -H "Content-Type: application/json" \
  -d '{"folder":"C:/scripts","script":"test0.ps1"}'
# 查看终端列表（获取返回的 id）
curl http://127.0.0.1:13025/terminals
# 查看终端输出（按 id）
curl "http://127.0.0.1:13025/terminal/output?id=0"
# 向脚本注入输入（交互式脚本）
curl -X POST http://127.0.0.1:13025/terminal/input \
  -H "Content-Type: application/json" \
  -d '{"id":0,"text":"Hello\\n"}'
# 强制终止单个终端
curl -X POST http://127.0.0.1:13025/terminal/stop \
  -H "Content-Type: application/json" \
  -d '{"id":0}'
# 终止所有终端
curl -X POST http://127.0.0.1:13025/terminal/stop_all
# 关闭 PsLauncher
curl -X POST http://127.0.0.1:13025/shutdown
```

**PowerShell 调用注意事项** 在 Windows PowerShell 中建议使用 `curl.exe` 而非 `curl`（Alias），必要时用 `--%` 阻止 PowerShell 解析参数。下面展示了一个正确的在PowerShell上调用的例子，尤其注意如何使用反斜杠和阻止解析参数：

```powershell
curl.exe --% -X POST http://127.0.0.1:13025/script/run -H "Content-Type: application/json" -d "{\"folder\":\"E:\\project_file\\limitless\\PsLauncher\\test_script\",\"script\":\"test0.ps1\"}"
```

## 5. Agent 使用要点

1. **先确保 PsLauncher 已启动**  
   - 可通过 `/status` 检查服务是否存活；若未启动，提示用户先启动或以 `--headless` 方式部署。
2. **异步、非阻塞调用**  
   - 所有操作都是 HTTP API，Agent 可在任意时刻查询输出、注入输入、终止进程，不会阻塞 Agent 主循环。
3. **进程生命周期闭环**  
   - `/script/run` → `/terminals` → `/terminal/output` → `/terminal/input` → `/terminal/stop`  
   - 建议在任务完成后显式 `/terminal/stop` 或 `/terminal/stop_all`，避免僵尸进程。
4. **交互式脚本处理**  
   - 对于等待输入的脚本（如 `Read-Host`），通过 `/terminal/input` 注入文本；  
   - 可通过反复 `/terminal/output` 判断脚本是否已进入交互状态。
5. **调试与自我学习**  
   - Agent 首次接入时，可以调用 `/help` 获取端点结构，再据此生成请求体模板。

## 6. 配置要点（给用户看）

AI 若需影响用户环境，应让用户确认：

- `config.json` 中 `api.bind_ip` / `bind_port` 是否符合预期（默认 `127.0.0.1:13025`）。
- 是否配置 `api.auth_token` 以开启认证。
- 是否以 `--headless` 启动纯 API 实例，避免 GUI 依赖。
