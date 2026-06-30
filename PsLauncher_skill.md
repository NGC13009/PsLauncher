# PsLauncher HTTP API Skill (AI Agent Specific)

This document contains all configurations required for AI Agent operation. If you are an AI, this document is complete.

For GUI operation instructions intended for human users, if needed, please direct them to the [full PsLauncher manual](https://github.com/NGC13009/PsLauncher.git).

## 1. Functional Positioning

PsLauncher is a local script orchestrator that provides HTTP API for PowerShell / Bash / Batch scripts to:

- Asynchronously start, terminate, and batch-reclaim processes
- Query real-time output and historical logs
- Inject input into running scripts
- Uniformly manage multiple local service processes (llama.cpp / Ollama / LiteLLM, etc.)
AI Agents interact with PsLauncher via HTTP API, **without relying on GUI or blocking the Agent loop**.

## 2. Service Endpoint and Authentication

### Default Address

- After startup, the HTTP API is provided at `127.0.0.1:13025` by default. If inaccessible, please instruct the user to modify the instructions in this skill.md to configure the correct path.
- Can be started in pure API mode with `--headless`, which does not display the GUI.

### Authentication (Optional)

When the `api.auth_token` field in the `config.json` configuration file is non-empty, all requests must include:

```http
Authorization: Bearer <your-token>
```

Otherwise, `401 Unauthorized` will be returned.

If authentication is required, please instruct the user to modify the instructions in this skill.md to configure the correct token.

### Pretty Output (for Debugging)

All endpoints support the query parameter `?pretty=true`, returning formatted JSON (suitable for human viewing); without `pretty`, compact JSON is returned for easy programmatic parsing. You should use the correct parameter based on the current task type.

## 3. API Endpoint Overview

> All endpoints support `POST`; query-type endpoints also support `GET`.

### Status and Help

- `GET/POST /status`
  - Check overall service status
  - No request body, no parameters.
- `GET /help`
  - Returns an HTML help page (for humans).
- `POST /help`
  - Returns a structured list of all available endpoints (suitable as a call template).

### Path Management (Script Directories)

- `GET/POST /folders`
  - Get the list of all script folder paths currently scanned.
- `POST /folder/add`
  - Request body: `{"path": "C:/scripts"}`
  - Add a new folder to the scan list.
- `POST /folder/remove`
  - Request body: `{"path": "C:/scripts"}`
  - Remove a specified folder from the scan list.

### Script Listing and Execution

- `GET/POST /scripts`
  - Optional query parameter: `?folder=<absolute path>`
  - Returns the list of runnable scripts in that folder (only `.ps1/.bat/.sh`).
- `POST /script/run`
  - Request body:

    ```json
    {
      "folder": "C:/scripts",
      "script": "test0.ps1"
    }
    ```

  - Runs the script in a new terminal tab, returns terminal information (including `id`).

### Terminal Process Management

- `GET/POST /terminals`
  - Returns the list of all terminals, each containing:
    - `id`: integer ID
    - `name`: script name
    - status and other metadata.
- `POST /terminal/stop`
  - Request body:

    ```json
    { "id": 0 }
    ```

    or

    ```json
    { "name": "test0.ps1" }
    ```

  - Forcefully terminates the specified terminal and its entire process tree (hard kill, no leftovers).
- `POST /terminal/stop_all`
  - No request body
  - Terminates all running terminal processes.

### Output and Input

- `GET/POST /terminal/output`
  - Query parameters: `?id=0` or `?name=test0.ps1`
  - Returns the complete output (cumulative log) of that terminal.
- `POST /terminal/clear`
  - Request body: `{ "id": 0 }`
  - Clears the output buffer of that terminal (does not affect the process).
- `POST /terminal/input`
  - Request body:

    ```json
    {
      "id": 0,
      "text": "hello\n"
    }
    ```

  - Injects a string into the standard input of the running script (for interactive scripts).

### Shutting Down PsLauncher

- `GET/POST /shutdown`
  - No parameters
  - Safely shuts down PsLauncher (attempts to stop all running scripts first).

## 4. Calling Patterns and Examples (curl Templates)

The following are typical call flows (AI Agents can directly generate HTTP requests following this pattern).

### 4.1 Basic Call Template (assuming no auth_token configured)

```bash
# Check status
curl http://127.0.0.1:13025/status
# Get structured endpoint list (useful for generating request bodies)
curl -X POST http://127.0.0.1:13025/help?pretty=true
```

### 4.2 Managing Script Directories

```bash
# Add a script directory
curl -X POST http://127.0.0.1:13025/folder/add \
  -H "Content-Type: application/json" \
  -d '{"path":"C:/scripts"}'
# View added directories
curl http://127.0.0.1:13025/folders
# List runnable scripts in a directory
curl "http://127.0.0.1:13025/scripts?folder=C:/scripts"
```

### 4.3 Starting and Managing Script Processes

```bash
# Run a script (assuming directory C:/scripts, script test0.ps1)
curl -X POST http://127.0.0.1:13025/script/run \
  -H "Content-Type: application/json" \
  -d '{"folder":"C:/scripts","script":"test0.ps1"}'
# View terminal list (get the returned id)
curl http://127.0.0.1:13025/terminals
# View terminal output (by id)
curl "http://127.0.0.1:13025/terminal/output?id=0"
# Inject input into the script (interactive script)
curl -X POST http://127.0.0.1:13025/terminal/input \
  -H "Content-Type: application/json" \
  -d '{"id":0,"text":"Hello\\n"}'
# Forcefully stop a single terminal
curl -X POST http://127.0.0.1:13025/terminal/stop \
  -H "Content-Type: application/json" \
  -d '{"id":0}'
# Stop all terminals
curl -X POST http://127.0.0.1:13025/terminal/stop_all
# Shut down PsLauncher
curl -X POST http://127.0.0.1:13025/shutdown
```

**PowerShell Call Notes** In Windows PowerShell, it is recommended to use `curl.exe` instead of `curl` (which is an alias), and use `--%` when necessary to prevent PowerShell from parsing arguments. Below is a correct example of calling in PowerShell, paying special attention to backslash escaping and argument parsing prevention:

```powershell
curl.exe --% -X POST http://127.0.0.1:13025/script/run -H "Content-Type: application/json" -d "{\"folder\":\"E:\\project_file\\limitless\\PsLauncher\\test_script\",\"script\":\"test0.ps1\"}"
```

## 5. Key Points for Agent Usage

1. **Ensure PsLauncher is already started first**
   - Check service liveness via `/status`; if not started, prompt the user to start it or deploy with `--headless`.
2. **Asynchronous, non-blocking calls**
   - All operations are HTTP API calls; the Agent can query output, inject input, and terminate processes at any time without blocking the main Agent loop.
3. **Closed-loop process lifecycle**
   - `/script/run` → `/terminals` → `/terminal/output` → `/terminal/input` → `/terminal/stop`
   - It is recommended to explicitly `/terminal/stop` or `/terminal/stop_all` after task completion to avoid zombie processes.
4. **Handling interactive scripts**
   - For scripts waiting for input (e.g., `Read-Host`), inject text via `/terminal/input`;
   - Repeatedly call `/terminal/output` to determine whether the script has entered an interactive state.
5. **Debugging and self-learning**
   - When first accessing, the Agent can call `/help` to obtain endpoint structures and then generate request body templates accordingly.

## 6. Configuration Highlights (for Users)

If the AI needs to influence the user's environment, it should have the user confirm:

- Whether `api.bind_ip` / `bind_port` in `config.json` meet expectations (default `127.0.0.1:13025`).
- Whether `api.auth_token` is configured to enable authentication.
- Whether to start with `--headless` as a pure API instance to avoid GUI dependencies.
