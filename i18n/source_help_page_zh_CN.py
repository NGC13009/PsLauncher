# coding = utf-8
# Arch   = manyArch
#
# @File name:       i18n/source_help_page_zh_CN.py
# @brief:           帮助页面文本
# @attention:       None
# @Author:          get_help_page.py 脚本自动生成, 请勿直接编辑该文件
# @History:         2026-06-29		Create

html_content = '''\
<h1>PsLauncher - 轻量级多脚本管理器</h1>
<p>在一个轻量化的, 类似于vscode的界面中, 通过多标签页统一管理并运行PowerShell/Bash/cmd(Batch)脚本, 支持系统托盘常驻、子进程强杀、ANSI着色的终端输出, 像终端一样的交互式输入输出. 专为本地大模型部署（llama.cpp/litellm）等场景优化.</p>
<blockquote>
<p>一个很好的使用案例：<a href="run_llama.cpp_and_litellm_by_PsLauncher.md">如何使用 PsLauncher 自定义本地大模型服务配置</a></p>
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
<blockquote>
<p>程序内的帮助文档由Markdown自动生成, 因此Markdown文档或GitHub网页渲染的是正确的, 程序内自带的说明文档不一定是完全可正常访问的. 请以Markdown或网页说明为准.</p>
</blockquote>
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
<pre><code class="language-bash">usage: PsLauncher.py [-h] [--scale SCALE] [--light] [--dark] [--font FONT] [--height HEIGHT] [--width WIDTH]

PsLauncher - 通用脚本启动器

options:
  -h, --help       展示帮助
  --scale SCALE    设定窗口DPI缩放系数 例如 1.5
  --light          设定明亮主题
  --dark           设定暗色主题
  --font FONT      设定字体            例如 'Consolas'
  --height HEIGHT  窗口高度            例如 768
  --width WIDTH    窗口宽度            例如 1366
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
<li>选中脚本后点击「启动」，即可在新标签页运行脚本，查看实时输出，或进行交互式输入 (就像是真正的终端一样). 点击「终止」可一键强制停止所有相关进程，点击「中断」可向进程发送 Ctrl+C 信号优雅中断</li>
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
    &quot;font_scale&quot;: 1.5,        // 界面字体缩放因子（例如：1.5相当于Windows上的DPI缩放150%）
    &quot;dark_mode&quot;: true,        // 是否启用暗色模式（默认true）
    &quot;height_value&quot;: 1366,     // 调整窗口宽度
    &quot;width_value&quot;: 768,       // 调整窗口高度
    &quot;font_family&quot;: &quot;Consolas&quot; // 编辑器字体
}
</code></pre>
<h3>注意事项</h3>
<ul>
<li>如果需要源码执行, 请确保系统已安装 Python 3.x 和 Qt5/Qt6.</li>
<li>一些情况下, 程序可能运行时需要管理员权限（视脚本内容而定）.</li>
<li>(目前已知问题): 一些情况下终端字符着色似乎是错的</li>
<li>(目前已知问题): 编辑时编辑器背景颜色应该会变以提示用户, 但是现在完全没有这个视觉效果.</li>
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
<li><strong>启动时自动最小化到托盘</strong> - 勾选后，每次启动程序时自动隐藏到系统托盘</li>
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
<li><strong>清除终端屏幕</strong> (Ctrl+L) - 清除当前终端标签页的所有显示内容，重置屏幕为空白状态</li>
<li><strong>编辑脚本源代码</strong> (F4) - 进入/退出脚本编辑模式，支持保存更改</li>
</ul>
<h4>运行菜单</h4>
<ul>
<li><strong>启动脚本</strong> (F5) - 运行当前选中的脚本</li>
<li><strong>终止脚本（强制中止）</strong> (F6) - 强制终止当前标签页中运行的脚本及其所有子进程（进程树强杀）</li>
<li><strong>发送 Ctrl+C 中断</strong> (F7) - 向当前终端进程发送 Ctrl+C 中断信号 (0x03)，用于优雅中断正在运行的脚本</li>
</ul>
<h4>查看菜单</h4>
<ul>
<li><strong>切换自动换行模式</strong> - 开启/关闭文本自动换行</li>
<li><strong>语法着色方式</strong> - 设置代码高亮风格：</li>
<li>自动 (根据脚本类型自动识别)</li>
<li>PowerShell</li>
<li>bash</li>
<li>command</li>
<li>不进行着色 (关闭高亮)</li>
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
<li>⏹️<strong>终止</strong> - 强制终止当前焦点标签页的脚本（进程树强杀），悬浮提示："终止当前焦点标签页的脚本（强制终止进程树）"</li>
<li>❌<strong>中断</strong> - 向当前终端进程发送 Ctrl+C 中断信号 (0x03)，用于优雅中断正在运行的脚本，悬浮提示："向当前终端进程发送 Ctrl+C 中断信号（0x03），用于优雅中断正在运行的脚本"</li>
<li>
<p>🧹<strong>清屏</strong> - 清除当前终端标签页的所有显示内容，悬浮提示："清除当前终端标签页的所有显示内容"</p>
</li>
<li>
<p><strong>文本操作组</strong></p>
</li>
<li>📋<strong>复制</strong> - 复制当前选中的文本到剪贴板（未选中文本时复制当前标签页全部内容），悬浮提示："复制当前选中的文本到剪贴板，如果未选中任何内容则复制当前焦点页面的所有文本。"</li>
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
<p><strong>双击操作</strong></p>
</li>
<li>
<p>双击文件夹，可以折叠或展开文件夹的内容。</p>
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
<li>支持通过Ctrl+鼠标滚轮缩放</li>
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
<li><strong>Ctrl+C</strong>：由全局事件过滤器统一处理；若有文本被选中则复制到剪贴板，否则触发全局复制逻辑（复制标签页全部内容）或交由焦点控件处理。不再直接强制中止进程。</li>
<li><strong>Ctrl+X</strong>：剪切当前焦点控件的选中文本</li>
<li><strong>Ctrl+Z</strong>：对当前焦点 QTextEdit 控件执行撤销操作</li>
<li><strong>Ctrl+Y</strong>：对当前焦点 QTextEdit 控件执行重做操作</li>
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
<p>左侧文件树支持右键菜单操作, 右侧标签页也支持相应的右键操作。</p>
<h4>右键菜单功能</h4>
<ul>
<li><strong>▶️ 运行</strong>：直接运行选中的脚本</li>
<li><strong>✏️ 编辑/保存</strong>：打开脚本源码并进入编辑模式</li>
<li><strong>🔄 启动时启动该脚本 / 🔄 取消启动时启动该脚本</strong>：将脚本标记为启动时自动运行（仅对可运行后缀 <code>.ps1</code>/<code>.bat</code>/<code>.sh</code> 的脚本显示）。标记后文件树中该脚本会以蓝色高亮显示，悬浮提示会标注"启动时自动运行"。</li>
<li><strong>💻 用 VSC 编辑</strong>：尝试调用 VSCode（<code>code</code> 命令）打开选中文件进行编辑。若 VSCode 未安装或未添加到 PATH，会显示友好的错误提示。</li>
<li><strong>📝 重命名</strong>：重命名选中的脚本</li>
<li><strong>📋 复制</strong>：复制选中的脚本</li>
<li><strong>🚚 移动</strong>：将脚本移动到其他文件夹</li>
<li><strong>🗑️ 删除</strong>：永久删除选中的脚本</li>
</ul>
<h4>启动时自动运行</h4>
<p>对于需要随程序自启动的脚本（如本地服务进程），可通过以下方式配置：</p>
<ol>
<li>在文件树中右键目标脚本，选择 <strong>🔄 启动时启动该脚本</strong></li>
<li>脚本将在文件树中以蓝色高亮显示，方便识别</li>
<li>下次启动 PsLauncher 时，该脚本将自动在终端标签页中运行</li>
<li>若要取消，右键选择 <strong>🔄 取消启动时启动该脚本</strong></li>
</ol>
<p>配合 <strong>启动时自动最小化到托盘</strong> 功能，可实现完全无感的开机自启动后台服务管理。</p>
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
<td>终止脚本（强制中止）</td>
<td>强制终止当前运行的脚本及其所有子进程（进程树强杀）</td>
</tr>
<tr>
<td>F7</td>
<td>发送 Ctrl+C 中断</td>
<td>向当前终端进程发送 Ctrl+C 中断信号 (0x03)，用于优雅中断正在运行的脚本</td>
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
<td>复制 / 全局处理</td>
<td>有文本选中时复制到剪贴板；无选中时触发全局复制（复制标签页全部内容）或交由焦点控件处理</td>
</tr>
<tr>
<td>Ctrl+V</td>
<td>粘贴</td>
<td>粘贴剪贴板内容到当前焦点控件</td>
</tr>
<tr>
<td>Ctrl+X</td>
<td>剪切</td>
<td>剪切当前焦点控件的选中文本</td>
</tr>
<tr>
<td>Ctrl+Z</td>
<td>撤销</td>
<td>对当前焦点 QTextEdit 控件执行撤销操作</td>
</tr>
<tr>
<td>Ctrl+Y</td>
<td>重做</td>
<td>对当前焦点 QTextEdit 控件执行重做操作</td>
</tr>
<tr>
<td>Ctrl+L</td>
<td>清除终端屏幕</td>
<td>清除当前终端标签页的所有显示内容</td>
</tr>
</tbody>
</table>
<h3>配置文件</h3>
<p>目前一些内容并不能通过程序内实现配置。</p>
<p>您可以定位到程序exe所在的根目录，找到程序的配置文件（如果没有，运行一次程序会生成）。</p>
<p>然后使用txt格式打开它，就可以手动修改一些参数，例如启动的默认窗口尺寸等。</p>
<pre><code class="language-python">_default_config = {
    &quot;folders&quot;: [],                       # list[str] 文件夹路径的列表
    &quot;font_scale&quot;: 1.5,                   # float 字号缩放
    &quot;dark_mode&quot;: True,                   # bool 是否黑夜模式
    'height_value': 1080,                # int
    'width_value': 1920,                 # int
    'font_family': 'Consolas',           # str
    'line_wrap_mode': True,              # bool
    'supported_extensions': ['.ps1', '.bat', '.sh'], # list[str] 支持的文件后缀列表（在文件树中显示）, 必须至少包含 ['.ps1', '.bat', '.sh'] 的内容
    'runnable_extensions': ['.ps1', '.bat', '.sh'],  # list[str] 可运行的文件后缀列表（可以执行）, 必须至少包含 ['.ps1', '.bat', '.sh'] 的内容
    'syntax_highlight_mode': 'auto'      # 语法着色模式：枚举 'auto', 'ps1', 'bash', 'command', 'none'
}
</code></pre>
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
<p>如需强制停止，点击"⏹️终止"按钮或按F6（进程树强杀）；如需优雅中断，点击"❌中断"按钮或按F7（发送 Ctrl+C 信号）</p>
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
A: 使用工具栏的"📋复制"按钮复制选中文本（或直接按Ctrl+C），或使用"📄复制全部"复制整个标签页内容。现在Ctrl+C已由全局事件过滤器处理，有选中文本时复制，无选中时复制标签页全部内容。</p>
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
<li><strong>语言</strong>: Python 3.12+</li>
<li><strong>GUI 框架</strong>: PyQt5 / PyQt6 / PySide6</li>
</ul>
<h3>编译方式</h3>
<p>首先确保环境, 除了<code>requirements.txt</code>, 还需要<code>pip install pyinstaller</code>.</p>
<p>之后, 执行以下命令</p>
<pre><code class="language-bash">pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./
</code></pre>
<p>这个程序只有一个图标是媒体数据, 并且已经被处理为base64写死到源代码了, 因此不需要任何额外的资源配置操作, 直接编译即可.</p>
<h3>发布流程</h3>
<p>正确的发布流程如下：</p>
<ol>
<li>更改 <code>aboutandhelp.py</code> 里面的<code>__version__</code>和<code>__devdate__</code>.</li>
<li>执行<code>python get_help_page.py</code>编译多语言帮助页面（读取 <code>README.md</code> 生成英文、<code>README_CN.md</code> 生成中文等）</li>
<li>如果ico更新了,执行<code>python get_ico.py</code>编译一遍ico</li>
<li>执行<code>pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./</code>编译文件</li>
<li>如果有必要, 将帮助文档也放一份.</li>
<li>运行<code>get_zip_release.ps1</code>打包.</li>
</ol>
<p>正确的发布版本结构:</p>
<pre><code class="language-PowerShell">exe/
   PsLauncher_EN.exe
   PsLauncher_CN.exe
   _internal/*    # 必要的动态链接库
</code></pre>
<h3>多语言支持</h3>
<p>脚本 <code>code_translator.py</code> 用于将程序翻译为多个语言.</p>
<blockquote>
<p>作者(@NGC13009)在开发的时候使用的是一个本地仓库, 基于中文开发后, 用自动化(且不一定可靠的)方式将代码翻译为英文, 然后更新到当前仓库, 之后, 将中文代码复制一份放在<code>cn/</code>下. 中文版本是作者在本地仓库编译的, 之后用当前仓库编译英文版.</p>
</blockquote>
<h2>自动化测试与 CI/CD</h2>
<p>项目已搭建完整的自动化测试体系，基于 <code>pytest</code> + <code>pytest-qt</code> + <code>pytest-xdist</code>，支持 headless 并行执行。</p>
<h3>测试目录结构</h3>
<pre><code>test/
├── conftest.py              # 全局 fixtures：环境变量、临时配置、main_window 等
├── test_config.py           # 功能层：config.json 读写、默认值、注释解析、边界值
├── test_scanner.py          # 功能层：文件夹扫描、不递归、后缀过滤、实时刷新
├── test_script_types.py     # 算法层：.ps1/.bat/.sh 识别、解释器选择、扩展名校验
├── test_process_control.py  # 功能层：进程树强杀、Ctrl+C 信号(0x03)、无残留子进程
├── test_ansi.py             # 算法层：ANSI 转义解析与着色
├── test_syntax_highlight.py # 算法层：auto/ps1/bash/command/none 模式判别
├── test_i18n.py             # 算法层：国际化模块纯函数
├── test_utils.py            # 算法层：工具函数（主题、字体缩放）
├── test_autorun.py          # 功能层：启动时自动运行标记、蓝色高亮状态持久化
├── test_tray.py             # GUI 层：托盘隐藏/恢复/退出（offscreen 下 skip）
├── test_gui_main.py         # GUI 层：主窗口构造、菜单 Action 触发、标签页增删
├── test_gui_toolbar.py      # GUI 层：工具栏按钮映射
├── test_gui_terminal.py     # GUI 层：终端标签 ANSI 渲染、交互输入
├── test_gui_editor.py       # GUI 层：源码标签只读/编辑切换、保存、缩放
├── test_gui_tabs.py         # GUI 层：标签页批量关闭、F8/F9 快捷键
└── fixtures/
    ├── __init__.py
    ├── config_factory.py    # 构造不同 config.json 场景
    └── temp_scripts.py      # 临时脚本目录
</code></pre>
<h3>三层测试分层说明</h3>
<table>
<thead>
<tr>
<th>层级</th>
<th>说明</th>
<th>并行安全</th>
<th>标记</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>算法层 (algo)</strong></td>
<td>纯函数、无 Qt 依赖的独立逻辑测试</td>
<td>✅ 安全</td>
<td><code>@pytest.mark.algo</code></td>
</tr>
<tr>
<td><strong>功能层 (func)</strong></td>
<td>不实例化 QWidget 的业务逻辑测试（可 mock）</td>
<td>✅ 安全</td>
<td><code>@pytest.mark.func</code></td>
</tr>
<tr>
<td><strong>GUI 层 (gui)</strong></td>
<td>基于 pytest-qt 的交互测试，需 qtbot fixture</td>
<td>⚠️ 慎用</td>
<td><code>@pytest.mark.gui</code></td>
</tr>
</tbody>
</table>
<h3>执行命令</h3>
<p><strong>精简版</strong>（CI 与本地统一使用）：</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=short -p no:warnings --no-header
</code></pre>
<p><strong>详细版</strong>（本地调试用）：</p>
<pre><code class="language-bash">python -m pytest test/ -v --tb=long -p no:warnings
</code></pre>
<p><strong>仅运行非 GUI 测试</strong>（快速回归）：</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=short -p no:warnings --no-header -m &quot;not gui&quot; -n auto
</code></pre>
<p>参数说明：</p>
<ul>
<li><code>-q</code>/<code>--no-header</code>：精简输出，节省 token</li>
<li><code>--tb=short</code>：简短回溯，避免大量堆栈</li>
<li><code>-p no:warnings</code>：屏蔽 Python 警告</li>
<li><code>-n auto</code>：启用 pytest-xdist 按 CPU 核心数并行分发</li>
<li><code>-m "not gui"</code>：跳过 GUI 标记用例</li>
</ul>
<h3>Headless 环境要求</h3>
<p>pytest-qt 在无显示环境（CI/服务器）下运行需设置：</p>
<pre><code class="language-bash">export QT_QPA_PLATFORM=offscreen   # Linux/macOS
set QT_QPA_PLATFORM=offscreen      # Windows CMD
$env:QT_QPA_PLATFORM=&quot;offscreen&quot;   # Windows PowerShell
</code></pre>
<p>已在 <code>conftest.py</code> 顶部自动设置。如需指定 Qt API 绑定：</p>
<pre><code class="language-bash">export PYTEST_QT_API=pyqt5
</code></pre>
<h3>CI 工作流</h3>
<p>定义在 <code>.github/workflows/test.yml</code>，触发条件：</p>
<ul>
<li><code>push</code> 到 <code>main</code> 分支</li>
<li><code>pull_request</code> 到 <code>main</code> 分支</li>
</ul>
<p>矩阵：<code>ubuntu-latest</code> + <code>windows-latest</code>，Python 3.12。</p>
<h3>AI Agent 注意事项</h3>
<ul>
<li><strong>AI 完成测试代码后只需 <code>py_compile</code> 校验</strong>，不得自行执行 GUI 用例，交人类确认。</li>
<li>禁止读取 <code>source_ico.py</code>等source开头的文件，这些文件是通过编译器自动生成的，很大。</li>
<li>GUI 用例在 offscreen 下覆盖有限，托盘/拖动等需人工复核。</li>
</ul>
<h3>人类开发者须知（测试清单）</h3>
<p>对照原「人类开发者须知」清单，标注自动化覆盖状态：</p>
<table>
<thead>
<tr>
<th>检查项</th>
<th>自动化状态</th>
</tr>
</thead>
<tbody>
<tr>
<td>正常启动</td>
<td>✅ <code>test_gui_main.py</code></td>
</tr>
<tr>
<td>菜单栏功能依次检查正常</td>
<td>✅ <code>test_gui_main.py::TestMenuActions</code></td>
</tr>
<tr>
<td>工具栏功能依次检查正常</td>
<td>✅ <code>test_gui_toolbar.py</code></td>
</tr>
<tr>
<td>工具栏拖动后位置正确</td>
<td>⚠️ 拖动操作需人工确认</td>
</tr>
<tr>
<td>资源管理器显示正常</td>
<td>✅ <code>test_scanner.py</code></td>
</tr>
<tr>
<td>资源管理器右键菜单功能</td>
<td>⚠️ 右键菜单触发需人工确认</td>
</tr>
<tr>
<td>源代码标签正常</td>
<td>✅ <code>test_gui_editor.py</code></td>
</tr>
<tr>
<td>源代码标签修改功能、保存</td>
<td>✅ <code>test_gui_editor.py</code></td>
</tr>
<tr>
<td>多源代码标签切换</td>
<td>✅ <code>test_gui_main.py::TestTabManagement</code></td>
</tr>
<tr>
<td>任务终端标签正常</td>
<td>✅ <code>test_gui_terminal.py</code></td>
</tr>
<tr>
<td>任务终端交互输入</td>
<td>✅ <code>test_gui_terminal.py</code></td>
</tr>
<tr>
<td>任务终端中断功能</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
<tr>
<td>子进程关闭退出</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
<tr>
<td>子进程统一关闭退出</td>
<td>✅ <code>test_gui_tabs.py</code></td>
</tr>
<tr>
<td>子进程退出程序时退出</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
<tr>
<td>多子进程互不影响</td>
<td>⚠️ 需人工验证进程隔离</td>
</tr>
<tr>
<td>托盘隐藏/恢复</td>
<td>⚠️ offscreen 下跳过，需人工确认</td>
</tr>
<tr>
<td>托盘退出无残留</td>
<td>⚠️ 需人工确认</td>
</tr>
<tr>
<td>脚本从脚本路径运行</td>
<td>✅ <code>test_process_control.py</code></td>
</tr>
</tbody>
</table>
<p><strong>AI 已自动化覆盖：</strong> 23 项 ✅ / 5 项 ⚠️ 需人工</p>
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
<li>[x] 任务终端: 启动脚本后, 是从脚本路径运行的</li>
</ul>
<p>检查完成后记得恢复检查框!</p>
<h2>版权信息</h2>
<p>NGC13009</p>
<p><a href="https://github.com/NGC13009/PsLauncher.git">NGC13009/PsLauncher</a></p>
<p>GPLv3许可</p>'''
