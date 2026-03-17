html_content = '''\
<h1>PsLauncher - 轻量级多脚本管理器</h1>
<p>在一个轻量化的, 类似于vscode的界面中, 通过多标签页统一管理并运行PowerShell/Bash/cmd(Batch)脚本, 支持系统托盘常驻、子进程强杀、ANSI着色的终端输出, 像终端一样的交互式输入输出. 专为本地大模型部署（llama.cpp/litellm）等场景优化.</p>
<blockquote>
<p><strong>开发动机与应用场景:</strong>
我想在自己电脑上本地运行大模型, 并且一直使用<a href="https://github.com/ollama/ollama">ollama</a>. 偶然, 我发现相较于<a href="https://github.com/ggml-org/llama.cpp">llama.cpp</a>, ollama总是占用更多的显存, 因此我决定使用llama.cpp作为本地大模型部署后端(不可思议,因为ollama其实也是llama.cpp套了一层而已). 但是llama.cpp自身不支持多进程, 什么都得手工管理. 因此我考虑能不能自己造一个ollama类似的玩意帮我管理的更好一些.
我在之前写过一个项目: <a href="https://github.com/NGC13009/ollama-launcher">ollama-launcher</a>. 它的目的就是纯粹的一个后端管理软件, 并且要求轻量化且迅速. 因此我考虑能不能搞一个类似的东西去实现我的需求?
调研后, 我发现<a href="https://github.com/BerriAI/litellm">litellm</a>是一个非常好的东西, 轻量化并且启动迅速, 这使得我没必要自己做一个网关去集散不同llama.cpp后端, 方便多了. 而且它不仅能管理本地模型并提供统一接口api, 而且还能把要钱的api也放到一起, 像是openrouter一样十分省事. 这样就不用来回配置多个程序的api了.
最开始, 我直接使用PowerShell的多个标签页, 通过启动写好配置的PowerShell脚本来手工启动litellm以及多个模型的llama.cpp. 我可以手工管理<code>GGUF</code>模型文件, 我觉得这无妨. 因此这个方案其实就能用了.
但是启动几个终端实在是不方便并且不够优雅, 并且我无法很方便的把他们扔到托盘后台去. 因此, 整合一下我们的目的....就诞生了这个程序.</p>
</blockquote>
<h2>核心亮点</h2>
<ul>
<li><strong>多类型脚本统一管理</strong>：支持PowerShell(.ps1)/Bash(.sh)/Batch(.bat), 支持多文件夹扫描且不递归子目录, 记忆配置文件. 让你方便的在一处管理你常用的脚本.</li>
<li><strong>类VSCode多标签体验</strong>：源码查看与脚本运行输出分标签管理, 支持语法高亮、ANSI着色.</li>
<li><strong>全生命周期进程控制</strong>：一键启动/中止脚本, 强杀所有关联子进程, 无残留进程.</li>
<li><strong>系统托盘常驻</strong>：一键隐藏到托盘, 后台不占窗口, 随时唤起使用.</li>
<li><strong>交互式终端支持</strong>：运行标签页支持实时输入, 适配交互式脚本.</li>
<li><strong>个性化界面定制</strong>：支持暗色/亮色主题切换, 字体大小/DPI缩放自由调节.</li>
</ul>
<h2>解决的痛点</h2>
<ul>
<li>比如本地部署llama.cpp、litellm等工具时, 多个脚本散落在不同文件夹, 每次运行要反复切换目录、找文件</li>
<li>或者同时启动多个服务时, 终端窗口混乱, 无法统一管理&amp;中止</li>
<li>一些项目的自动化脚本需要经常执行, 但是我就是运维, 我不想搞个IDE打开还得等几秒, 况且我的服务器不一定有足够的内存或者磁盘支持它.</li>
<li>只想简单管理运行脚本, 不想为了这个需求打开VSCode等重量级IDE</li>
<li>我的脚本运行时间长, 需要脚本工具后台常驻, 随时快速唤起执行, 不占用前台窗口资源, 也不会因为任务窗口分散我的注意力.</li>
</ul>
<h2>快速开始</h2>
<h3>安装</h3>
<p>两种方式:</p>
<ul>
<li>下载源代码并使用Python运行</li>
<li>下载编译好的exe并直接运行</li>
</ul>
<h4>源码使用</h4>
<pre><code class="language-Bash"># 配置环境
git clone https://github.com/NGC13009/PsLauncher.git
cd PsLauncher
pip install -r ./requirements.txt
</code></pre>
<h4>Windows编译好的exe</h4>
<p>从<a href="https://github.com/NGC13009/PsLauncher/releases">release</a>页面下载exe, 解压并双击运行即可. (或者命令行高级启动, 后面有详细说明)</p>
<h3>启动</h3>
<p>不管何种安装方式, 都有有两种启动方式:</p>
<ul>
<li>编译后<strong>双击exe直接启动</strong>程序, 这会自动载入相关配置.</li>
<li>通过命令行启动程序(或者Python源代码), 这可以设定两个参数, 设定一次后程序会保存配置文件, 后续无需再次设置.</li>
</ul>
<p>使用命令行:</p>
<pre><code class="language-bash">--scale N   界面字体缩放因子（例如: 1.5, 相当于Windows上的DPI缩放150%）
--light     添加该参数以使用亮色主题（默认暗色）
</code></pre>
<p>例子:</p>
<pre><code class="language-bash"># 编译后exe启动
PsLauncher.exe --scale 2.0                # 缩放200%
PsLauncher.exe --scale 1.5 --light        # 亮色主题，缩放150%

# 源码启动
python PsLauncher.py --scale 1.5 --light  # 缩放150%
</code></pre>
<h3>使用</h3>
<ul>
<li>打开程序后，通过菜单栏「设置-添加脚本目录」，添加你的脚本存放文件夹（如llama.cpp、litellm所在目录）</li>
<li>左侧列表会自动扫描并分类展示目录下的所有脚本，点击即可在新标签页查看源码</li>
<li>选中脚本后点击「启动」，即可在新标签页运行脚本，查看实时输出，或进行交互式输入 (就像是真正的终端一样). 点击「中止」可一键停止所有相关进程</li>
<li>简单编辑当前脚本</li>
<li>多个标签页可以方便切换查看, 使用鼠标滚轮也可以滚动超出屏幕的多个标签页.</li>
<li>工具栏是可以挪动位置的</li>
</ul>
<h3>配置</h3>
<p>你也可以手工修改配置文件.</p>
<ul>
<li>程序支持 JSON 格式的配置文件, 用于保存用户指定的扫描路径、字体大小等配置.</li>
<li>配置文件默认路径为 <code>config.json</code>, 格式如下:</li>
</ul>
<pre><code class="language-json">// PsLauncher 程序配置文件: 配置文件支持注释. 您可以在此手动添加要扫描的文件夹路径. 
{
    &quot;folders&quot;: [
        &quot;C:/application/LLMexe/llama.cpp&quot;,
        &quot;C:/application/LLMexe/test_script&quot;,
        &quot;C:/application/LLMexe/litellm&quot;
    ],
    &quot;font_scale&quot;: 1.5,  // 界面字体缩放因子（例如：1.5相当于Windows上的DPI缩放150%）
    &quot;dark_mode&quot;: true  // 是否启用暗色模式（默认true）
}
</code></pre>
<h3>注意事项</h3>
<ul>
<li>如果需要源码执行, 请确保系统已安装 Python 3.x 和 Qt5/Qt6.</li>
<li>一些情况下, 程序可能运行时需要管理员权限（视脚本内容而定）.</li>
<li>(目前已知问题): 一些情况下终端字符着色似乎是错的</li>
<li>(目前已知问题): 终端标签内, 在选中的时候无法使用<code>ctrl+c</code>复制, 这会直接发送中断信号. 这可能是按下ctrl时会自动先捕获按键导致的. 如果需要复制内容, 请使用工具栏的按钮.</li>
</ul>
<h2>详细使用方法与功能说明</h2>
<h3>程序界面构成</h3>
<p>PsLauncher 采用类 VSCode 的界面布局，主要分为以下几个区域：</p>
<ol>
<li><strong>菜单栏</strong> - 位于窗口顶部，按功能分类组织所有操作</li>
<li><strong>工具栏</strong> - 菜单栏下方，提供常用功能的快捷按钮，支持拖动调整位置</li>
<li><strong>左侧文件列表</strong> - 资源管理器，显示已添加文件夹中的所有脚本文件</li>
<li><strong>右侧标签页区域</strong> - 主要工作区，支持多标签页切换查看和编辑</li>
</ol>
<h3>菜单栏功能详解</h3>
<h4>系统菜单</h4>
<ul>
<li><strong>保存当前配置</strong> (F2) - 立即保存当前配置到配置文件</li>
<li><strong>隐藏窗口到系统托盘</strong> (F10) - 将程序窗口隐藏到系统托盘，后台运行</li>
</ul>
<h4>文件菜单</h4>
<ul>
<li><strong>添加文件夹路径</strong> (F2) - 添加新的脚本文件夹到扫描列表</li>
<li><strong>移除选中的文件夹路径</strong> (F3) - 从扫描列表中移除选中的文件夹</li>
</ul>
<h4>编辑菜单</h4>
<ul>
<li><strong>复制选定内容</strong> (F11) - 复制当前焦点控件中选中的文本</li>
<li><strong>粘贴</strong> (F12) - 将剪贴板内容粘贴到当前焦点控件</li>
<li><strong>复制标签页全部到剪贴板</strong> - 复制当前标签页全部文本内容</li>
<li><strong>编辑脚本源代码</strong> (F4) - 进入/退出脚本编辑模式，支持保存更改</li>
</ul>
<h4>工具菜单</h4>
<ul>
<li><strong>启动脚本</strong> (F5) - 运行当前选中的脚本</li>
<li><strong>终止脚本</strong> (F6) - 停止当前标签页中运行的脚本</li>
</ul>
<h4>脚本管理菜单</h4>
<ul>
<li><strong>新建路径</strong> - 在选中文件夹下创建新文件夹</li>
<li><strong>新建脚本</strong> - 在选中文件夹中创建新脚本文件</li>
<li><strong>重命名脚本</strong> - 重命名选中的脚本文件</li>
<li><strong>复制脚本</strong> - 复制选中的脚本文件（可重命名）</li>
<li><strong>移动脚本</strong> - 将脚本移动到其他已添加的文件夹</li>
<li><strong>删除脚本</strong> - 永久删除选中的脚本文件（不经过回收站）</li>
</ul>
<h4>标签菜单</h4>
<ul>
<li><strong>关闭所有源码标签页</strong> (F8) - 关闭所有源代码查看标签页</li>
<li><strong>关闭所有运行标签页</strong> (F9) - 关闭所有终端运行标签页（会停止运行中的进程）</li>
<li><strong>关闭所有标签页</strong> - 关闭所有标签页，包括源码和终端标签</li>
</ul>
<h4>帮助菜单</h4>
<ul>
<li><strong>帮助</strong> (F1) - 打开帮助文档</li>
<li><strong>关于</strong> - 显示程序信息和版权信息</li>
</ul>
<h3>工具栏功能详解</h3>
<p>工具栏按钮按功能分组，使用分隔符分隔：</p>
<ol>
<li><strong>窗口管理组</strong></li>
<li>
<p>📌<strong>隐藏</strong> - 隐藏窗口到系统托盘，悬浮提示："隐藏窗口到系统托盘, 通过单击托盘图标即可恢复窗口"</p>
</li>
<li>
<p><strong>脚本控制组</strong></p>
</li>
<li>▶️<strong>运行</strong> - 运行当前焦点标签页的脚本，悬浮提示："运行当前焦点标签页的脚本"</li>
<li>
<p>⏹️<strong>中止</strong> - 中止当前焦点标签页的脚本，悬浮提示："中止当前焦点标签页的脚本"</p>
</li>
<li>
<p><strong>文本操作组</strong></p>
</li>
<li>📋<strong>复制</strong> - 复制当前选中的文本到剪贴板，悬浮提示："复制当前选中的文本到剪贴板"</li>
<li>📤<strong>粘贴</strong> - 粘贴当前剪贴板内容到光标位置，悬浮提示："粘贴当前剪贴板内容到光标位置"</li>
<li>
<p>📄<strong>复制全部</strong> - 复制焦点标签页全部文本到剪贴板，悬浮提示："复制焦点标签页全部文本到剪贴板"</p>
</li>
<li>
<p><strong>编辑功能组</strong></p>
</li>
<li>
<p>✏️<strong>快速编辑</strong>（💾<strong>保存</strong>） - 进入/退出编辑模式，保存脚本更改，悬浮提示："进入/退出编辑模式，保存脚本更改"（编辑模式时变为"保存脚本更改"）</p>
</li>
<li>
<p><strong>标签页管理组</strong></p>
</li>
<li>🗑️<strong>关闭所有源码</strong> - 关闭所有只读源代码查看标签页，悬浮提示："关闭所有只读源代码查看标签页"</li>
<li>🚫<strong>中止所有终端</strong> - 关闭所有终端标签页，包括运行中的以及已经结束的，悬浮提示："关闭所有终端标签页, 包括运行中的以及已经结束的"</li>
<li>💥<strong>关闭所有标签</strong> - 关闭所有标签，这会关闭所有源代码标签页，同时关闭所有终端标签页，如果终端内正在执行，那么将强制中止，悬浮提示："关闭所有标签, 这会关闭所有源代码标签页, 同时关闭所有终端标签页, 如果终端内正在执行, 那么将强制中止. 可能导致执行中的程序或脚本不能正常退出."</li>
</ol>
<h3>左侧文件列表功能</h3>
<p>左侧文件列表（资源管理器）是脚本管理的主要入口：</p>
<ol>
<li><strong>单击操作</strong></li>
<li>单击<strong>文件夹项</strong>：展开/折叠文件夹</li>
<li>
<p>单击<strong>脚本项</strong>：在右侧打开一个新的源码查看标签页，显示脚本源代码</p>
</li>
<li>
<p><strong>文件类型支持</strong></p>
</li>
<li>支持 <code>.ps1</code> (PowerShell脚本)</li>
<li>支持 <code>.bat</code>、<code>.cmd</code> (批处理脚本)</li>
<li>
<p>支持 <code>.sh</code> (Bash脚本)</p>
</li>
<li>
<p><strong>扫描规则</strong></p>
</li>
<li>仅扫描已添加文件夹的根目录，不递归子目录</li>
<li>实时更新显示，添加/删除文件后可通过刷新菜单更新</li>
</ol>
<h3>右侧标签页功能</h3>
<p>右侧区域采用多标签页设计，支持两种类型的标签页：</p>
<h4>1. 源码查看标签页 (📝 前缀)</h4>
<ul>
<li><strong>查看模式</strong>：默认只读模式，显示脚本源代码</li>
<li>支持语法高亮（PowerShell/Bash/Batch语法）</li>
<li>支持代码折叠（通过Ctrl+鼠标滚轮缩放）</li>
<li>暗色主题背景，类似VSCode风格</li>
<li><strong>编辑模式</strong>：通过点击"✏️快速编辑"按钮进入</li>
<li>背景色变为深灰色以示区别</li>
<li>可修改脚本内容</li>
<li>编辑完成后点击"💾保存"保存更改</li>
<li>自动处理UTF-8/GBK编码 (可能也不是那么好用...)</li>
</ul>
<h4>2. 终端运行标签页 (🖥️ 前缀)</h4>
<ul>
<li><strong>ANSI着色支持</strong>：正确显示彩色终端输出</li>
<li><strong>交互式输入</strong>：支持向运行中的进程输入命令</li>
<li><strong>进程控制</strong>：</li>
<li>运行脚本：显示启动时间戳和脚本路径</li>
<li>中止脚本：强制终止进程及其所有子进程</li>
<li>进程结束：显示结束时间戳</li>
</ul>
<h3>终端交互式操作指南</h3>
<p>终端标签页提供类似真实终端的交互体验：</p>
<h4>键盘操作</h4>
<ul>
<li><strong>Enter/Return键</strong>：发送当前输入行的命令给进程</li>
<li><strong>Ctrl+C</strong>：发送中断信号给运行中的进程（强制中止）</li>
<li><strong>Ctrl+V</strong>：粘贴剪贴板内容到输入位置（不发送给进程）</li>
<li><strong>Backspace/Left键</strong>：限制在输入区域内删除/移动，不能修改历史输出</li>
</ul>
<h4>输入保护机制</h4>
<ul>
<li>输入区域和历史输出区域分离</li>
<li>用户只能在当前输入行内编辑</li>
<li>防止误操作修改已输出的历史内容</li>
<li>复制输出内容时，需使用工具栏的"复制"按钮</li>
</ul>
<h4>进程管理</h4>
<ul>
<li><strong>启动进程</strong>：在新标签页中运行脚本，自动根据文件类型调用相应解释器</li>
<li><strong>终止进程</strong>：强制终止进程树，确保无残留进程</li>
<li><strong>进程状态</strong>：实时显示标准输出和标准错误流</li>
<li><strong>异常处理</strong>：进程异常退出时显示相应提示</li>
</ul>
<h3>右键菜单</h3>
<p>左侧文件树支持右键菜单操作, 右侧标签页也支持相应的右键操作.</p>
<h3>系统托盘功能</h3>
<h4>托盘图标操作</h4>
<ul>
<li><strong>单击托盘图标</strong>：恢复显示程序窗口</li>
<li><strong>右键托盘图标</strong>：显示托盘菜单</li>
</ul>
<h4>托盘菜单功能</h4>
<ul>
<li><strong>打开窗口</strong>：从托盘恢复显示程序</li>
<li><strong>退出程序</strong>：安全退出程序（会先试图停止所有运行中的脚本）</li>
</ul>
<h4>托盘通知</h4>
<ul>
<li>隐藏到托盘时显示提示信息</li>
<li>程序状态变化时可通过托盘图标感知</li>
</ul>
<h3>快捷键汇总</h3>
<table>
<thead>
<tr>
<th>快捷键</th>
<th>功能</th>
<th>说明</th>
</tr>
</thead>
<tbody>
<tr>
<td>F1</td>
<td>打开帮助</td>
<td>显示帮助文档</td>
</tr>
<tr>
<td>F2</td>
<td>添加文件夹路径</td>
<td>添加新的脚本文件夹</td>
</tr>
<tr>
<td>F3</td>
<td>移除文件夹路径</td>
<td>移除选中的文件夹</td>
</tr>
<tr>
<td>F4</td>
<td>编辑/保存脚本</td>
<td>切换编辑模式或保存更改</td>
</tr>
<tr>
<td>F5</td>
<td>启动脚本</td>
<td>运行当前选中的脚本</td>
</tr>
<tr>
<td>F6</td>
<td>终止脚本</td>
<td>停止当前运行的脚本</td>
</tr>
<tr>
<td>F8</td>
<td>关闭所有源码标签页</td>
<td>清理源代码查看标签</td>
</tr>
<tr>
<td>F9</td>
<td>关闭所有运行标签页</td>
<td>清理终端运行标签</td>
</tr>
<tr>
<td>F10</td>
<td>隐藏到系统托盘</td>
<td>最小化到托盘运行</td>
</tr>
<tr>
<td>F11</td>
<td>复制选定内容</td>
<td>复制选中的文本</td>
</tr>
<tr>
<td>F12</td>
<td>粘贴</td>
<td>粘贴剪贴板内容</td>
</tr>
<tr>
<td>Ctrl+C</td>
<td>中断进程</td>
<td>发送中断信号给运行中的进程</td>
</tr>
<tr>
<td>Ctrl+V</td>
<td>粘贴文本</td>
<td>粘贴到当前输入位置</td>
</tr>
</tbody>
</table>
<h3>使用流程示例</h3>
<ol>
<li>
<p><strong>初始设置</strong></p>
</li>
<li>
<p>启动程序</p>
</li>
<li>点击"文件"→"添加文件夹路径"或按F2</li>
<li>选择包含脚本的文件夹（如llama.cpp目录）</li>
<li>
<p>程序自动扫描该文件夹下的脚本文件</p>
</li>
<li>
<p><strong>查看和编辑脚本</strong></p>
</li>
<li>
<p>在左侧文件列表中单击脚本文件</p>
</li>
<li>右侧打开源码标签页显示代码</li>
<li>如需修改，点击"✏️快速编辑"按钮进入编辑模式</li>
<li>
<p>修改后点击"💾保存"保存更改</p>
</li>
<li>
<p><strong>运行脚本</strong></p>
</li>
<li>
<p>在左侧文件列表中单击脚本文件</p>
</li>
<li>点击工具栏"▶️运行"按钮或按F5</li>
<li>右侧打开终端标签页运行脚本</li>
<li>查看实时输出，可进行交互式输入</li>
<li>
<p>如需停止，点击"⏹️中止"按钮或按F6</p>
</li>
<li>
<p><strong>多任务管理</strong></p>
</li>
<li>
<p>可同时打开多个脚本查看源码</p>
</li>
<li>可同时运行多个脚本在不同标签页</li>
<li>使用鼠标滚轮滚动标签栏切换标签页</li>
<li>
<p>使用标签管理功能批量关闭标签页</p>
</li>
<li>
<p><strong>后台运行</strong></p>
</li>
<li>
<p>点击工具栏"📌隐藏"按钮或按F10</p>
</li>
<li>程序窗口隐藏到系统托盘</li>
<li>脚本继续在后台运行</li>
<li>单击托盘图标随时恢复窗口</li>
</ol>
<h3>常见问题解答</h3>
<p><strong>Q: 如何复制终端输出内容？</strong>
A: 使用工具栏的"📋复制"按钮复制选中文本，或使用"📄复制全部"复制整个标签页内容。注意：在终端标签页中直接按Ctrl+C会发送中断信号给进程。</p>
<p><strong>Q: 编辑模式保存失败怎么办？</strong>
A: 可能是文件权限问题，请尝试以管理员权限运行程序，或检查文件是否被其他程序占用。</p>
<p><strong>Q: 如何调整界面字体大小？</strong>
A: 通过命令行参数 <code>--scale</code> 启动程序，或在配置文件中修改 <code>font_scale</code> 值。</p>
<p><strong>Q: 脚本运行后没有输出怎么办？</strong>
A: 检查脚本是否需要交互式输入，终端支持交互式操作，尝试在输入区域键入命令后按Enter键。</p>
<p><strong>Q: 如何彻底删除脚本文件？</strong>
A: 使用"脚本管理"→"删除脚本"功能，注意此操作直接删除文件，不经过回收站。</p>
<h2>开发信息与开发者须知</h2>
<ul>
<li><strong>语言</strong>: Python 3.x</li>
<li><strong>GUI 框架</strong>: PyQt5 / PyQt6</li>
<li><strong>脚本执行</strong>: PowerShell</li>
<li><strong>语法高亮</strong>: 基于 PyQt 的语法分析模块</li>
<li><strong>ANSI 支持</strong>: 通过终端模拟器实现 ANSI 着色</li>
</ul>
<h3>编译方式</h3>
<p>首先确保环境, 除了<code>requirements.txt</code>, 还需要<code>pip install pyinstaller</code>.</p>
<p>之后, 执行以下命令</p>
<pre><code class="language-bash">pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./
</code></pre>
<p>这个程序只有一个图标是媒体数据, 并且已经被处理为base64写死到源代码了, 因此不需要任何额外的资源配置操作, 直接编译即可.</p>
<h2>AI 开发者须知</h2>
<p>如果你是AI那尤其要好好看这里! 开发时应该尽可能:</p>
<ul>
<li><strong>Ctrl+C</strong>: 在终端标签页中, 如果有文本被选中, 则复制选中文本到剪贴板；否则发送中断信号给运行中的进程.</li>
<li><strong>Ctrl+V</strong>: 总是粘贴剪贴板内容到当前焦点控件, 而不是发送给运行中的程序.</li>
<li>所有工具栏按钮的功能都在菜单栏中有对应的菜单项, 按功能分类组织:</li>
<li>工具栏按钮按功能分组, 使用分隔符分隔不同类型的功能:</li>
<li>保持代码风格和注释风格</li>
<li><strong>尤其重要</strong>: 这是GUI程序, 测试必须且仅能由人类处理, 你如果是AI, 那么改好后进行简单的自动语法检查, 然后直接结束并提交给人类做进一步测试, 作为AI你无需执行完整程序, 因为你可能不具备GUI操作能力. 您作为AI有义务告知人类需要进行哪些测试或交互测试.</li>
<li><strong>尤其重要</strong>: 如果你是AI, 那么永远不要尝试读取<code>source_ico.py</code>, 这里面就一个base64编码的字符串叫<code>icon_base64_data</code>, 用于给程序提供图标. 读取它没有任何意义并且也会让你很累.</li>
</ul>
<h2>人类开发者须知</h2>
<p>您作为人类, 有义务协助ai执行GUI功能测试. 请按照下面的检查清单逐一确认是否需要检查 (比如更改过相应的代码, 那么就得检查). 清单仅供参考, 如果有新的需求请注意随时添加:</p>
<ul>
<li>[x] 正常启动</li>
<li>[x] 通过json配置更改界面缩放</li>
<li>[x] 菜单栏功能依次检查正常</li>
<li>[x] 工具栏功能依次检查正常</li>
<li>[x] 工具栏拖动后位置正确</li>
<li>[x] 资源管理器显示正常</li>
<li>[x] 资源管理器右键菜单功能依次检查正常</li>
<li>[x] 资源管理器: 复制, 新建, 删除等功能</li>
<li>[x] 源代码标签正常</li>
<li>[x] 源代码标签右键菜单</li>
<li>[x] 源代码标签修改功能, 保存等</li>
<li>[x] 多个源代码标签切换</li>
<li>[x] 任务终端标签正常</li>
<li>[x] 任务终端标签右键菜单</li>
<li>[x] 任务终端标签修改功能, 保存等</li>
<li>[x] 多个任务终端标签切换</li>
<li>[x] 任务终端交互输入</li>
<li>[x] 任务终端的中断功能</li>
<li>[x] 任务终端: 子进程是否可以在关闭标签页时正常退出</li>
<li>[x] 任务终端: 子进程是否可以在统一关闭标签页时正常退出</li>
<li>[x] 任务终端: 子进程是否可以在退出整个程序时正常退出</li>
<li>[x] 任务终端: 多个子进程相互不影响</li>
<li>[x] 托盘: 可隐藏</li>
<li>[x] 托盘: 可恢复</li>
<li>[x] 托盘: 托盘提示正常</li>
<li>[x] 托盘: 可退出且无残留子进程</li>
</ul>
<p>检查完成后记得恢复检查框!</p>
<h2>版权信息</h2>
<p>NGC13009</p>
<p><a href="https://github.com/NGC13009/PsLauncher.git">NGC13009/PsLauncher</a></p>
<p>GPLv3许可</p>'''
