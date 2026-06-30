# coding = utf-8
# Arch   = manyArch
#
# @File name:       i18n/source_help_page.py
# @brief:           帮助页面文本
# @attention:       None
# @Author:          get_help_page.py 脚本自动生成, 请勿直接编辑该文件
# @History:         2026-06-29		Create

html_content = '''\
<h1>PsLauncher — Lightweight Script Orchestrator for Local LLM Scenarios</h1>
<p>Unify and manage PowerShell / Bash / Batch scripts in a lightweight VSCode-like interface, while embedding a built-in HTTP API service. This allows <strong>both humans and AI Agents to operate the same local service process with a unified set of asynchronous, non‑blocking semantics</strong>: start, interact, force‑kill, query output, and batch recycle. Supports system tray persistence, process‑tree force‑kill, ANSI‑colored terminal, and interactive I/O. Optimized for local LLM deployment stacks such as llama.cpp / Ollama / litellm. Compatible with Windows, Linux, and macOS.</p>
<center><a href='./README.md'>English version</a> | <a href='./README_CN.md'>中文说明书</a></center>

<blockquote>
<p>The English version readme is provided by machine translation and may be inaccurate.</p>
</blockquote>
<p><img alt="pic" src="pic.jpg" /></p>
<center>Fig. PsLauncher in action</center>

<h2>Key Highlights</h2>
<ul>
<li><strong>AI is no longer blocked by program processes</strong> – while a program runs inside the terminal, the AI can freely inspect logs or perform other operations at any time. Manage multiple programs’ I/O simultaneously, completely decoupling the interaction timing between programs and AI.</li>
<li><strong>Bidirectional control from the same source for human and machine</strong> – breaks the isolation between AI Agents and human operations. Machine‑issued instructions and human GUI operations share the same state, eliminating state conflicts and handover barriers. Truly enables AI execution with human takeover at any time.</li>
<li><strong>Unified governance of heterogeneous scripts</strong> – ends the fragmented, inconsistent startup logic scattered across different directories and languages in the local LLM ecosystem. Converge them into a single scheduling perspective, greatly reducing the cognitive load of environment maintenance.</li>
<li><strong>Deterministic resource reclamation</strong> – directly tackles the persistent issues of zombie processes and GPU memory leaks. Provides a thorough cleanup capability from graceful termination to process‑tree force‑kill, ensuring stable release of hardware resources when switching between services. No extra CPU / memory / GPU overhead.</li>
<li><strong>Dynamic long‑running task management with full lifecycle closure</strong> – elevates traditional terminals from one‑shot sessions to visual task containers. Supports viewing historical output and injecting new commands on the fly while a task is still running, perfectly suiting AI‑orchestrated long‑running workflows and interactive scripts. No fear that a stuck program will break the agent loop.</li>
<li><strong>Seamless switching across all deployment forms</strong> – caters to both low‑profile desktop development and headless server backend hosting with the same system, eliminating experience fragmentation across different environments.</li>
</ul>
<pre><code class="language-mermaid">flowchart TB
    %% Node styles
    classDef agentNode fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px,color:#0d47a1;
    classDef plNode fill:#fff8e1,stroke:#ffa000,stroke-width:2px,color:#e65100;
    classDef svcNode fill:#e8f5e9,stroke:#43a047,stroke-width:2px,color:#1b5e20;
    classDef apiNode fill:#ffebee,stroke:#d32f2f,stroke-width:3px,color:#b71c1c;
    classDef guiNode fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#4a148c;

    subgraph Agent[&quot;AI Agent loop&quot;]
        AGENT[&quot;AI Agent&quot;]:::agentNode
        skill[&quot;LLM + skill.md&quot;]:::agentNode
    end

    subgraph GUI[&quot;Human UI&quot;]
        traynode[&quot;System Tray&quot;]:::guiNode
        GUIUI[&quot;Graphical Interface&quot;]:::guiNode
    end

    subgraph PL[&quot;PsLauncher Core&quot;]
        direction TB
        API[&quot;HTTP API&lt;br/&gt;(AI call interface)&quot;]:::apiNode
        core[&quot;Process Scheduler&quot;]:::apiNode
        logctrl[&quot;Log &amp; Context Manager&quot;]:::apiNode
    end

    subgraph SVCS[&quot;Local Service Processes&quot;]
        LLAMA[&quot;llama.cpp&quot;]:::svcNode
        OLLAMA[&quot;Ollama&quot;]:::svcNode
        LITELLM[&quot;LiteLLM&quot;]:::svcNode
        TRAIN[&quot;Model Training&quot;]:::svcNode
        LORA[&quot;LoRA Fine‑tuning&quot;]:::svcNode
        CUSTOM[&quot;Custom Scripts&quot;]:::svcNode
    end

    %% Core interaction
    Agent &lt;==&gt;|&quot;Call API&lt;br/&gt;(run/manage/interact/return results)&quot;| PL

    %% GUI interaction
    GUI &lt;==&gt;|&quot;Bidirectional sync&lt;br/&gt;(state sharing)&quot;| PL
    GUI -.-&gt;|&quot;Human takeover/monitoring&quot;| PL

    %% Service management
    PL --&gt;|&quot;Unified scheduling&quot;| LLAMA
    PL --&gt;|&quot;Unified scheduling&quot;| OLLAMA
    PL --&gt;|&quot;Unified scheduling&quot;| LITELLM
    PL --&gt;|&quot;Unified scheduling&quot;| TRAIN
    PL --&gt;|&quot;Unified scheduling&quot;| LORA
    PL --&gt;|&quot;Unified scheduling&quot;| CUSTOM
</code></pre>
<center>Fig. PsLauncher architecture and highlights</center>

<h2>Problems Solved</h2>
<ul>
<li><strong>Fragmented environments and chaotic scheduling</strong> – inference tools and gateway scripts are scattered across various directories. Running multiple services simultaneously leads to terminal explosion and cumbersome parameter memorisation. There is no unified control centre to eliminate the disconnect of manually navigating directories and switching contexts.</li>
<li><strong>Resource leaks and hardware conflicts</strong> – after abnormal exits, zombie child processes often remain, occupying CPU, memory, and GPU memory silently. This causes frequent hardware resource conflicts on next startup. There is a lack of a robust lifecycle fallback mechanism.</li>
<li><strong>Interaction gap between AI and local environment</strong> – large language models struggle to safely and stably control the local computing environment. Traditional shell commands are fragile and lack self‑description. Agents need a structured, introspectable interface to form a closed‑loop of “start‑monitor‑interact‑reclaim”.</li>
<li><strong>Asynchronous issues between AI agent and program execution</strong> – traditional harness programs block the agent loop during script execution. Synchronous blocking may be interrupted by script timeouts or hangs. A unified asynchronous interface is needed so that the agent can manage program I/O and process lifecycle without blocking.</li>
<li><strong>Mismatch between heavy operations and lightweight needs</strong> – managing local scripts often forces the use of heavyweight IDEs or complex container orchestration systems. For simple scheduling and background persistence, the overhead and learning cost are too high. A zero‑intrusion lightweight solution is urgently needed.</li>
</ul>
<hr />
<h2>Quick Start</h2>
<blockquote>
<p>Note: The built‑in help documentation in PsLauncher is auto‑generated from Markdown. The Markdown or GitHub‑rendered page is correct; the in‑program help may not be fully accessible due to rendering issues. If you encounter problems, please refer to the Markdown or the <a href="https://github.com/NGC13009/PsLauncher.git">web page</a>.</p>
</blockquote>
<h3>Installation</h3>
<p>Two options:</p>
<ul>
<li>Download the source code and run with Python</li>
<li>Download the compiled executable and run directly</li>
</ul>
<h4>Using Source Code</h4>
<pre><code class="language-Bash">git clone https://github.com/NGC13009/PsLauncher.git
cd PsLauncher
pip install -r ./requirements.txt
</code></pre>
<h4>Windows Compiled Executable</h4>
<p>Download the executable from the <a href="https://github.com/NGC13009/PsLauncher/releases">release</a> page.</p>
<h3>Launch</h3>
<p>You can double‑click the executable to start, or launch via command line (parameters only need to be specified on first run; the program saves settings automatically):</p>
<pre><code class="language-bash"># Compiled executable
PsLauncher.exe

# Source code
python PsLauncher.py
</code></pre>
<h3>Usage</h3>
<h4>For Human Users (Direct Use)</h4>
<ol>
<li>Through the menu bar <strong>Settings → Add Script Folder</strong>, add the folder containing your scripts.</li>
<li>The left panel will automatically scan and display all scripts with the matching extensions. Click a script to view its source code.</li>
<li>Select a script and click <strong>Run</strong> (or press <code>F5</code>) to run it in a new terminal tab and see real‑time output.</li>
<li>Click <strong>Terminate</strong> (or <code>F6</code>) to forcefully stop the process, or click <strong>Interrupt</strong> (or <code>F7</code>) to send <code>Ctrl+C</code> for a graceful interruption.
A complete usage example: <a href="run_llama.cpp_and_litellm_by_PsLauncher.md">How to use PsLauncher to manage local LLM service configurations and run instances</a></li>
</ol>
<h4>Integrating PsLauncher into AI Agents via skill.md</h4>
<p>You can use PsLauncher as a skill.md in your agent workflow. For example, place this README (choose the language your AI understands) in your agent’s skill folder, then start a PsLauncher instance:</p>
<pre><code class="language-bash"># Compiled executable
PsLauncher.exe

# Without GUI
PsLauncher.exe --headless

# Or modify the config so that it automatically minimises to tray on startup (handy for humans to check status anytime).
</code></pre>
<p>Then the AI can call PsLauncher to asynchronously start/stop scripts or processes.</p>
<blockquote>
<ul>
<li>For programs, you need to write them as executable scripts so PsLauncher can manage them.</li>
<li>If you only use LLM operation, we recommend using <a href="pslauncher_skill.md">pslauncher_skill.md</a> as the skill, because it contains only API endpoint descriptions.</li>
<li>If necessary, translate the <code>skill.md</code> into your preferred language. For example, the Chinese version is <a href="pslauncher_skill_CN.md">pslauncher_skill_CN.md</a>.</li>
<li>If humans also need to use it, we recommend this README because it includes GUI usage instructions, allowing you to get operational tips from the AI after it has read the manual.</li>
</ul>
</blockquote>
<h4>Using Other Programs to Listen for Changes</h4>
<p>PsLauncher also exposes a <strong>TCP long‑connection event server</strong> (default port <code>13026</code>) to push internal state changes to external programs. When you need to integrate PsLauncher's state into automated monitoring, LLM Agent real‑time awareness workflows, or other scenarios requiring real‑time synchronisation (e.g., an AI Agent monitoring prompt output from multiple automated scripts, or cross‑process synchronisation), you don't need to poll the HTTP API — just establish a TCP long connection to continuously receive event pushes.</p>
<blockquote>
<p>For detailed event types, configuration, and listener script usage, please refer to the "<a href="#tcp-event-server">TCP Event Server</a>" section of this manual.</p>
<ul>
<li>This feature may be particularly useful for robotics scenarios, where multiple drivers may execute simultaneously. PsLauncher can provide a unified context and asynchronous execution process, effectively decoupling robot drivers (e.g., servo motors, stepper motors) from the LLM.</li>
</ul>
</blockquote>
<p>If you have read the above and experimented with the program, and want to dive deeper, continue reading the full manual.</p>
<hr />
<h2>Detailed Usage and Feature Description</h2>
<p>The following manual contains almost all features of the program, very detailed, with no particular emphasis. It is recommended to use AI search to find features you are interested in and ask the AI to explain how to use them, rather than reading this document straight through.</p>
<h3>Program Interface Layout</h3>
<p>PsLauncher adopts a VSCode‑like interface, mainly divided into the following areas:</p>
<ol>
<li><strong>Menu Bar</strong> – at the top of the window, all operations organised by function.</li>
<li><strong>Toolbar</strong> – below the menu bar, providing quick buttons for frequently used functions; supports drag‑and‑drop to adjust position.</li>
<li><strong>Left File List</strong> – Explorer, showing all script files in the added folders.</li>
<li><strong>Right Tab Area</strong> – main workspace, supports multiple tabs for viewing and editing.</li>
</ol>
<h3>Menu Bar Functions in Detail</h3>
<h4>System Menu</h4>
<ul>
<li><strong>Save Current Configuration</strong> (<code>F2</code>) – immediately save the current configuration to the config file.</li>
<li><strong>Hide Window to System Tray</strong> (<code>F10</code>) – hide the program window to the system tray and run in the background.</li>
<li><strong>Auto‑minimise to Tray on Startup</strong> – when checked, the program will automatically hide to the system tray each time it starts.</li>
<li><strong>Edit Configuration File</strong> – allows editing of all configuration options via a GUI. However, this interface is a crude auto‑generated view of all config items. Unless you cannot find a proper setting in the program, or the program does not provide a setting method, or you don’t want to manually edit the config file, you can modify settings here.</li>
</ul>
<h4>File Menu</h4>
<ul>
<li><strong>Add Folder Path</strong> (<code>F2</code>) – add a new script folder to the scan list.</li>
<li><strong>Remove Selected Folder Path</strong> (<code>F3</code>) – remove the selected folder from the scan list.</li>
</ul>
<h4>Edit Menu</h4>
<ul>
<li><strong>Copy Selected</strong> (<code>F11</code>) – copy the selected text in the current focus widget.</li>
<li><strong>Paste</strong> (<code>F12</code>) – paste clipboard content into the current focus widget.</li>
<li><strong>Copy Entire Tab to Clipboard</strong> – copy all text from the current tab.</li>
<li><strong>Clear Terminal Screen</strong> (<code>Ctrl+L</code>) – clear all displayed content in the current terminal tab, resetting the screen to blank.</li>
<li><strong>Edit Script Source</strong> (<code>F4</code>) – enter/exit script editing mode, supports saving changes.</li>
</ul>
<h4>Run Menu</h4>
<ul>
<li><strong>Run Script</strong> (<code>F5</code>) – run the currently selected script.</li>
<li><strong>Terminate Script (Force Stop)</strong> (<code>F6</code>) – forcefully terminate the script running in the current tab and all its child processes (process‑tree force‑kill).</li>
<li><strong>Send Ctrl+C Interrupt</strong> (<code>F7</code>) – send a <code>Ctrl+C</code> interrupt signal (<code>0x03</code>) to the current terminal process for a graceful interruption of the running script.</li>
</ul>
<h4>View Menu</h4>
<ul>
<li><strong>Toggle Word Wrap</strong> – enable/disable automatic text wrapping.</li>
<li><strong>Syntax Highlighting Mode</strong> – set code highlighting style:</li>
<li>Auto (automatically detect based on script type)</li>
<li>PowerShell</li>
<li>bash</li>
<li>command</li>
<li>None (no highlighting)</li>
</ul>
<h4>Script Management Menu</h4>
<ul>
<li><strong>New Folder</strong> – create a new subfolder under the selected folder.</li>
<li><strong>New Script</strong> – create a new script file in the selected folder.</li>
<li><strong>Rename Script</strong> – rename the selected script file.</li>
<li><strong>Copy Script</strong> – copy the selected script file (can be renamed).</li>
<li><strong>Move Script</strong> – move the script to another added folder.</li>
<li><strong>Delete Script</strong> – permanently delete the selected script file (bypasses Recycle Bin).</li>
</ul>
<h4>Tab Menu</h4>
<ul>
<li><strong>Close All Source Tabs</strong> (<code>F8</code>) – close all source code view tabs.</li>
<li><strong>Close All Run Tabs</strong> (<code>F9</code>) – close all terminal run tabs (will stop running processes).</li>
<li><strong>Close All Tabs</strong> – close all tabs, including source and terminal tabs.</li>
</ul>
<h4>Help Menu</h4>
<ul>
<li><strong>Help</strong> (<code>F1</code>) – open the help documentation.</li>
<li><strong>About</strong> – show program information and copyright.</li>
</ul>
<h3>Toolbar Functions in Detail</h3>
<p>Toolbar buttons are grouped by function with separators:</p>
<ol>
<li><strong>Window Management</strong></li>
<li>📌<strong>Hide</strong> – hide window to system tray. Tooltip: <code>Hide window to system tray; click the tray icon to restore.</code></li>
<li><strong>Script Control</strong></li>
<li>▶️<strong>Run</strong> – run the script in the currently focused tab. Tooltip: <code>Run the script in the currently focused tab.</code></li>
<li>⏹️<strong>Terminate</strong> – forcefully terminate the script in the currently focused tab (process‑tree kill). Tooltip: <code>Terminate the script in the currently focused tab (force‑kill process tree).</code></li>
<li>❌<strong>Interrupt</strong> – send <code>Ctrl+C</code> interrupt signal (<code>0x03</code>) to the current terminal process for graceful interruption. Tooltip: <code>Send Ctrl+C interrupt signal (0x03) to the current terminal process for graceful interruption.</code></li>
<li>🧹<strong>Clear</strong> – clear all content in the current terminal tab. Tooltip: <code>Clear all content in the current terminal tab.</code></li>
<li><strong>Text Operations</strong></li>
<li>📋<strong>Copy</strong> – copy the selected text to clipboard (if no text selected, copy the entire current tab content). Tooltip: <code>Copy selected text; if nothing selected, copy all text of the focused tab.</code></li>
<li>📤<strong>Paste</strong> – paste clipboard content at cursor position. Tooltip: <code>Paste clipboard content at cursor position.</code></li>
<li>📄<strong>Copy All</strong> – copy all text of the focused tab to clipboard. Tooltip: <code>Copy all text of the focused tab to clipboard.</code></li>
<li><strong>Editing</strong></li>
<li>✏️<strong>Quick Edit</strong> (💾<strong>Save</strong>) – enter/exit edit mode, save script changes. Tooltip: <code>Enter/exit edit mode, save script changes.</code> (changes to <code>Save script changes</code> when in edit mode)</li>
<li><strong>Tab Management</strong></li>
<li>🗑️<strong>Close All Source</strong> – close all read‑only source code view tabs. Tooltip: <code>Close all read‑only source code view tabs.</code></li>
<li>🚫<strong>Stop All Terminals</strong> – close all terminal tabs, including running and finished ones. Tooltip: <code>Close all terminal tabs, including running and finished ones.</code></li>
<li>💥<strong>Close All Tabs</strong> – close all tabs, including source and terminal; if a process is running, it will be forcibly terminated. Tooltip: <code>Close all tabs, including source and terminal; running processes will be forcibly terminated. May cause improper exit of programs or scripts.</code></li>
</ol>
<h3>Left File List Features</h3>
<p>The left file list (Explorer) is the main entry for script management:</p>
<ol>
<li><strong>Single‑click</strong></li>
<li>Click on a <strong>folder</strong> – expand/collapse the folder.</li>
<li>Click on a <strong>script</strong> – open a new source code view tab on the right showing the script source.</li>
<li><strong>Double‑click</strong></li>
<li>Double‑click a folder to expand or collapse it.</li>
<li><strong>Supported file types</strong></li>
<li><code>.ps1</code> (PowerShell scripts)</li>
<li><code>.bat</code>, <code>.cmd</code> (Batch scripts)</li>
<li><code>.sh</code> (Bash scripts)</li>
<li><strong>Scanning rules</strong></li>
<li>Only scans the root of added folders, does not recurse subdirectories.</li>
<li>Updates in real time; after adding/deleting files, refresh via the menu.</li>
</ol>
<h3>Right‑hand Tab Area Features</h3>
<p>The right area uses a multi‑tab design supporting two types of tabs:</p>
<h4>1. Source Code View Tab (📝 prefix)</h4>
<ul>
<li><strong>View mode</strong>: read‑only by default, displays script source code</li>
<li>Supports syntax highlighting (PowerShell / Bash / Batch)</li>
<li>Supports zoom via <code>Ctrl+Mouse wheel</code></li>
<li>Dark theme, VSCode‑style</li>
<li><strong>Edit mode</strong>: enter by clicking the <code>✏️ Quick Edit</code> button</li>
<li>Background turns dark grey to indicate editing</li>
<li>Can modify script content</li>
<li>After editing, click <code>💾 Save</code> to save changes</li>
<li>Handles UTF‑8/GBK encoding automatically (though not always perfectly)</li>
</ul>
<h4>2. Terminal Run Tab (🖥️ prefix)</h4>
<ul>
<li><strong>ANSI colour support</strong>: correctly displays coloured terminal output</li>
<li><strong>Interactive input</strong>: supports sending commands to the running process</li>
<li><strong>Process control</strong>:</li>
<li>Run script – shows start timestamp and script path</li>
<li>Stop script – forcefully terminates the process and all its children</li>
<li>Process end – shows end timestamp</li>
</ul>
<h3>Terminal Interactive Operation Guide</h3>
<p>Terminal tabs provide an interactive experience similar to a real terminal:</p>
<h4>Keyboard Operations</h4>
<ul>
<li><strong><code>Enter/Return</code></strong> – send the current input line to the process.</li>
<li><strong><code>Ctrl+C</code></strong> – handled globally by the event filter: if text is selected, copy to clipboard; otherwise triggers global copy (copy entire tab) or passes to the focused widget. It no longer directly terminates the process.</li>
<li><strong><code>Ctrl+X</code></strong> – cut selected text from the focused widget.</li>
<li><strong><code>Ctrl+Z</code></strong> – undo for the focused QTextEdit widget.</li>
<li><strong><code>Ctrl+Y</code></strong> – redo for the focused QTextEdit widget.</li>
<li><strong><code>Ctrl+V</code></strong> – paste clipboard content to the input area (not sent to the process).</li>
<li><strong><code>Backspace/Left Arrow</code></strong> – restricted to deletion/navigation within the input area; cannot modify historical output.</li>
</ul>
<h4>Input Protection</h4>
<ul>
<li>Input area and historical output area are separated.</li>
<li>Users can only edit the current input line.</li>
<li>Prevents accidental modification of already output history.</li>
<li>To copy output, use the toolbar <code>Copy</code> button.</li>
</ul>
<h4>Process Management</h4>
<ul>
<li><strong>Start process</strong> – runs the script in a new tab, automatically invoking the appropriate interpreter based on file type.</li>
<li><strong>Terminate process</strong> – forcefully terminates the process tree to ensure no residual processes.</li>
<li><strong>Process status</strong> – displays real‑time stdout and stderr.</li>
<li><strong>Exception handling</strong> – shows appropriate prompts on abnormal process exit.</li>
</ul>
<h3>Context Menus</h3>
<p>Both the left file tree and right tabs support context menus.</p>
<h4>File Tree Context Menu</h4>
<p><strong>Folder context menu:</strong></p>
<ul>
<li><strong>📂 Open in File Explorer</strong> – open the folder in the system file manager.</li>
<li><strong>📂 Remove Folder Path</strong> – remove the folder from the scan list (with confirmation dialog).</li>
<li><strong>📂 Add Folder Path</strong> – add a new script folder.</li>
</ul>
<p><strong>Script file context menu:</strong></p>
<ul>
<li><strong>▶️ Run</strong> – run the selected script directly.</li>
<li><strong>✏️ Edit/Save</strong> – open the script source and enter edit mode.</li>
<li><strong>🔄 Run on Startup / 🔄 Cancel Run on Startup</strong> – mark the script to run automatically on PsLauncher startup (only shown for runnable extensions <code>.ps1</code>/<code>.bat</code>/<code>.sh</code>). When marked, the script will be highlighted in blue in the file tree, and the tooltip will indicate <code>Run on Startup</code>.</li>
<li><strong>💻 Edit with VSC</strong> – attempts to open the selected file with VSCode (<code>code</code> command). If VSCode is not installed or not in PATH, a friendly error message is shown.</li>
<li><strong>📝 Rename</strong> – rename the selected script.</li>
<li><strong>📋 Copy</strong> – copy the selected script.</li>
<li><strong>🚚 Move</strong> – move the script to another folder.</li>
</ul>
<h4>Auto‑Run on Startup</h4>
<p>For scripts that need to start with the program (e.g., local service processes), you can configure them as follows:</p>
<ol>
<li>Right‑click the target script in the file tree and select <strong>🔄 Run on Startup</strong>.</li>
<li>The script will be highlighted in blue for easy identification.</li>
<li>The next time PsLauncher starts, that script will automatically run in a terminal tab.</li>
<li>To cancel, right‑click and select <strong>🔄 Cancel Run on Startup</strong>.</li>
</ol>
<p>Combined with <strong>Auto‑minimise to Tray on Startup</strong>, you can achieve completely silent background service management that starts with the system.</p>
<h3>System Tray Features</h3>
<h4>Tray Icon Actions</h4>
<ul>
<li><strong>Single‑click</strong> – restore the program window.</li>
<li><strong>Right‑click</strong> – show the tray menu.</li>
</ul>
<h4>Tray Menu</h4>
<ul>
<li><strong>Open Window</strong> – restore the program from tray.</li>
<li><strong>Exit Program</strong> – safely exit the program (will attempt to stop all running scripts first).</li>
</ul>
<h4>Tray Notifications</h4>
<ul>
<li>A prompt appears when hiding to tray.</li>
<li>Program status changes can be perceived via the tray icon.</li>
</ul>
<h3>Keyboard Shortcuts Summary</h3>
<table>
<thead>
<tr>
<th>Shortcut</th>
<th>Function</th>
<th>Description</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>F1</code></td>
<td>Help</td>
<td>Show help documentation</td>
</tr>
<tr>
<td><code>F2</code></td>
<td>Add Folder Path</td>
<td>Add a new script folder</td>
</tr>
<tr>
<td><code>F3</code></td>
<td>Remove Folder Path</td>
<td>Remove the selected folder</td>
</tr>
<tr>
<td><code>F4</code></td>
<td>Edit/Save Script</td>
<td>Toggle edit mode or save changes</td>
</tr>
<tr>
<td><code>F5</code></td>
<td>Run Script</td>
<td>Run the currently selected script</td>
</tr>
<tr>
<td><code>F6</code></td>
<td>Terminate Script (Force)</td>
<td>Forcefully terminate the currently running script and all its child processes (process‑tree kill)</td>
</tr>
<tr>
<td><code>F7</code></td>
<td>Send <code>Ctrl+C</code> Interrupt</td>
<td>Send <code>Ctrl+C</code> interrupt signal (<code>0x03</code>) to the current terminal process for graceful interruption</td>
</tr>
<tr>
<td><code>F8</code></td>
<td>Close All Source Tabs</td>
<td>Close all source code view tabs</td>
</tr>
<tr>
<td><code>F9</code></td>
<td>Close All Run Tabs</td>
<td>Close all terminal run tabs</td>
</tr>
<tr>
<td><code>F10</code></td>
<td>Hide to System Tray</td>
<td>Minimise to tray</td>
</tr>
<tr>
<td><code>F11</code></td>
<td>Copy Selected</td>
<td>Copy selected text</td>
</tr>
<tr>
<td><code>F12</code></td>
<td>Paste</td>
<td>Paste clipboard content</td>
</tr>
<tr>
<td><code>Ctrl+C</code></td>
<td>Copy / Global handling</td>
<td>If text selected, copy; otherwise trigger global copy (copy entire tab) or pass to focus widget</td>
</tr>
<tr>
<td><code>Ctrl+V</code></td>
<td>Paste</td>
<td>Paste clipboard content into the current focus widget</td>
</tr>
<tr>
<td><code>Ctrl+X</code></td>
<td>Cut</td>
<td>Cut selected text from the current focus widget</td>
</tr>
<tr>
<td><code>Ctrl+Z</code></td>
<td>Undo</td>
<td>Undo for the current QTextEdit widget</td>
</tr>
<tr>
<td><code>Ctrl+Y</code></td>
<td>Redo</td>
<td>Redo for the current QTextEdit widget</td>
</tr>
<tr>
<td><code>Ctrl+L</code></td>
<td>Clear Terminal Screen</td>
<td>Clear all content in the current terminal tab</td>
</tr>
</tbody>
</table>
<h3>Configuration File</h3>
<p>Most configuration can be done through the program interface, but you can also manually edit the config file.</p>
<p>The default config file path is <code>config.json</code> (in the program root, auto‑generated on first run). Supports JSON with comments:</p>
<pre><code class="language-json">// PsLauncher configuration file
{
    &quot;folders&quot;: [  // List of folder paths to scan for scripts
        &quot;E:/project_file/limitless/PsLauncher/test_script&quot;
    ],
    &quot;font_scale&quot;: 1.5,  // Font size scaling factor (e.g., 1.5 = 150%)
    &quot;dark_mode&quot;: true,  // Enable dark theme
    &quot;height_value&quot;: 1080,  // Window height in pixels
    &quot;width_value&quot;: 1920,  // Window width in pixels
    &quot;font_family&quot;: &quot;Consolas&quot;,  // Font family for editor and terminal
    &quot;line_wrap_mode&quot;: false,  // Enable automatic line wrap
    &quot;supported_extensions&quot;: [  // File extensions shown in the script tree
        &quot;.ps1&quot;,
        &quot;.bat&quot;,
        &quot;.sh&quot;,
        &quot;.json&quot;,
        &quot;.yaml&quot;
    ],
    &quot;runnable_extensions&quot;: [  // File extensions that can be executed
        &quot;.ps1&quot;,
        &quot;.bat&quot;,
        &quot;.sh&quot;
    ],
    &quot;syntax_highlight_mode&quot;: &quot;auto&quot;,  // Syntax highlighting mode: auto, ps1, bash, command, none
    &quot;auto_run_scripts&quot;: [],  // List of script paths to auto‑run on startup
    &quot;auto_minimize_to_tray&quot;: false,  // Auto‑minimise to system tray on startup
    &quot;language&quot;: &quot;zh_CN&quot;,  // UI language code (e.g., en, zh_CN)
    &quot;api&quot;: {  // HTTP API server configuration
        &quot;enabled&quot;: true,  // Enable HTTP API server
        &quot;bind_ip&quot;: &quot;127.0.0.1&quot;,  // IP address to bind (127.0.0.1 = localhost only)
        &quot;bind_port&quot;: 13025,  // Port number
        &quot;auth_token&quot;: &quot;&quot;  // Bearer token for authentication (empty = no auth)
    }
}
</code></pre>
<h3>Example Workflow</h3>
<h4>Initial Setup</h4>
<ol>
<li>Launch the program.</li>
<li>Click <code>File</code> → <code>Add Folder Path</code> or press <code>F2</code>.</li>
<li>Select the folder containing your scripts (e.g., llama.cpp directory).</li>
<li>The program automatically scans for script files in that folder.</li>
</ol>
<h4>View and Edit Scripts</h4>
<ol>
<li>Click a script file in the left file list.</li>
<li>A source code view tab opens on the right showing the code.</li>
<li>To modify, click the <code>✏️ Quick Edit</code> button to enter edit mode.</li>
<li>After editing, click <code>💾 Save</code> to save changes.</li>
</ol>
<h4>Run a Script</h4>
<ol>
<li>Click a script file in the left file list.</li>
<li>Click the <code>▶️ Run</code> button on the toolbar or press <code>F5</code>.</li>
<li>A terminal tab opens on the right and the script runs.</li>
<li>View real‑time output and perform interactive input as needed.</li>
<li>To force stop, click <code>⏹️ Terminate</code> or press <code>F6</code> (process‑tree kill); for graceful interruption, click <code>❌ Interrupt</code> or press <code>F7</code> (send <code>Ctrl+C</code>).</li>
</ol>
<h4>Multi‑task Management</h4>
<ul>
<li>You can open multiple scripts for viewing simultaneously.</li>
<li>You can run multiple scripts in different tabs concurrently.</li>
<li>Scroll the tab bar with the mouse wheel to switch tabs.</li>
<li>Use tab management functions to batch‑close tabs.</li>
</ul>
<h4>Background Operation</h4>
<ol>
<li>Click the <code>📌 Hide</code> button on the toolbar or press <code>F10</code>.</li>
<li>The window hides to the system tray.</li>
<li>Scripts continue running in the background.</li>
<li>Click the tray icon to restore the window at any time.</li>
</ol>
<h3>Command‑Line Arguments</h3>
<pre><code class="language-bash">usage: PsLauncher.py [-h] [--scale SCALE] [--light] [--dark] [--font FONT] [--height HEIGHT] [--width WIDTH]

PsLauncher - Universal Script Launcher

options:
  -h, --help        show this help message
  --scale SCALE     set window DPI scaling factor, e.g., 1.5
  --light           set light theme
  --dark            set dark theme
  --font FONT       set font, e.g., 'Consolas'
  --height HEIGHT   window height, e.g., 768
  --width WIDTH     window width, e.g., 1366
  --headless        headless mode, no GUI window, only HTTP API
</code></pre>
<h3>HTTP API Server</h3>
<p>PsLauncher exposes an HTTP API server on <code>127.0.0.1:13025</code> by default. Any LLM or human can send POST/GET requests to operate PsLauncher functions, equivalent to performing operations via the GUI.</p>
<h4>Headless Mode</h4>
<p>Start PsLauncher with <code>--headless</code> to run without the GUI, serving only via HTTP API:</p>
<pre><code class="language-bash">python PsLauncher.py --headless
</code></pre>
<h4>API Configuration</h4>
<p>Configure API parameters in <code>launcher_config.json</code>:</p>
<pre><code class="language-json">{
    // ...other settings...
    &quot;api&quot;: {
        &quot;enabled&quot;: true,           // Enable API server (false disables on next start)
        &quot;bind_ip&quot;: &quot;127.0.0.1&quot;,    // Bind IP (127.0.0.1 does not respond to public requests)
        &quot;bind_port&quot;: 13025,        // Bind port
        &quot;auth_token&quot;: &quot;&quot;           // Bearer Token (empty = no authentication)
    }
}
</code></pre>
<h4>Authentication</h4>
<p>If <code>auth_token</code> is set, all requests must carry the Authorization header:</p>
<pre><code class="language-text">Authorization: Bearer &lt;your-token&gt;
</code></pre>
<p>Incorrect tokens return <code>401 Unauthorized</code>.</p>
<p><strong>Pretty output</strong>: All endpoints support the <code>?pretty=true</code> query parameter to return formatted JSON (with indentation and newlines), making it human‑readable. Without <code>pretty</code>, the default is compact format with backslash escapes for control characters, suitable for programmatic parsing.</p>
<h4>API Endpoints</h4>
<p>All endpoints support POST; most query endpoints also support GET.</p>
<table>
<thead>
<tr>
<th>Endpoint</th>
<th>Description</th>
<th>Request Body / Parameters</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>GET/POST /status</code></td>
<td>Check status</td>
<td>None</td>
</tr>
<tr>
<td><code>GET /help</code></td>
<td>Show help information (HTML format)</td>
<td>None</td>
</tr>
<tr>
<td><code>POST /help</code></td>
<td>Get list of all available API endpoint formats (request body structure reference)</td>
<td>None</td>
</tr>
<tr>
<td><code>GET/POST /folders</code></td>
<td>List folder paths</td>
<td>None</td>
</tr>
<tr>
<td><code>GET/POST /scripts</code></td>
<td>List scripts</td>
<td><code>?folder=&lt;path&gt;</code> (optional)</td>
</tr>
<tr>
<td><code>POST /folder/add</code></td>
<td>Add a folder path</td>
<td><code>{"path":"C:/scripts"}</code></td>
</tr>
<tr>
<td><code>POST /folder/remove</code></td>
<td>Remove a folder path</td>
<td><code>{"path":"C:/scripts"}</code></td>
</tr>
<tr>
<td><code>POST /script/run</code></td>
<td>Run a script</td>
<td><code>{"folder":"C:/scripts","script":"test0.ps1"}</code></td>
</tr>
<tr>
<td><code>GET/POST /terminals</code></td>
<td>List terminal tabs (with IDs)</td>
<td>None</td>
</tr>
<tr>
<td><code>POST /terminal/stop</code></td>
<td>Stop a terminal</td>
<td><code>{"id":0}</code> or <code>{"name":"test0.ps1"}</code></td>
</tr>
<tr>
<td><code>POST /terminal/stop_all</code></td>
<td>Stop all terminals</td>
<td>No parameters</td>
</tr>
<tr>
<td><code>GET/POST /terminal/output</code></td>
<td>View terminal output</td>
<td><code>?id=0</code> or <code>?name=test0.ps1</code></td>
</tr>
<tr>
<td><code>POST /terminal/clear</code></td>
<td>Clear terminal output</td>
<td><code>{"id":0}</code></td>
</tr>
<tr>
<td><code>POST /terminal/input</code></td>
<td>Send a string to terminal</td>
<td><code>{"id":0,"text":"hello\n"}</code></td>
</tr>
<tr>
<td><code>GET/POST /shutdown</code></td>
<td>Shut down PsLauncher</td>
<td>No parameters</td>
</tr>
</tbody>
</table>
<h4>Usage Examples (Complete Walkthrough)</h4>
<p>All examples assume PsLauncher is already running, and replace <code>E:\\project_file\\limitless\\PsLauncher\\test_script</code> with the <strong>absolute path</strong> to your <code>test_script</code> folder.</p>
<p>The repository includes several test scripts that can be used directly. (You may need to download the source code, as the release version does not include test scripts.)</p>
<blockquote>
<p><strong>PowerShell note</strong>: PowerShell parses arguments differently from CMD. We recommend using <code>--%</code> (stop parsing symbol). All examples below use the <code>--%</code> syntax with backslash path separators and escaping. These examples have been tested on Windows 11 with PowerShell.</p>
</blockquote>
<ul>
<li>Check service status</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/status
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;status&quot;: &quot;ok&quot;, &quot;version&quot;: &quot;v2.0.1&quot;, &quot;app&quot;: &quot;PsLauncher&quot;}
</code></pre>
<ul>
<li>Get all available API endpoint formats (pretty formatted)</li>
</ul>
<pre><code class="language-powershell">curl.exe -X POST http://127.0.0.1:13025/help?pretty=true
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{
  &quot;success&quot;: true,
  &quot;endpoints&quot;: [
    {
      &quot;method&quot;: &quot;GET&quot;,
      &quot;path&quot;: &quot;/status&quot;,
      &quot;description&quot;: &quot;Check server status&quot;,
      &quot;params&quot;: null,
      &quot;body&quot;: null,
      &quot;response&quot;: {
        &quot;status&quot;: &quot;ok&quot;,
        &quot;version&quot;: &quot;x.x.x&quot;,
        &quot;app&quot;: &quot;PsLauncher&quot;
      }
    },
    ..... // many lines omitted
  ]
}
</code></pre>
<ul>
<li>Add test_script folder to scan list</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/folder/add -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;path\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;Added folder: E:\\project_file\\limitless\\PsLauncher\\test_script&quot;}
</code></pre>
<ul>
<li>List all runnable scripts</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/scripts
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;scripts&quot;: [{&quot;folder&quot;: &quot;E:/project_file/limitless/PsLauncher/test_script&quot;, &quot;name&quot;: &quot;test0.ps1&quot;, ...}....}
</code></pre>
<ul>
<li>Run test0.ps1 (basic output + show working directory)</li>
</ul>
<blockquote>
<p>test0.ps1 content: prints three lines, then displays the current working directory.</p>
</blockquote>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/script/run -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;folder\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;,\&quot;script\&quot;:\&quot;test0.ps1\&quot;}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;terminal_id&quot;: 0, &quot;message&quot;: &quot;Started script: test0.ps1&quot;}
</code></pre>
<p>At the same time, the PsLauncher GUI launches the script.</p>
<ul>
<li>List terminals (record the ID)</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/terminals
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;terminals&quot;: [{&quot;id&quot;: 0, &quot;name&quot;: &quot;test0.ps1&quot;, &quot;script&quot;: &quot;E:\\project_file\\limitless\\PsLauncher\\test_script\\test0.ps1&quot;, &quot;running&quot;: false}]}
</code></pre>
<ul>
<li>View terminal output (id=0 from the previous test0.ps1)</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/terminal/output?id=0&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;id&quot;: 0, &quot;name&quot;: &quot;test0.ps1&quot;, &quot;output&quot;: &quot;[PsLauncher 2026-06-30 21:40:20] start: E:\\project_file\\limitless\\PsLauncher\\test_script\\test0.ps1\ntest0-1\ntest0-2\ntest0-3\nCurrent work path: E:\\project_file\\limitless\\PsLauncher\\test_script\n\n[PsLauncher 2026-06-30 21:40:20] Process terminated.\n&quot;}
</code></pre>
<ul>
<li>Run test2.ps1 (interactive input demo)</li>
</ul>
<blockquote>
<p>test2.ps1 content: prints three lines, then waits for keyboard input via Read‑Host.</p>
</blockquote>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/script/run -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;folder\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;,\&quot;script\&quot;:\&quot;test2.ps1\&quot;}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;terminal_id&quot;: 1, &quot;message&quot;: &quot;Started script: test2.ps1&quot;}
</code></pre>
<ul>
<li>List terminals again (should now have id=0 and id=1)</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/terminals
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;terminals&quot;: [{&quot;id&quot;: 0, &quot;name&quot;: &quot;test0.ps1&quot;, &quot;script&quot;: &quot;E:\\project_file\\limitless\\PsLauncher\\test_script\\test0.ps1&quot;, &quot;running&quot;: false}, {&quot;id&quot;: 1, &quot;name&quot;: &quot;test2.ps1&quot;, &quot;script&quot;: &quot;E:\\project_file\\limitless\\PsLauncher\\test_script\\test2.ps1&quot;, &quot;running&quot;: true}]}
</code></pre>
<ul>
<li>Send input to id=1 (test2.ps1)</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/input -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;id\&quot;:1,\&quot;text\&quot;:\&quot;Hello PsLauncher\&quot;}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;Sent input to terminal ID=1&quot;}
</code></pre>
<ul>
<li>View test2.ps1 output (should include the input just sent)</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/terminal/output?id=1&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;id&quot;: 1, &quot;name&quot;: &quot;test2.ps1&quot;, &quot;output&quot;: &quot;[PsLauncher 2026-06-30 21:41:29] start: E:\\project_file\\limitless\\PsLauncher\\test_script\\test2.ps1\ntest2-1\ntest2-2\ntest2-3\nHello PsLauncher\nYou entered: Hello PsLauncher\n\n[PsLauncher 2026-06-30 21:41:44] Process terminated.\n&quot;}
</code></pre>
<ul>
<li>Run test3.bat (batch script demo)</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/script/run -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;folder\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;,\&quot;script\&quot;:\&quot;test3.bat\&quot;}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;terminal_id&quot;: 2, &quot;message&quot;: &quot;Started script: test3.bat&quot;}
</code></pre>
<ul>
<li>View test3.bat output</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/terminal/output?id=2&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;id&quot;: 2, &quot;name&quot;: &quot;test3.bat&quot;, &quot;output&quot;: &quot;[PsLauncher 2026-06-30 21:41:55] start: E:\\project_file\\limitless\\PsLauncher\\test_script\\test3.bat\nbat test3-1\nbat test3-2\nbat test3-3\n\n[PsLauncher 2026-06-30 21:41:55] Process terminated.\n&quot;}
</code></pre>
<ul>
<li>Clear test3.bat terminal output</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/clear -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;id\&quot;:2}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;Cleared output of terminal ID=2&quot;}
</code></pre>
<ul>
<li>Stop terminal id=1 (test2.ps1)</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/stop -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;id\&quot;:1}&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;Stopped terminal ID=1&quot;}
</code></pre>
<ul>
<li>Stop all terminals</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/stop_all
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;Stopped 2 terminals&quot;}
</code></pre>
<ul>
<li>Shut down PsLauncher</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/shutdown
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;PsLauncher is shutting down...&quot;}
</code></pre>
<blockquote>
<p>At the same time, PsLauncher exits.</p>
</blockquote>
<h3>TCP Event Server</h3>
<p>PsLauncher exposes a TCP long‑connection event server on <code>127.0.0.1:13026</code> by default, used to push internal state changes to connected clients in real time.</p>
<blockquote>
<p><strong>Use cases</strong>: real‑time monitoring of script status changes, terminal output streams, script list/path changes, etc., avoiding the overhead of polling the HTTP API. For example, an automated operations monitoring system or an LLM Agent can maintain a single long connection to receive real‑time terminal output prompts and status changes, enabling synchronous responses.</p>
</blockquote>
<h4>TCP Event Server Configuration</h4>
<p>Configure in <code>launcher_config.json</code>:</p>
<pre><code class="language-json">{
    &quot;tcp_event_server&quot;: {
        &quot;enabled&quot;: true,            // Enable TCP event server (enabled by default)
        &quot;bind_ip&quot;: &quot;127.0.0.1&quot;,     // Bind IP (127.0.0.1 does not respond to public requests)
        &quot;bind_port&quot;: 13026          // Bind port
    }
}
</code></pre>
<h4>Protocol</h4>
<ul>
<li><strong>Transport</strong>: raw TCP, newline‑delimited JSON (each JSON object occupies one line, terminated by <code>\n</code>)</li>
<li><strong>Encoding</strong>: UTF-8</li>
<li><strong>Client subscription</strong> (optional): after connecting, the client can send a subscription message to receive only specific event types</li>
</ul>
<h5>Client Subscription Message Format</h5>
<p>After a successful connection, the client sends a JSON message:</p>
<pre><code class="language-json">{&quot;subscribe&quot;: [&quot;path_changed&quot;, &quot;terminal_status&quot;]}
</code></pre>
<ul>
<li>No subscription message = receive all events</li>
<li><code>{"subscribe": ["*"]}</code> = reset to all events</li>
<li><code>{"subscribe": []}</code> = cancel all subscriptions</li>
<li><code>{"subscribe": ["path_changed", "terminal_output"]}</code> = only receive path changes and terminal output events</li>
</ul>
<h5>Server Event Push Format</h5>
<pre><code class="language-json">{
    &quot;event&quot;: &quot;path_changed&quot;,
    &quot;timestamp&quot;: &quot;2026-06-30 22:00:00&quot;,
    &quot;data&quot;: { ... }
}
</code></pre>
<h4>Event Types</h4>
<table>
<thead>
<tr>
<th>Event Type</th>
<th>Trigger</th>
<th>data Field</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>path_changed</code></td>
<td>Folder path added or removed</td>
<td><code>{"folders": ["path1", "path2", ...]}</code></td>
</tr>
<tr>
<td><code>script_changed</code></td>
<td>Script created/renamed/copied/moved/deleted</td>
<td><code>{"folder": "C:/scripts", "scripts": [{"name": "file.ps1", "path": "..."}]}</code></td>
</tr>
<tr>
<td><code>terminal_output</code></td>
<td>New stdout/stderr output from a terminal</td>
<td><code>{"terminal_id": 0, "script": "C:/scripts/test.ps1", "text": "Hello World\n"}</code></td>
</tr>
<tr>
<td><code>terminal_status</code></td>
<td>Terminal process status change</td>
<td><code>{"terminal_id": 0, "script": "C:/scripts/test.ps1", "status": "started\|finished\|stopped\|closed"}</code></td>
</tr>
</tbody>
</table>
<p><code>terminal_status</code> values:</p>
<ul>
<li><code>started</code>: script process started</li>
<li><code>finished</code>: script process exited normally</li>
<li><code>stopped</code>: script process was forcefully terminated</li>
<li><code>closed</code>: terminal tab closed (process no longer running)</li>
</ul>
<h4>Using the Listener Script</h4>
<p>The project provides <code>test_event_listener.py</code> for quick testing and understanding of the feature; you can run it directly to observe real‑time events:</p>
<pre><code class="language-bash"># Listen to all events
python test_event_listener.py

# Only listen to path changes and terminal status changes
python test_event_listener.py --subscribe path_changed terminal_status

# Specify address and port
python test_event_listener.py --host 127.0.0.1 --port 13026
</code></pre>
<p>Example output:</p>
<pre><code>PsLauncher TCP Event Listener
Connected to: 127.0.0.1:13026
Subscribed events: all
Waiting for events... (press Ctrl+C to exit)
------------------------------------------------------------

[2026-06-30 22:05:00] Event type: terminal_status
  Terminal ID: 0
  Script: C:/scripts/test0.ps1
  Status: 🚀 Started

[2026-06-30 22:05:01] Event type: terminal_output
  Terminal ID: 0
  Script: C:/scripts/test0.ps1
  Output: Hello World

[2026-06-30 22:05:02] Event type: path_changed
  Folder list (1 total):
    - C:/my_scripts

[2026-06-30 22:05:05] Event type: terminal_status
  Terminal ID: 0
  Script: C:/scripts/test0.ps1
  Status: ✅ Finished normally
</code></pre>
<h4>Manual Testing with telnet / nc</h4>
<pre><code class="language-bash"># Using telnet (requires Windows Telnet Client enabled)
telnet 127.0.0.1 13026

# Using ncat (recommended, available from nmap)
ncat 127.0.0.1 13026

# Using PowerShell
$client = New-Object System.Net.Sockets.TcpClient('127.0.0.1', 13026)
$stream = $client.GetStream()
$reader = New-Object System.IO.StreamReader($stream)
while (($line = $reader.ReadLine()) -ne $null) { Write-Host $line }
</code></pre>
<p>Once connected, the terminal will continuously display pushed event JSON lines.</p>
<h3>Using Pretty Output (Human‑Readable)</h3>
<p>Add <code>?pretty=true</code> to make the output human‑readable.</p>
<ul>
<li>With <code>?pretty=true</code>:</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/status?pretty=true&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{
  &quot;status&quot;: &quot;ok&quot;,
  &quot;version&quot;: &quot;v2.0.1&quot;,
  &quot;app&quot;: &quot;PsLauncher&quot;
}
</code></pre>
<ul>
<li>Without <code>?pretty=true</code>:</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/status&quot;
</code></pre>
<p>Expected output:</p>
<pre><code class="language-jsonc">{&quot;status&quot;: &quot;ok&quot;, &quot;version&quot;: &quot;v2.0.1&quot;, &quot;app&quot;: &quot;PsLauncher&quot;}
</code></pre>
<h3>Notes</h3>
<ul>
<li>If running from source, ensure Python 3.x and Qt5/Qt6 are installed.</li>
<li>In some cases, administrator privileges may be required (depending on script content).</li>
<li>(Known issue) Terminal colour rendering may be incorrect in some cases.</li>
<li>(Known issue) The editor background colour should change to indicate edit mode, but sometimes this visual cue does not appear.</li>
</ul>
<h3>Frequently Asked Questions</h3>
<p><strong>Q: How to copy terminal output?</strong>
A: Use the <code>📋 Copy</code> button to copy selected text (or press <code>Ctrl+C</code> directly), or use <code>📄 Copy All</code> to copy the entire tab content. <code>Ctrl+C</code> is now handled globally: if text is selected, it copies; otherwise it copies the entire tab content.</p>
<p><strong>Q: What if save fails in edit mode?</strong>
A: It may be a file permission issue. Try running the program as administrator, or check if the file is locked by another program.</p>
<p><strong>Q: How to adjust interface font size?</strong>
A: Start the program with the <code>--scale</code> command‑line parameter, or modify the <code>font_scale</code> value in the configuration file.</p>
<p><strong>Q: No output after running a script?</strong>
A: Check if the script requires interactive input. The terminal supports interactive operation – try typing a command in the input area and pressing <code>Enter</code>.</p>
<p><strong>Q: How to permanently delete a script file?</strong>
A: Use <code>Script Management</code> → <code>Delete Script</code>. Note that this deletes the file directly, bypassing the Recycle Bin.</p>
<h2>Development Information &amp; Notes for Developers</h2>
<ul>
<li><strong>Language</strong>: Python 3.12+</li>
<li><strong>GUI Framework</strong>: PyQt5 / PyQt6 / PySide6</li>
</ul>
<h3>Build Process</h3>
<p>First ensure the environment: besides <code>requirements.txt</code>, you also need <code>pip install pyinstaller</code>.</p>
<p>Then run:</p>
<pre><code class="language-bash">pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./
</code></pre>
<p>The program has only one media asset (the icon), which has been base64‑encoded into the source code, so no additional resource configuration is needed – just build directly.</p>
<h3>Release Procedure</h3>
<p>The proper release procedure is as follows:</p>
<ol>
<li>Update <code>__version__</code> and <code>__devdate__</code> in <code>aboutandhelp.py</code>.</li>
<li>Run automatic testing <code>python -m pytest test/ -q --tb=long -p no:warnings</code> verify no bug.</li>
<li>Run <code>python check_i18n_coverage.py</code> to verify i18n coverage.</li>
<li>Run <code>python get_help_page.py</code> to compile multi‑language help pages (reads <code>README.md</code> for English, <code>README_CN.md</code> for Chinese, etc.)</li>
<li>If the icon is updated, run <code>python get_ico.py</code> to recompile it.</li>
<li>Run <code>pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./</code> to build.</li>
<li>If necessary, also place the help documents.</li>
<li>Run <code>get_zip_release.ps1</code> to package.</li>
</ol>
<p>Correct release directory structure:</p>
<pre><code class="language-PowerShell">exe/
   PsLauncher.exe
   _internal/*    # Required dynamic libraries
</code></pre>
<h3>Internationalisation (i18n)</h3>
<p>This program uses a custom i18n module for multi‑language support. You can check the code in the <code>i18n</code> folder to understand its simple mechanism.</p>
<p>The HTTP API server also supports i18n: all endpoint descriptions, error messages, and operation response messages in <code>POST /help</code>, as well as error messages returned by all API endpoints, automatically switch language based on the configured <code>language</code> setting.</p>
<h3>Automated Testing</h3>
<p>The project has a complete automated testing suite based on <code>pytest</code> + <code>pytest-qt</code> + <code>pytest-xdist</code>, supporting headless parallel execution.</p>
<h4>Test Directory Structure</h4>
<pre><code class="language-text">test/
├── conftest.py              # Global fixtures: environment variables, temp config, main_window, etc.
├── test_config.py           # Functional: config.json read/write, defaults, comment parsing, boundary values
├── test_scanner.py          # Functional: folder scanning, non‑recursive, suffix filtering, real‑time refresh
├── test_script_types.py     # Algorithmic: .ps1/.bat/.sh detection, interpreter selection, extension validation
├── test_process_control.py  # Functional: process‑tree force‑kill, Ctrl+C signal (0x03), no leftover children
├── test_ansi.py             # Algorithmic: ANSI escape parsing and colouring
├── test_syntax_highlight.py # Algorithmic: auto/ps1/bash/command/none mode discrimination
├── test_i18n.py             # Algorithmic: i18n module pure functions
├── test_utils.py            # Algorithmic: utility functions (theme, font scaling)
├── test_autorun.py          # Functional: auto‑run on startup flag, blue highlight state persistence
├── test_tray.py             # GUI: tray hide/restore/exit (skipped under offscreen)
├── test_gui_main.py         # GUI: main window construction, menu Action triggers, tab add/delete
├── test_gui_toolbar.py      # GUI: toolbar button mappings
├── test_gui_terminal.py     # GUI: terminal tab ANSI rendering, interactive input
├── test_gui_editor.py       # GUI: source tab read‑only/edit toggle, save, zoom
├── test_gui_tabs.py         # GUI: batch tab closing, F8/F9 shortcuts
└── fixtures/
    ├── __init__.py
    ├── config_factory.py    # Build different config.json scenarios
    └── temp_scripts.py      # Temporary script directory
</code></pre>
<h4>Three‑Tier Test Classification</h4>
<table>
<thead>
<tr>
<th>Tier</th>
<th>Description</th>
<th>Parallel‑safe</th>
<th>Marker</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Algorithmic (algo)</strong></td>
<td>Pure functions, no Qt dependency</td>
<td>✅ Safe</td>
<td><code>@pytest.mark.algo</code></td>
</tr>
<tr>
<td><strong>Functional (func)</strong></td>
<td>Business logic without QWidget instantiation (mockable)</td>
<td>✅ Safe</td>
<td><code>@pytest.mark.func</code></td>
</tr>
<tr>
<td><strong>GUI (gui)</strong></td>
<td>Interactive tests based on pytest‑qt, require qtbot fixture</td>
<td>⚠️ Use with caution</td>
<td><code>@pytest.mark.gui</code></td>
</tr>
</tbody>
</table>
<h4>Running Tests</h4>
<p><strong>Minimal version</strong> (uniform for CI and local):</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=short -p no:warnings --no-header
</code></pre>
<p><strong>Detailed version</strong> (local debugging):</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=long -p no:warnings
</code></pre>
<p><strong>Only non‑GUI tests</strong> (fast regression):</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=short -p no:warnings --no-header -m &quot;not gui&quot;
</code></pre>
<p>Parameter meanings:</p>
<ul>
<li><code>-q</code>/<code>--no-header</code>: concise output, saves tokens. If you are human, <code>-v</code> might be more suitable.</li>
<li><code>--tb=short</code>: short traceback, avoids excessive stack dumps.</li>
<li><code>-p no:warnings</code>: suppress Python warnings.</li>
<li><code>-n auto</code>: enable pytest‑xdist parallelisation across CPU cores.</li>
<li><code>-m "not gui"</code>: skip GUI‑marked tests.</li>
</ul>
<h4>Headless Environment Requirements</h4>
<p>pytest‑qt requires the following when running in a headless environment (CI/server):</p>
<pre><code class="language-bash">export QT_QPA_PLATFORM=offscreen   # Linux/macOS
set QT_QPA_PLATFORM=offscreen      # Windows CMD
$env:QT_QPA_PLATFORM=&quot;offscreen&quot;   # Windows PowerShell
</code></pre>
<p>This is already set automatically at the top of <code>conftest.py</code>. To specify a Qt binding:</p>
<pre><code class="language-bash">export PYTEST_QT_API=pyqt5
</code></pre>
<h4>Notes for AI Agents</h4>
<ul>
<li>After writing test code, AI should only run <code>py_compile</code> or the pytest suite. <strong>AI must not execute GUI‑only tests themselves</strong> (they will block the agent loop). Any GUI‑only tests should be run and confirmed by a human assistant.</li>
<li>Do not read files starting with <code>source_</code> (e.g., <code>source_ico.py</code>) – these are auto‑generated by the compiler and are very large.</li>
<li>GUI tests have limited coverage in offscreen mode; tray and drag‑and‑drop features require manual verification.</li>
<li>After development, you must run <code>python -m pytest test/ -q --tb=long -p no:warnings</code> to confirm all tests pass.</li>
<li>After development is complete, if necessary, please modify the README and add automated test cases to cover the new functionality.</li>
</ul>
<h4>Checklist for Human Developers (Test Coverage)</h4>
<p>Below is a checklist with automation status:</p>
<table>
<thead>
<tr>
<th>Item</th>
<th>Automated Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Normal startup</td>
<td>✅ <code>test_gui_main.py</code></td>
</tr>
<tr>
<td>Menu bar functions work correctly</td>
<td>✅ <code>test_gui_main.py::TestMenuActions</code></td>
</tr>
<tr>
<td>Toolbar functions work correctly</td>
<td>✅ <code>test_gui_toolbar.py</code></td>
</tr>
<tr>
<td>Toolbar dragging keeps correct position</td>
<td>⚠️ Drag requires manual confirmation</td>
</tr>
<tr>
<td>File explorer displays correctly</td>
<td>✅ <code>test_scanner.py</code></td>
</tr>
<tr>
<td>File explorer context menu functions</td>
<td>⚠️ Context menu trigger requires manual confirmation</td>
</tr>
<tr>
<td>Source code tab works correctly</td>
<td>✅ <code>test_gui_editor.py</code></td>
</tr>
<tr>
<td>Source code tab editing and saving</td>
<td>✅ <code>test_gui_editor.py</code></td>
</tr>
<tr>
<td>Multiple source tabs switching</td>
<td>✅ <code>test_gui_main.py::TestTabManagement</code></td>
</tr>
<tr>
<td>Terminal tab works correctly</td>
<td>✅ <code>test_gui_terminal.py</code></td>
</tr>
<tr>
<td>Terminal interactive input</td>
<td>✅ <code>test_gui_terminal.py</code></td>
</tr>
<tr>
<td>Terminal interrupt function</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
<tr>
<td>Child process exits when tab closed</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
<tr>
<td>Child processes exit on bulk tab close</td>
<td>✅ <code>test_gui_tabs.py</code></td>
</tr>
<tr>
<td>Child processes exit when program exits</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
<tr>
<td>Multiple child processes do not interfere</td>
<td>⚠️ Manual verification of process isolation</td>
</tr>
<tr>
<td>Tray hide/restore</td>
<td>⚠️ Skipped under offscreen, manual confirmation needed</td>
</tr>
<tr>
<td>Tray exit leaves no residues</td>
<td>⚠️ Manual confirmation needed</td>
</tr>
<tr>
<td>Scripts run from the script’s folder</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
</tbody>
</table>
<p><strong>AI automated coverage:</strong> 23 items ✅ / 5 items ⚠️ require human verification.</p>
<h2>Notes for Human Developers</h2>
<p>As a human, you are obliged to assist the AI in executing GUI functional tests. Please check the following checklist whenever necessary (e.g., if you have changed the corresponding code). The list is for reference; feel free to add new items as needed:</p>
<ul>
<li>[x] Normal startup</li>
<li>[x] Change interface scaling via JSON config</li>
<li>[x] Menu bar functions work correctly</li>
<li>[x] Toolbar functions work correctly</li>
<li>[x] Toolbar drag‑and‑drop positioning works</li>
<li>[x] File explorer displays correctly</li>
<li>[x] File explorer context menu functions work correctly</li>
<li>[x] File explorer: copy, new, delete, etc.</li>
<li>[x] Source code tabs work correctly</li>
<li>[x] Source code tab context menu</li>
<li>[x] Source code tab editing, saving, etc.</li>
<li>[x] Multiple source code tab switching</li>
<li>[x] Terminal tabs work correctly</li>
<li>[x] Terminal tab context menu</li>
<li>[x] Terminal tab editing, saving, etc.</li>
<li>[x] Multiple terminal tab switching</li>
<li>[x] Terminal interactive input</li>
<li>[x] Terminal interrupt function</li>
<li>[x] Terminal: child process exits when tab is closed</li>
<li>[x] Terminal: child processes exit when bulk closing tabs</li>
<li>[x] Terminal: child processes exit when the entire program exits</li>
<li>[x] Terminal: multiple child processes do not interfere with each other</li>
<li>[x] Tray: can hide</li>
<li>[x] Tray: can restore</li>
<li>[x] Tray: tooltip works</li>
<li>[x] Tray: can exit without leftover child processes</li>
<li>[x] Terminal: scripts run from their own directory when started</li>
</ul>
<p>Remember to restore the checkboxes after verification!</p>
<h2>Copyright Information</h2>
<p>NGC13009</p>
<p><a href="https://github.com/NGC13009/PsLauncher.git">NGC13009/PsLauncher</a></p>
<p>Licensed under GPLv3.</p>'''
