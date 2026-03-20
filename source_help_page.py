html_content = '''\
<h1>PsLauncher - Lightweight Multi-Script Tray Manager</h1>
<p>Within a lightweight, VS Code-like interface, PowerShell/Bash/cmd (Batch) scripts are managed and run uniformly through multiple tabs. It supports <strong>system tray persistence</strong>, forced termination of child processes, ANSI-colored terminal output, and interactive input/output like a terminal. It is specifically optimized for scenarios such as local large-scale model deployment (llama.cpp/litellm). In theory, this can even manage assistant applications like OpenCLAW.</p>
<p><img alt="pic" src="pic.jpg" /></p>
<p><a href="README_CN.md">中文说明</a></p>
<blockquote>
<p>The English version readme is provided by machine translation and may be inaccurate.
A good use case: <a href="run_llama.cpp_and_litellm_by_PsLauncher.md">How to use PsLauncher to customize the local large model service configuration</a></p>
</blockquote>
<h2>Key Highlights</h2>
<ul>
<li><strong>Unified Management of Multiple Script Types:</strong> Supports PowerShell (.ps1), Bash (.sh), and Batch (.bat) scripts, supports multi-folder scanning without recursion to subdirectories, and remembers configuration files. This allows you to conveniently manage your frequently used scripts in one place.</li>
<li><strong>VSCode-like Multi-Tab Experience:</strong> Source code viewing and script execution output are managed in separate tabs, supporting syntax highlighting and ANSI coloring.</li>
<li><strong>Full Lifecycle Process Control:</strong> One-click start/stop of scripts, force-killing all associated child processes, leaving no residual processes.</li>
<li><strong>System Tray Resident:</strong> One-click hiding to the system tray, running in the background without occupying a window, and easily accessible.</li>
<li><strong>Interactive Terminal Support:</strong> Run tabs support real-time input, adapted for interactive scripts.</li>
<li><strong>Personalized Interface Customization:</strong> Supports dark/light theme switching, and freely adjustable font size/DPI scaling.</li>
</ul>
<h2>Pain Points Addressed</h2>
<ul>
<li>For example, when deploying tools like llama.cpp and littlem locally, multiple scripts are scattered across different folders, requiring repeated directory switching and file searches each time they run.</li>
<li>Or, when starting multiple services simultaneously, the terminal window becomes cluttered, making unified management and termination impossible.</li>
<li>Some project automation scripts need to be executed frequently, but as an operations engineer, I don't want to have to wait several seconds to open an IDE, especially since my server may not have enough memory or disk space to support it.</li>
<li>I just want simple script management and execution, without needing to open heavyweight IDEs like VS Code for this purpose.</li>
<li>My scripts run for long periods, requiring script tools to remain running in the background, allowing for quick and easy execution without consuming foreground window resources or distracting me with task windows.</li>
</ul>
<h2>Quick Start</h2>
<h3>Installation</h3>
<p>Two methods:</p>
<ul>
<li>
<p>Download the source code and run it using Python</p>
</li>
<li>
<p>Download the pre-compiled exe and run it directly</p>
</li>
</ul>
<h4>Source Code Usage</h4>
<pre><code class="language-Bash"># Configure Environment

git clone https://github.com/NGC13009/PsLauncher.git
cd PsLauncher
pip install -r ./requirements.txt
</code></pre>
<h4>Windows Compiled EXE</h4>
<p>Download the EXE from the <a href="https://github.com/NGC13009/PsLauncher/releases">release</a> page, extract it, and double-click to run it. (Alternatively, you can use advanced command-line startup, explained in detail later.)</p>
<h3>Starting the Program</h3>
<p>Regardless of the installation method, there are two ways to start the program:</p>
<ul>
<li><strong>Double-click the exe file after compilation to start the program directly.</strong> This will automatically load the relevant configuration.</li>
<li><strong>Start the program via the command line (or Python source code).</strong> This allows you to set two parameters. After setting them once, the program will save the configuration file, and you won't need to set them again later.</li>
</ul>
<p>Using the command line:</p>
<pre><code class="language-bash">usage: PsLauncher.py [-h] [--scale SCALE] [--light] [--dark] [--font FONT] [--height HEIGHT] [--width WIDTH]

PsLauncher - A general script launcher

options:
  -h, --help       show this help message and exit
  --scale SCALE    Interface font scaling factor (e.g., 1.5, equivalent to 150% DPI scaling on Windows)
  --light          use light theme
  --dark           use dark theme
  --font FONT      set font family
  --height HEIGHT  window height
  --width WIDTH    window width
</code></pre>
<p>Example:</p>
<pre><code class="language-bash"># Start the compiled exe
PsLauncher.exe --scale 2.0 # Scale 200%
PsLauncher.exe --scale 1.5 --light # Light theme, scale 150%

# Start from source code
python PsLauncher.py --scale 1.5 --light # Scale 150%
</code></pre>
<h3>Usage</h3>
<ul>
<li>After opening the program, add your script storage folder (e.g., the directory containing llama.cpp and littlem) via the menu bar "Settings - Add Script Directory".</li>
<li>The left-hand list will automatically scan and categorize all scripts in the directory. Click on a script to view its source code in a new tab.</li>
<li>Select a script and click "Start" to run it in a new tab, view real-time output, or perform interactive input (just like a real terminal). Click "Stop" to stop all related processes with one click.</li>
<li>Simple editing of the current script</li>
<li>Multiple tabs can be easily switched between. You can also scroll through tabs that extend beyond the screen using the mouse wheel.</li>
<li>The toolbar is movable.</li>
</ul>
<h3>Configuration</h3>
<p>You can also manually modify the configuration file.</p>
<ul>
<li>The program supports JSON format configuration files to store user-specified configurations such as scan paths and font sizes.</li>
<li>The default path to the configuration file is <code>config.json</code>, and its format is as follows:</li>
</ul>
<pre><code class="language-json">{
    &quot;folders&quot;: [
        &quot;C:/application/LLMexe/llama.cpp&quot;,
        &quot;C:/application/LLMexe/test_script&quot;,
        &quot;C:/application/LLMexe/litellm&quot;
    ],
    &quot;font_scale&quot;: 1.5,        // Interface font scaling factor (e.g., 1.5 is equivalent to 150% DPI scaling on Windows)
    &quot;dark_mode&quot;: true,        // Whether to enable dark mode (default is true)
    &quot;height_value&quot;: 1366,     // window size height
    &quot;width_value&quot;: 768,       // window size width
    &quot;font_family&quot;: &quot;Consolas&quot; // font family
}
</code></pre>
<h3>Notes</h3>
<ul>
<li>If you need to execute from source, please ensure that Python 3.x and Qt5/Qt6 are installed on your system.</li>
<li>In some case, the program may require administrator privileges to run (depending on the script content).</li>
<li>(Currently known issue): Terminal character coloring appears to be incorrect in some cases.</li>
<li>(Currently known issue): Within a terminal tab, you cannot use <code>ctrl+c</code> to copy while it is selected; this will directly send an interrupt signal. This may be due to the automatic capture of keystrokes when ctrl is pressed. If you need to copy content, please use the button in the toolbar.</li>
</ul>
<h2>Detailed Usage and Function Description</h2>
<h3>Program Interface Structure</h3>
<p>PsLauncher adopts a VSCode-like interface layout, mainly divided into the following areas:</p>
<ol>
<li><strong>Menu Bar</strong> - Located at the top of the window, organizing all operations by function.</li>
<li><strong>Toolbar</strong> - Below the menu bar, providing shortcut buttons for frequently used functions, which can be dragged to adjust their position.</li>
<li><strong>Left-side File List</strong> - An explorer displaying all script files in added folders.</li>
<li><strong>Right-side Tab Area</strong> - The main workspace, supporting multi-tab switching for viewing and editing.</li>
</ol>
<h3>Menu Bar Function Details</h3>
<h4>System Menu</h4>
<ul>
<li><strong>Save Current Configuration</strong> (F2) - Immediately saves the current configuration to a configuration file.</li>
<li><strong>Hide Window to System Tray</strong> (F10) - Hides the program window to the system tray, running it in the background.</li>
</ul>
<h4>File Menu</h4>
<ul>
<li><strong>Add Folder Path</strong> (F2) - Adds a new script folder to the scan list.</li>
<li><strong>Remove Selected Folder Path</strong> (F3) - Remove selected folders from the scan list</li>
</ul>
<h4>Edit Menu</h4>
<ul>
<li><strong>Copy Selected Content</strong> (F11) - Copy the text selected in the currently focused control</li>
<li><strong>Paste</strong> (F12) - Paste the clipboard content into the currently focused control</li>
<li><strong>Copy Tab All to Clipboard</strong> - Copy all text content of the current tab</li>
<li><strong>Edit Script Source Code</strong> (F4) - Enter/exit script editing mode, supports saving changes</li>
</ul>
<h4>Tools Menu</h4>
<ul>
<li><strong>Start Script</strong> (F5) - Run the currently selected script</li>
<li><strong>Terminate Script</strong> (F6) - Stop the script running in the current tab</li>
</ul>
<h4>Script Management Menu</h4>
<ul>
<li><strong>Create Path</strong> - Create a new folder under the selected folder</li>
<li><strong>Create Script</strong> - Create a new script file in the selected folder</li>
<li><strong>Rename Script</strong> - Rename the selected script file</li>
<li><strong>Copy Script</strong> - Copy the selected script file (can be renamed)</li>
<li><strong>Move Script</strong> - Move the script to another added folder</li>
<li><strong>Delete Script</strong> - Permanently delete the selected script file (without going through the recycle bin)</li>
</ul>
<h4>Tab Menu</h4>
<ul>
<li><strong>Close all source code tabs</strong> (F8) - Close all source code viewing tabs</li>
<li><strong>Close all run tabs</strong> (F9) - Close all terminal run tabs (will stop running processes)</li>
<li><strong>Close all tabs</strong> - Close all tabs, including source code and terminal tabs</li>
</ul>
<h4>Help Menu</h4>
<ul>
<li><strong>Help</strong> (F1) - Open help documentation</li>
<li><strong>About</strong> - Display program information and copyright information</li>
</ul>
<h3>Toolbar Function Details</h3>
<p>Toolbar buttons are grouped by function, separated by separators:</p>
<ol>
<li><strong>Window Management Group</strong></li>
<li>
<p>📌 <strong>Hide</strong> - Hides the window to the system tray. Hover tooltip: "Hidden window to system tray. Restore the window by clicking the tray icon."</p>
</li>
<li>
<p><strong>Script Control Group</strong></p>
</li>
<li>▶️ <strong>Run</strong> - Runs the script in the currently focused tab. Hover tooltip: "Runs the script in the currently focused tab."</li>
<li>
<p>⏹️ <strong>Abort</strong> - Aborts the script in the currently focused tab. Hover tooltip: "Aborts the script in the currently focused tab."</p>
</li>
<li>
<p><strong>Text Operation Group</strong></p>
</li>
<li>📋 <strong>Copy</strong> - Copies the currently selected text to the clipboard. Hover tooltip: "Copies the currently selected text to the clipboard."</li>
<li>📤 <strong>Paste</strong> - Pastes the current clipboard content to the cursor position. Hover tooltip: "Paste the current clipboard content to the cursor position."</li>
<li>
<p>📄 <strong>Copy All</strong> - Copy all text from the focused tab to the clipboard. Hovering tooltip: "Copy all text from the focused tab to the clipboard."</p>
</li>
<li>
<p><strong>Edit Function Group</strong></p>
</li>
<li>
<p>✏️ <strong>Quick Edit</strong> (💾 <strong>Save</strong>) - Enter/exit edit mode, save script changes. Hovering tooltip: "Enter/exit edit mode, save script changes" (changes to "Save script changes" in edit mode).</p>
</li>
<li>
<p><strong>Tab Management Group</strong></p>
</li>
<li>🗑️ <strong>Close All Source Code</strong> - Close all read-only source code viewing tabs. Hovering tooltip: "Close all read-only source code viewing tabs."</li>
<li>🚫 <strong>Terminate All Terminals</strong> - Close all terminal tabs, including running and terminated ones. Hovering tooltip: "Close all terminal tabs, including running and terminated ones."</li>
<li>💥 <strong>Close All Tabs</strong> - Close all tabs. This will close all source code tabs and all terminal tabs. If execution is in progress within a terminal, it will be forcibly terminated. Hovering tooltip: "Close all tabs, this will close all source code tabs." Simultaneously close all terminal tabs; if anything is running in the terminal, it will be forcibly terminated. This may prevent running programs or scripts from exiting normally.</li>
</ol>
<h3>Left-Side File List Functionality</h3>
<p>The left-side file list (Windows Explorer) is the main entry point for script management:</p>
<ol>
<li><strong>Click Actions</strong></li>
<li>Clicking a <strong>folder item</strong>: Expands/collapses the folder</li>
<li>
<p>Clicking a <strong>script item</strong>: Opens a new source code view tab on the right, displaying the script's source code</p>
</li>
<li>
<p><strong>File Type Support</strong></p>
</li>
<li>Supports <code>.ps1</code> (PowerShell scripts)</li>
<li>Supports <code>.bat</code> and <code>.cmd</code> (batch scripts)</li>
<li>
<p>Supports <code>.sh</code> (Bash scripts)</p>
</li>
<li>
<p><strong>Scanning Rules</strong></p>
</li>
<li>Only scans the root directory of added folders, not recursively scanning subdirectories</li>
<li>Real-time updates; refresh the display after adding/deleting files via the refresh menu</li>
</ol>
<h3>Right-Side Tab Functionality</h3>
<p>The right-side area uses a multi-tab design, supporting two types of tabs:</p>
<h4>1. Source Code View Tab (📝 prefix)</h4>
<ul>
<li><strong>View Mode</strong>: Default read-only mode, displays script source code</li>
<li>Supports syntax highlighting (PowerShell/Bash/Batch syntax)</li>
<li>Supports zoom in/out using Ctrl + mouse wheel</li>
<li>Dark theme background, similar to VSCode</li>
<li><strong>Edit Mode</strong>: Enter by clicking the "✏️ Quick Edit" button</li>
<li>Background color changes to dark gray for distinction</li>
<li>Script content can be modified</li>
<li>Click "💾 Save" to save changes after editing</li>
<li>Automatically handles UTF-8/GBK encoding (may not be very reliable...)</li>
</ul>
<h4>2. Terminal Run Tab (🖥️ prefix)</h4>
<ul>
<li><strong>ANSI Coloring Support</strong>: Correctly displays colored terminal output</li>
<li><strong>Interactive Input</strong>: Supports entering commands into running processes</li>
<li><strong>Process Control</strong>:</li>
<li>Run Script: Displays start timestamp and script path</li>
<li>Abort Script: Forcefully terminates the process and all its child processes</li>
<li>Process End: Displays end timestamp</li>
</ul>
<h3>Terminal Interactive Operation Guide</h3>
<p>The Terminal tab provides an interactive experience similar to a real terminal:</p>
<h4>Keyboard Operations</h4>
<ul>
<li><strong>Enter/Return Keys</strong>: Send the command of the current input line to the process.</li>
<li><strong>Ctrl+C</strong>: Send an interrupt signal to the running process (force termination).</li>
<li><strong>Ctrl+V</strong>: Paste clipboard content to the input location (does not send to the process).</li>
<li><strong>Backspace/Left Keys</strong>: Restrict deletion/moving within the input area; cannot modify historical output.</li>
</ul>
<h4>Input Protection Mechanism</h4>
<ul>
<li>Separate input and historical output areas.</li>
<li>Users can only edit within the current input line.</li>
<li>Prevents accidental modification of previously output content.</li>
<li>When copying output content, use the "Copy" button on the toolbar.</li>
</ul>
<h4>Process Management</h4>
<ul>
<li><strong>Start Process</strong>: Runs the script in a new tab, automatically calling the appropriate interpreter based on the file type.</li>
<li><strong>Terminate Process</strong>: Forcefully terminates the process tree, ensuring no residual processes.</li>
<li><strong>Process Status</strong>: Displays standard output and standard error streams in real time.</li>
<li><strong>Exception Handling</strong>: Displays appropriate prompts when a process exits abnormally.</li>
</ul>
<h3>Right-Click Menu</h3>
<p>The left-side file tree supports right-click menu operations. The right-side tabs also support corresponding right-click operations.</p>
<h3>System Tray Functions</h3>
<h4>Tray Icon Operations</h4>
<ul>
<li><strong>Click the tray icon</strong>: Restore the program window</li>
<li><strong>Right-click the tray icon</strong>: Display the tray menu</li>
</ul>
<h4>Tray Menu Functions</h4>
<ul>
<li><strong>Open Window</strong>: Restore the program from the tray</li>
<li><strong>Exit Program</strong>: Safely exit the program (will first attempt to stop all running scripts)</li>
</ul>
<h4>Tray Notifications</h4>
<ul>
<li>Display a notification message when hidden in the tray</li>
<li>Changes in program status can be detected via the tray icon</li>
</ul>
<h3>Keyboard Shortcuts Summary</h3>
<table>
<thead>
<tr>
<th>Keyboard Shortcuts</th>
<th>Functions</th>
<th>Descriptions</th>
</tr>
</thead>
<tbody>
<tr>
<td>F1</td>
<td>Open Help</td>
<td>Display Help Documentation</td>
</tr>
<tr>
<td>F2</td>
<td>Add Folder Path</td>
<td>Add New Script Folder</td>
</tr>
<tr>
<td>F3</td>
<td>Remove Folder Path</td>
<td>Remove Selected Folder</td>
</tr>
<tr>
<td>F4</td>
<td>Edit/Save Script</td>
<td>Switch Edit Mode or Save Changes</td>
</tr>
<tr>
<td>F5</td>
<td>Start Script</td>
<td>Run Currently Selected Script</td>
</tr>
<tr>
<td>F6</td>
<td>Terminate Script</td>
<td>Stop Currently Running Script</td>
</tr>
<tr>
<td>F8</td>
<td>Close All Source Code Tabs</td>
<td>Clear Source Code Viewing Tabs</td>
</tr>
<tr>
<td>F9</td>
<td>Close All Running Tabs</td>
<td>Clear Terminal Running Tabs</td>
</tr>
<tr>
<td>F10</td>
<td>Hide to System Tray</td>
<td>Minimize to Tray</td>
</tr>
<tr>
<td>F11</td>
<td>Copy Selected Content</td>
<td>Copy Selected Text</td>
</tr>
<tr>
<td>F12</td>
<td>Paste</td>
<td>Paste Clipboard Content</td>
</tr>
<tr>
<td>Ctrl+C</td>
<td>Interrupt Process</td>
<td>Send Interrupt Signal to Running Process</td>
</tr>
<tr>
<td>Ctrl+V</td>
<td>Paste Text</td>
<td>Paste into the current input location</td>
</tr>
</tbody>
</table>
<h3>Example Usage Flow</h3>
<ol>
<li><strong>Initial Setup</strong></li>
<li>Start the program</li>
<li>Click "File" → "Add Folder Path" or press F2</li>
<li>Select the folder containing the script (e.g., the llama.cpp directory)</li>
<li>
<p>The program automatically scans the script files in that folder</p>
</li>
<li>
<p><strong>Viewing and Editing the Script</strong></p>
</li>
<li>Click the script file in the file list on the left</li>
<li>The source code tab opens on the right to display the code</li>
<li>To modify, click the "✏️Quick Edit" button to enter edit mode</li>
<li>
<p>After modification, click "💾Save" to save the changes</p>
</li>
<li>
<p><strong>Running the Script</strong></p>
</li>
<li>Click the script file in the file list on the left</li>
<li>Click the "▶️Run" button in the toolbar or press F5</li>
<li>The terminal tab opens on the right to run the script</li>
<li>View the real-time output and perform interactive input</li>
<li>
<p>To stop, click the "⏹️Stop" button or press F6</p>
</li>
<li>
<p><strong>Multi-task Management</strong></p>
</li>
<li>Allows opening multiple scripts simultaneously to view source code.</li>
<li>Allows running multiple scripts simultaneously on different tabs.</li>
<li>Use the mouse wheel to scroll through the tab bar and switch tabs.</li>
<li>
<p>Use the tab management function to close tabs in batches.</p>
</li>
<li>
<p><strong>Runs in the background</strong></p>
</li>
<li>Click the "📌Hide" button in the toolbar or press F10.</li>
<li>The program window is hidden in the system tray.</li>
<li>The script continues to run in the background.</li>
<li>Click the tray icon to restore the window at any time.</li>
</ol>
<h3>Frequently Asked Questions</h3>
<p><strong>Q: How do I copy terminal output?</strong>
A: Use the "📋Copy" button in the toolbar to copy selected text, or use "📄Copy All" to copy the entire tab's content. Note: Pressing Ctrl+C directly in the terminal tab will send an interrupt signal to the process.</p>
<p><strong>Q: What if saving in edit mode fails?</strong>
A: This may be a file permission issue. Try running the program with administrator privileges, or check if the file is being used by another program.</p>
<p><strong>Q: How do I adjust the interface font size?</strong>
A: Start the program using the command-line parameter <code>--scale</code>, or modify the <code>font_scale</code> value in the configuration file.</p>
<p><strong>Q: What if there is no output after the script runs?</strong>
A: Check if the script requires interactive input. The terminal supports interactive operation. Try typing the command in the input area and pressing Enter.</p>
<p><strong>Q: How do I completely delete a script file?</strong>
A: Use the "Script Management" → "Delete Script" function. Note that this operation directly deletes the file without going through the recycle bin.</p>
<h2>Development Information and Developer Guidelines</h2>
<ul>
<li><strong>Language</strong>: Python 3.x</li>
<li><strong>GUI Framework</strong>: PyQt5 / PyQt6</li>
<li><strong>Script Execution</strong>: PowerShell</li>
<li><strong>Syntax Highlighting</strong>: PyQt-based syntax analysis module</li>
<li><strong>ANSI Support</strong>: ANSI highlighting via terminal emulator</li>
</ul>
<h3>Compilation Method</h3>
<p>First, ensure the environment is configured. Besides <code>requirements.txt</code>, you also need to run <code>pip install pyinstaller</code>.</p>
<p>Then, execute the following command:</p>
<pre><code class="language-bash">pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./
</code></pre>
<p>This program only has one icon representing media data, and this data has already been processed and hardcoded into the source code as base64. Therefore, no additional resource configuration is required; simply compile it.</p>
<h2>AI Developer Guidelines</h2>
<p>If you are an AI developer, pay special attention to this! During development, you should:</p>
<ul>
<li><strong>Ctrl+C</strong>: In the terminal tab, if text is selected, copy the selected text to the clipboard; otherwise, send an interrupt signal to the running process.</li>
<li><strong>Ctrl+V</strong>: Always paste clipboard content to the currently focused control, instead of sending it to the running program.</li>
<li>All toolbar buttons have corresponding menu items in the menu bar, organized by function:</li>
<li>Group toolbar buttons by function, using separators to separate different types of functions:</li>
<li>Maintain good coding and commenting style.</li>
<li><strong>Especially Important</strong>: This is a GUI program. Testing must and can only be done by humans. If you are an AI, after modifying it, perform a simple automatic syntax check, then finish and submit it to humans for further testing. As an AI, you do not need to execute the complete program because you may not have GUI operation capabilities. You, as the AI, have an obligation to inform humans which tests or interactive tests are needed.</li>
<li><strong>Especially Important</strong>: If you are an AI, never try to read <code>source_ico.py</code>. There's only one base64 encoded string here called <code>icon_base64_data</code>, used to provide the icon for the program. Reading it is meaningless and will only make your time and effort tedious.</li>
</ul>
<h2>Notice to Human Developers</h2>
<p>As a human, you have an obligation to assist the AI ​​in performing GUI functionality testing. Please check the following checklist item by item to confirm if it needs to be checked (e.g., if corresponding code has been modified, then it must be checked). The checklist is for reference only; please add it as needed if new requirements arise:</p>
<ul>
<li>[x] Normal startup</li>
<li>[x] Changing interface scaling via JSON configuration</li>
<li>[x] Menu bar functionality checked correctly</li>
<li>[x] Toolbar functionality checked correctly</li>
<li>[x] Toolbar position correct after dragging</li>
<li>[x] File Explorer displays correctly</li>
<li>[x] File Explorer right-click menu functionality checked correctly</li>
<li>[x] File Explorer: Copy, New, Delete, etc. functions</li>
<li>[x] Source code tabs function correctly</li>
<li>[x] Source code tab right-click menu</li>
<li>[x] Source code tab modification functionality, save, etc.</li>
<li>[x] Switching between multiple source code tabs</li>
<li>[x] Task terminal tabs function correctly</li>
<li>[x] Task terminal tab right-click menu</li>
<li>[x] Task terminal tab modification functionality, save, etc.</li>
<li>[x] Switching between multiple task terminal tabs</li>
<li>[x] Task terminal interactive input</li>
<li>[x] Task terminal interrupt function</li>
<li>[x] Task terminal: Can child processes exit normally when the tab is closed?</li>
<li>[x] Task terminal: Can child processes exit normally when all tabs are closed?</li>
<li>[x] Task terminal: Can child processes exit normally when the entire program exits?</li>
<li>[x] Task terminal: Multiple child processes do not affect each other</li>
<li>[x] Tray: Can be hidden</li>
<li>[x] Tray: Can be restored</li>
<li>[x] Tray: Tray display is normal</li>
<li>[x] Tray: Can exit without residual child processes</li>
<li>[x] Task terminal: After starting the script, it runs from the script path</li>
</ul>
<p>Remember to restore the check box after checking!</p>
<h2>Copyright</h2>
<p>NGC13009</p>
<p><a href="https://github.com/NGC13009/PsLauncher.git">NGC13009/PsLauncher</a></p>
<p>GPLv3 License</p>'''
