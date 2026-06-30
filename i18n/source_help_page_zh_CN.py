# coding = utf-8
# Arch   = manyArch
#
# @File name:       i18n/source_help_page_zh_CN.py
# @brief:           帮助页面文本
# @attention:       None
# @Author:          get_help_page.py 脚本自动生成, 请勿直接编辑该文件
# @History:         2026-06-29		Create

html_content = '''\
<h1>PsLauncher — 面向本地 LLM 场景的轻量脚本编排器</h1>
<p>在一个类 VSCode 的轻量界面中统一管理并运行 PowerShell / Bash / Batch 脚本，同时内置一套 HTTP API 服务，<strong>让人与 AI Agent 能以同一套语义异步的，非阻塞的操作统一管理的本地服务进程</strong>：启动、交互、强杀、查输出、批量回收。支持系统托盘常驻、子进程树强杀、ANSI 着色终端与交互式输入输出，专为 llama.cpp / Ollama / litellm 等本地大模型部署场景优化。兼容Windows，Linux，macos等。</p>
<center><a href='./README_CN.md'>中文说明书</a> | <a href='./README.md'>English version</a></center>

<p><img alt="pic" src="pic.jpg" /></p>
<center>图. PsLauncher的运行状态展示</center>

<h2>核心亮点</h2>
<ul>
<li><strong>ai不再因为程序进程而阻塞</strong>：当程序执行在终端内的时候，ai仍旧可以选择随时查看日志或进行其他操作。同时管理多个程序的输入输出，彻底解耦程序和ai的交互时序问题。</li>
<li><strong>人机同源的双向控制</strong>：打破AI Agent与人类操作的隔离墙，机器的指令与人工的图形界面操作共享同一状态，消除人机双轨制带来的状态冲突与接管壁垒，真正实现AI执行、人可接管。</li>
<li><strong>异构脚本的统一治理</strong>：终结本地大模型生态中各类推理脚本分散、异构的混乱局面，将不同目录、不同语言的启动逻辑收敛为单一调度视角，大幅降低环境维护的心智负担。</li>
<li><strong>计算资源的确定性回收</strong>：直击僵尸进程与显存泄漏的顽疾，提供从优雅终止到进程树强杀的彻底回收能力，保障硬件资源在多服务切换中的稳定释放。不再产生cpu/内存/GPU的额外占用。</li>
<li><strong>长任务的动态托管闭环</strong>：将传统终端从一次性升级为可视化任务容器，支持在任务运行期间随时查阅历史轨迹并动态注入新指令，完美适配AI长时编排与交互式脚本的运行诉求。无惧程序卡死导致agent loop被打断。</li>
<li><strong>全场景形态的无缝切换</strong>：兼顾桌面开发的低打扰常驻需求与无头服务器的纯后端托管诉求，以同一套系统消除不同部署环境下的体验割裂。</li>
</ul>
<pre><code class="language-mermaid">flowchart TB
    %% 定义节点样式
    classDef agentNode fill:#e1f5fe,stroke:#03a9f4,stroke-width:2px,color:#0d47a1;
    classDef plNode fill:#fff8e1,stroke:#ffa000,stroke-width:2px,color:#e65100;
    classDef svcNode fill:#e8f5e9,stroke:#43a047,stroke-width:2px,color:#1b5e20;
    classDef apiNode fill:#ffebee,stroke:#d32f2f,stroke-width:3px,color:#b71c1c;
    classDef guiNode fill:#f3e5f5,stroke:#8e24aa,stroke-width:2px,color:#4a148c;

    subgraph Agent[&quot;AI Agent loop&quot;]
        AGENT[&quot;AI Agent&quot;]:::agentNode
        skill[&quot;LLM + skill.md&quot;]:::agentNode
    end

    subgraph GUI[&quot;人类操作界面&quot;]
        traynode[&quot;托盘&quot;]:::guiNode
        GUIUI[&quot;用户图形界面&quot;]:::guiNode
    end

    subgraph PL[&quot;PsLauncher 内核&quot;]
        direction TB
        API[&quot;HTTP API&lt;br/&gt;(AI 调用接口)&quot;]:::apiNode
        core[&quot;进程调度器&quot;]:::apiNode
        logctrl[&quot;日志上下文管理&quot;]:::apiNode
    end

    subgraph SVCS[&quot;本地服务进程&quot;]
        LLAMA[&quot;llama.cpp&quot;]:::svcNode
        OLLAMA[&quot;Ollama&quot;]:::svcNode
        LITELLM[&quot;LiteLLM&quot;]:::svcNode
        TRAIN[&quot;模型训练进程&quot;]:::svcNode
        LORA[&quot;LoRA微调任务&quot;]:::svcNode
        CUSTOM[&quot;自定义脚本&quot;]:::svcNode
    end

    %% 核心交互流
    Agent &lt;==&gt;|&quot;调用API&lt;br/&gt;(运行/管理/交互/回传结果)&quot;| PL

    %% GUI 与编排层交互
    GUI &lt;==&gt;|&quot;双向同步&lt;br/&gt;(状态共享)&quot;| PL
    GUI -.-&gt;|&quot;人工接管/监控&quot;| PL

    %% 服务管理
    PL --&gt;|&quot;统一调度&quot;| LLAMA
    PL --&gt;|&quot;统一调度&quot;| OLLAMA
    PL --&gt;|&quot;统一调度&quot;| LITELLM
    PL --&gt;|&quot;统一调度&quot;| TRAIN
    PL --&gt;|&quot;统一调度&quot;| LORA
    PL --&gt;|&quot;统一调度&quot;| CUSTOM
</code></pre>
<center>图. PsLauncher的架构原理与亮点技术</center>

<h2>解决的痛点</h2>
<ul>
<li><strong>环境碎片化与调度混乱</strong>：各类推理工具与网关的脚本散落在不同角落，多服务并行时面临终端窗口爆炸、参数记忆繁琐等问题。缺乏一个统一的控制中枢来消除手动穿梭目录与环境切换的割裂感。</li>
<li><strong>资源泄漏与硬件冲突</strong>：异常退出后常遗留难以清理的僵尸子进程，导致处理器/内存/显存被隐性占用，下一次启动时频发硬件资源冲突，缺乏强有力的生命周期兜底机制。</li>
<li><strong>AI与本地环境的交互鸿沟</strong>：大模型难以稳定、安全地操控本地计算环境。传统的Shell命令脆弱且缺乏自描述性，Agent亟需一种结构化、可自省的接口来形成"启动-监控-交互-回收"的闭环控制。</li>
<li><strong>AI agent和程序执行的异步问题</strong>：传统harness程序的agent loop会被程序或脚本执行打断，同步式的阻塞处理可能因脚本超时或者脚本停止执行而中断，因此需要使用更为统一的异步访问接口的令agent处理程序或脚本的输入输出，统一管控进程生命周期。</li>
<li><strong>重运维与轻需求的错位</strong>：管理本地脚本往往被迫引入重量级IDE或复杂的容器编排系统，对于仅需简单调度与后台常驻的需求而言，系统开销与学习成本过高，亟需一种零侵入的轻量化方案。</li>
</ul>
<hr />
<h2>快速开始</h2>
<blockquote>
<p>注意：PsLauncher程序内的帮助文档由Markdown自动生成, 因此Markdown文档或GitHub网页渲染的是正确的, 程序内自带的说明文档不一定是完全可正常访问的. 如果存在渲染问题，请以Markdown或<a href="https://github.com/NGC13009/PsLauncher.git">网页说明</a>为准.</p>
</blockquote>
<h3>安装</h3>
<p>两种方式:</p>
<ul>
<li>下载源代码并使用Python运行</li>
<li>下载编译好的exe并直接运行</li>
</ul>
<h4>源码使用</h4>
<pre><code class="language-Bash">git clone https://github.com/NGC13009/PsLauncher.git
cd PsLauncher
pip install -r ./requirements.txt
</code></pre>
<h4>Windows编译好的exe</h4>
<p>从<a href="https://github.com/NGC13009/PsLauncher/releases">release</a>页面下载exe。</p>
<h3>启动</h3>
<p>可直接双击 exe 启动，或通过命令行启动（参数仅首次需指定，程序会自动保存配置）：</p>
<pre><code class="language-bash"># 编译后exe启动
PsLauncher.exe

# 源码启动
python PsLauncher.py
</code></pre>
<h3>使用</h3>
<h4>对于人类用户的直接使用方式</h4>
<ol>
<li>通过菜单栏「设置 → 添加脚本目录」，添加你的脚本存放文件夹</li>
<li>左侧列表会自动扫描并展示目录下匹配指定后缀的所有脚本，单击脚本即可查看源码</li>
<li>选中脚本后点击「启动」（或按 <code>F5</code>），即可在新标签页运行脚本，查看实时输出</li>
<li>点击「终止」（或按 <code>F6</code>）强制停止进程，点击「中断」（或按 <code>F7</code>）发送 <code>Ctrl+C</code> 优雅中断
一个完整使用案例：<a href="run_llama.cpp_and_litellm_by_PsLauncher.md">如何使用 PsLauncher 自定义的管控本地大模型服务配置，运行实例等</a></li>
</ol>
<h4>通过 skill 向 AI AGENT 接入 PsLauncher</h4>
<p>你可以将PsLauncher作为skill.md接入你的agent工作流。例如，将本README.md（考虑您的ai能看懂的语言版本）放置于 AI AGENT 的skill文件夹内，然后启动一个PsLauncher实例：</p>
<pre><code class="language-bash"># 编译后exe启动
PsLauncher.exe

# 不启动GUI
PsLauncher.exe  --headless

# 或者修改配置文件，令启动时自动最小化到托盘（这同时方便人类随时查看状态）。
</code></pre>
<p>之后ai即可调用 PsLauncher 进行异步的脚本或进程的启停管控。</p>
<blockquote>
<ul>
<li>对于程序，需要写成执行指令的脚本，以使用PsLauncher进行管理。</li>
<li>如果只使用LLM操作，那推荐使用<a href="pslauncher_skill.md">pslauncher_skill.md</a>来作为技能，因为这个文件仅包含api端点调用的说明。</li>
<li>如有必要，请自行翻译获得所需语言的<code>skill.md</code>。例如中文版是<a href="pslauncher_skill_CN.md">pslauncher_skill_CN.md</a>。</li>
<li>如果需要人类同时使用，那推荐使用本README，因为它还包括了GUI使用说明，这能让你和ai聊天的时候获得来自于ai看过说明书学会的操作提示。</li>
</ul>
</blockquote>
<h4>使用其他程序监听更改</h4>
<p>PsLauncher 同时暴露一个 <strong>TCP 长连接事件服务器</strong>（默认端口 <code>13026</code>），用于将程序内部的状态变化推送给外部程序。当你需要将 PsLauncher 的状态集成到自动化运维监控、LLM Agent 的实时感知流程，或其他需要实时同步的场景时（例如一个 AI Agent 监控多个自动化脚本的提示信息输出，或跨进程同步操作状态），无需轮询 HTTP API，只需建立一个 TCP 长连接即可持续接收事件推送。</p>
<blockquote>
<p>详细的事件类型、配置方式和监听脚本使用方法，请参见本说明书的「<a href="#TCP事件服务器">TCP 事件服务器</a>」章节。</p>
<ul>
<li>该功能可能对于机器人场景非常有效，因为多个驱动可能同时执行，PsLauncher可以提供统一的上下文环境与异步执行过程，并将机器人的驱动（例如伺服电机，舵机等）与LLM端进行很好的解耦。</li>
</ul>
</blockquote>
<p>如果上面的内容看完后，加上程序摸索了一遍，想进一步探索，请继续阅读说明书。</p>
<hr />
<h2>详细使用方法与功能说明</h2>
<p>下面的说明书包含了几乎程序所有功能的说明，十分详细，没有重点。建议通过ai搜索自己感兴趣的功能并令ai向您解释使用方法，而非直接阅读本说明。</p>
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
<li><strong>保存当前配置</strong> (<code>F2</code>) - 立即保存当前配置到配置文件</li>
<li><strong>隐藏窗口到系统托盘</strong> (<code>F10</code>) - 将程序窗口隐藏到系统托盘，后台运行</li>
<li><strong>启动时自动最小化到托盘</strong> - 勾选后，每次启动程序时自动隐藏到系统托盘</li>
<li><strong>编辑配置文件</strong> - 允许编辑所有配置，但是这个界面是自动展开所有配置的GUI用于用户修改，十分简陋，除非找不到程序中正规的配置项目，或者本身程序不提供设置方式，或者不想编辑配置文件，那么可以从此处修改配置项。</li>
</ul>
<h4>文件菜单</h4>
<ul>
<li><strong>添加文件夹路径</strong> (<code>F2</code>) - 添加新的脚本文件夹到扫描列表</li>
<li><strong>移除选中的文件夹路径</strong> (<code>F3</code>) - 从扫描列表中移除选中的文件夹</li>
</ul>
<h4>编辑菜单</h4>
<ul>
<li><strong>复制选定内容</strong> (<code>F11</code>) - 复制当前焦点控件中选中的文本</li>
<li><strong>粘贴</strong> (<code>F12</code>) - 将剪贴板内容粘贴到当前焦点控件</li>
<li><strong>复制标签页全部到剪贴板</strong> - 复制当前标签页全部文本内容</li>
<li><strong>清除终端屏幕</strong> (<code>Ctrl+L</code>) - 清除当前终端标签页的所有显示内容，重置屏幕为空白状态</li>
<li><strong>编辑脚本源代码</strong> (<code>F4</code>) - 进入/退出脚本编辑模式，支持保存更改</li>
</ul>
<h4>运行菜单</h4>
<ul>
<li><strong>启动脚本</strong> (<code>F5</code>) - 运行当前选中的脚本</li>
<li><strong>终止脚本（强制中止）</strong> (<code>F6</code>) - 强制终止当前标签页中运行的脚本及其所有子进程（进程树强杀）</li>
<li><strong>发送 Ctrl+C 中断</strong> (<code>F7</code>) - 向当前终端进程发送 <code>Ctrl+C</code> 中断信号 (<code>0x03</code>)，用于优雅中断正在运行的脚本</li>
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
<li><strong>关闭所有源码标签页</strong> (<code>F8</code>) - 关闭所有源代码查看标签页</li>
<li><strong>关闭所有运行标签页</strong> (<code>F9</code>) - 关闭所有终端运行标签页（会停止运行中的进程）</li>
<li><strong>关闭所有标签页</strong> - 关闭所有标签页，包括源码和终端标签</li>
</ul>
<h4>帮助菜单</h4>
<ul>
<li><strong>帮助</strong> (<code>F1</code>) - 打开帮助文档</li>
<li><strong>关于</strong> - 显示程序信息和版权信息</li>
</ul>
<h3>工具栏功能详解</h3>
<p>工具栏按钮按功能分组，使用分隔符分隔：</p>
<ol>
<li><strong>窗口管理组</strong></li>
<li>📌<strong>隐藏</strong> - 隐藏窗口到系统托盘，悬浮提示：<code>隐藏窗口到系统托盘, 通过单击托盘图标即可恢复窗口</code></li>
<li><strong>脚本控制组</strong></li>
<li>▶️<strong>运行</strong> - 运行当前焦点标签页的脚本，悬浮提示：<code>运行当前焦点标签页的脚本</code></li>
<li>⏹️<strong>终止</strong> - 强制终止当前焦点标签页的脚本（进程树强杀），悬浮提示：<code>终止当前焦点标签页的脚本（强制终止进程树）</code></li>
<li>❌<strong>中断</strong> - 向当前终端进程发送 <code>Ctrl+C</code> 中断信号 (<code>0x03</code>)，用于优雅中断正在运行的脚本，悬浮提示：<code>向当前终端进程发送 Ctrl+C 中断信号（0x03），用于优雅中断正在运行的脚本</code></li>
<li>🧹<strong>清屏</strong> - 清除当前终端标签页的所有显示内容，悬浮提示：<code>清除当前终端标签页的所有显示内容</code></li>
<li><strong>文本操作组</strong></li>
<li>📋<strong>复制</strong> - 复制当前选中的文本到剪贴板（未选中文本时复制当前标签页全部内容），悬浮提示：<code>复制当前选中的文本到剪贴板，如果未选中任何内容则复制当前焦点页面的所有文本。</code></li>
<li>📤<strong>粘贴</strong> - 粘贴当前剪贴板内容到光标位置，悬浮提示：<code>粘贴当前剪贴板内容到光标位置</code></li>
<li>📄<strong>复制全部</strong> - 复制焦点标签页全部文本到剪贴板，悬浮提示：<code>复制焦点标签页全部文本到剪贴板</code></li>
<li><strong>编辑功能组</strong></li>
<li>✏️<strong>快速编辑</strong>（💾<strong>保存</strong>） - 进入/退出编辑模式，保存脚本更改，悬浮提示：<code>进入/退出编辑模式，保存脚本更改</code>（编辑模式时变为<code>保存脚本更改</code>）</li>
<li><strong>标签页管理组</strong></li>
<li>🗑️<strong>关闭所有源码</strong> - 关闭所有只读源代码查看标签页，悬浮提示：<code>关闭所有只读源代码查看标签页</code></li>
<li>🚫<strong>中止所有终端</strong> - 关闭所有终端标签页，包括运行中的以及已经结束的，悬浮提示：<code>关闭所有终端标签页, 包括运行中的以及已经结束的</code></li>
<li>💥<strong>关闭所有标签</strong> - 关闭所有标签，这会关闭所有源代码标签页，同时关闭所有终端标签页，如果终端内正在执行，那么将强制中止，悬浮提示：<code>关闭所有标签, 这会关闭所有源代码标签页, 同时关闭所有终端标签页, 如果终端内正在执行, 那么将强制中止. 可能导致执行中的程序或脚本不能正常退出.</code></li>
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
<li>支持通过 <code>Ctrl+鼠标滚轮</code> 缩放</li>
<li>暗色主题背景，类似VSCode风格</li>
<li><strong>编辑模式</strong>：通过点击 <code>✏️快速编辑</code> 按钮进入</li>
<li>背景色变为深灰色以示区别</li>
<li>可修改脚本内容</li>
<li>编辑完成后点击 <code>💾保存</code> 保存更改</li>
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
<li><strong><code>Enter/Return键</code></strong>：发送当前输入行的命令给进程</li>
<li><strong><code>Ctrl+C</code></strong>：由全局事件过滤器统一处理；若有文本被选中则复制到剪贴板，否则触发全局复制逻辑（复制标签页全部内容）或交由焦点控件处理。不再直接强制中止进程。</li>
<li><strong><code>Ctrl+X</code></strong>：剪切当前焦点控件的选中文本</li>
<li><strong><code>Ctrl+Z</code></strong>：对当前焦点 QTextEdit 控件执行撤销操作</li>
<li><strong><code>Ctrl+Y</code></strong>：对当前焦点 QTextEdit 控件执行重做操作</li>
<li><strong><code>Ctrl+V</code></strong>：粘贴剪贴板内容到输入位置（不发送给进程）</li>
<li><strong><code>Backspace/Left键</code></strong>：限制在输入区域内删除/移动，不能修改历史输出</li>
</ul>
<h4>输入保护机制</h4>
<ul>
<li>输入区域和历史输出区域分离</li>
<li>用户只能在当前输入行内编辑</li>
<li>防止误操作修改已输出的历史内容</li>
<li>复制输出内容时，需使用工具栏的 <code>复制</code> 按钮</li>
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
<h4>右键菜单功能（文件树）</h4>
<p><strong>文件夹右键菜单：</strong></p>
<ul>
<li><strong>📂 在资源管理器中打开</strong>：在系统文件管理器中打开该文件夹</li>
<li><strong>📂 移除文件夹路径</strong>：从扫描列表中移除当前文件夹（弹出二次确认对话框）</li>
<li><strong>📂 添加文件夹路径</strong>：添加新的脚本文件夹到扫描列表
<strong>脚本文件右键菜单：</strong></li>
<li><strong>▶️ 运行</strong>：直接运行选中的脚本</li>
<li><strong>✏️ 编辑/保存</strong>：打开脚本源码并进入编辑模式</li>
<li><strong>🔄 启动时启动该脚本 / 🔄 取消启动时启动该脚本</strong>：将脚本标记为启动时自动运行（仅对可运行后缀 <code>.ps1</code>/<code>.bat</code>/<code>.sh</code> 的脚本显示）。标记后文件树中该脚本会以蓝色高亮显示，悬浮提示会标注<code>启动时自动运行</code>。</li>
<li><strong>💻 用 VSC 编辑</strong>：尝试调用 VSCode（<code>code</code> 命令）打开选中文件进行编辑。若 VSCode 未安装或未添加到 PATH，会显示友好的错误提示。</li>
<li><strong>📝 重命名</strong>：重命名选中的脚本</li>
<li><strong>📋 复制</strong>：复制选中的脚本</li>
<li><strong>🚚 移动</strong>：将脚本移动到其他文件夹</li>
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
<td><code>F1</code></td>
<td>打开帮助</td>
<td>显示帮助文档</td>
</tr>
<tr>
<td><code>F2</code></td>
<td>添加文件夹路径</td>
<td>添加新的脚本文件夹</td>
</tr>
<tr>
<td><code>F3</code></td>
<td>移除文件夹路径</td>
<td>移除选中的文件夹</td>
</tr>
<tr>
<td><code>F4</code></td>
<td>编辑/保存脚本</td>
<td>切换编辑模式或保存更改</td>
</tr>
<tr>
<td><code>F5</code></td>
<td>启动脚本</td>
<td>运行当前选中的脚本</td>
</tr>
<tr>
<td><code>F6</code></td>
<td>终止脚本（强制中止）</td>
<td>强制终止当前运行的脚本及其所有子进程（进程树强杀）</td>
</tr>
<tr>
<td><code>F7</code></td>
<td>发送 <code>Ctrl+C</code> 中断</td>
<td>向当前终端进程发送 <code>Ctrl+C</code> 中断信号 (<code>0x03</code>)，用于优雅中断正在运行的脚本</td>
</tr>
<tr>
<td><code>F8</code></td>
<td>关闭所有源码标签页</td>
<td>清理源代码查看标签</td>
</tr>
<tr>
<td><code>F9</code></td>
<td>关闭所有运行标签页</td>
<td>清理终端运行标签</td>
</tr>
<tr>
<td><code>F10</code></td>
<td>隐藏到系统托盘</td>
<td>最小化到托盘运行</td>
</tr>
<tr>
<td><code>F11</code></td>
<td>复制选定内容</td>
<td>复制选中的文本</td>
</tr>
<tr>
<td><code>F12</code></td>
<td>粘贴</td>
<td>粘贴剪贴板内容</td>
</tr>
<tr>
<td><code>Ctrl+C</code></td>
<td>复制 / 全局处理</td>
<td>有文本选中时复制到剪贴板；无选中时触发全局复制（复制标签页全部内容）或交由焦点控件处理</td>
</tr>
<tr>
<td><code>Ctrl+V</code></td>
<td>粘贴</td>
<td>粘贴剪贴板内容到当前焦点控件</td>
</tr>
<tr>
<td><code>Ctrl+X</code></td>
<td>剪切</td>
<td>剪切当前焦点控件的选中文本</td>
</tr>
<tr>
<td><code>Ctrl+Z</code></td>
<td>撤销</td>
<td>对当前焦点 QTextEdit 控件执行撤销操作</td>
</tr>
<tr>
<td><code>Ctrl+Y</code></td>
<td>重做</td>
<td>对当前焦点 QTextEdit 控件执行重做操作</td>
</tr>
<tr>
<td><code>Ctrl+L</code></td>
<td>清除终端屏幕</td>
<td>清除当前终端标签页的所有显示内容</td>
</tr>
</tbody>
</table>
<h3>配置文件</h3>
<p>您可以通过程序界面进行大部分配置，也可以手工修改配置文件。</p>
<p>配置文件默认路径为 <code>config.json</code>（位于程序根目录，首次运行自动生成），支持 JSON 格式及注释：</p>
<pre><code class="language-json">// PsLauncher 程序配置文件
{
    &quot;folders&quot;: [  // 扫描脚本的文件夹路径列表
        &quot;E:/project_file/limitless/PsLauncher/test_script&quot;
    ],
    &quot;font_scale&quot;: 1.5,  // 字体大小缩放因子 (例如: 1.5 = 150%)
    &quot;dark_mode&quot;: true,  // 启用深色模式主题
    &quot;height_value&quot;: 1080,  // 窗口高度 (像素)
    &quot;width_value&quot;: 1920,  // 窗口宽度 (像素)
    &quot;font_family&quot;: &quot;Consolas&quot;,  // 编辑器和终端的字体族
    &quot;line_wrap_mode&quot;: false,  // 启用自动换行
    &quot;supported_extensions&quot;: [  // 在脚本树中显示的文件扩展名
        &quot;.ps1&quot;,
        &quot;.bat&quot;,
        &quot;.sh&quot;,
        &quot;.json&quot;,
        &quot;.yaml&quot;
    ],
    &quot;runnable_extensions&quot;: [  // 可以被执行的文件扩展名
        &quot;.ps1&quot;,
        &quot;.bat&quot;,
        &quot;.sh&quot;
    ],
    &quot;syntax_highlight_mode&quot;: &quot;auto&quot;,  // 语法高亮模式: auto (自动), ps1, bash, command, none
    &quot;auto_run_scripts&quot;: [],  // 启动时自动运行的脚本路径列表
    &quot;auto_minimize_to_tray&quot;: false,  // 启动时自动最小化到系统托盘
    &quot;language&quot;: &quot;zh_CN&quot;,  // UI 语言代码 (例如: en, zh_CN)
    &quot;api&quot;: {  // HTTP API 服务器配置
        &quot;enabled&quot;: true,  // 是否启用 HTTP API 服务器
        &quot;bind_ip&quot;: &quot;127.0.0.1&quot;,  // 绑定 API 服务器的 IP 地址 (127.0.0.1 = 仅本机)
        &quot;bind_port&quot;: 13025,  // API 服务器的端口号
        &quot;auth_token&quot;: &quot;&quot;  // API 认证的 Bearer 令牌 (留空 = 无需认证)
    }
}
</code></pre>
<h3>使用流程示例</h3>
<h4>初始设置</h4>
<ol>
<li>启动程序</li>
<li>点击 <code>文件</code>→<code>添加文件夹路径</code> 或按 <code>F2</code></li>
<li>选择包含脚本的文件夹（如llama.cpp目录）</li>
<li>程序自动扫描该文件夹下的脚本文件</li>
</ol>
<h4>查看和编辑脚本</h4>
<ol>
<li>在左侧文件列表中单击脚本文件</li>
<li>右侧打开源码标签页显示代码</li>
<li>如需修改，点击 <code>✏️快速编辑</code> 按钮进入编辑模式</li>
<li>修改后点击 <code>💾保存</code> 保存更改</li>
</ol>
<h4>运行脚本</h4>
<ol>
<li>在左侧文件列表中单击脚本文件</li>
<li>点击工具栏 <code>▶️运行</code> 按钮或按 <code>F5</code></li>
<li>右侧打开终端标签页运行脚本</li>
<li>查看实时输出，可进行交互式输入</li>
<li>如需强制停止，点击 <code>⏹️终止</code> 按钮或按 <code>F6</code>（进程树强杀）；如需优雅中断，点击 <code>❌中断</code> 按钮或按 <code>F7</code>（发送 <code>Ctrl+C</code> 信号）</li>
</ol>
<h4>多任务管理</h4>
<ol>
<li>可同时打开多个脚本查看源码</li>
<li>可同时运行多个脚本在不同标签页</li>
<li>使用鼠标滚轮滚动标签栏切换标签页</li>
<li>使用标签管理功能批量关闭标签页</li>
</ol>
<h4>后台运行</h4>
<ol>
<li>点击工具栏 <code>📌隐藏</code> 按钮或按 <code>F10</code></li>
<li>程序窗口隐藏到系统托盘</li>
<li>脚本继续在后台运行</li>
<li>单击托盘图标随时恢复窗口</li>
</ol>
<h3>命令行参数说明</h3>
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
  --headless       无头模式，不显示GUI窗口，仅通过HTTP API操作
</code></pre>
<h3>HTTP API 服务器</h3>
<p>PsLauncher 启动后默认在 <code>127.0.0.1:13025</code> 暴露 HTTP API 服务器，任何 LLM 或人类的 POST/GET 请求都可以操作 PsLauncher 的功能，相当于在 GUI 上进行操作。</p>
<h4>无头模式</h4>
<p>通过 <code>--headless</code> 参数启动 PsLauncher，将不显示 GUI 窗口，仅通过 HTTP API 提供服务：</p>
<pre><code class="language-bash">python PsLauncher.py --headless
</code></pre>
<h4>API 配置</h4>
<p>在 <code>launcher_config.json</code> 中配置 API 相关参数：</p>
<pre><code class="language-json">{
    // ...其他配置...
    &quot;api&quot;: {
        &quot;enabled&quot;: true,           // 是否启用API服务器（false可在下次启动关闭）
        &quot;bind_ip&quot;: &quot;127.0.0.1&quot;,    // 绑定IP（127.0.0.1不响应公网请求）
        &quot;bind_port&quot;: 13025,        // 绑定端口
        &quot;auth_token&quot;: &quot;&quot;           // Bearer Token（空字符串=不验权）
    }
}
</code></pre>
<h4>验权方式</h4>
<p>若配置了 <code>auth_token</code>，所有请求需携带 Authorization 头：</p>
<pre><code class="language-text">Authorization: Bearer &lt;your-token&gt;
</code></pre>
<p>token 不正确时返回 <code>401 Unauthorized</code>。</p>
<p><strong>美化输出</strong>：所有端点都支持 <code>?pretty=true</code> 查询参数，返回格式化的 JSON（带缩进和换行），方便人类阅读。不带 <code>pretty</code> 参数时默认返回紧凑格式，同时回车等字符使用斜杠表示，便于程序解析。</p>
<h4>API 端点列表</h4>
<p>所有端点支持 POST 请求，大部分查询类端点同时支持 GET。</p>
<table>
<thead>
<tr>
<th>端点</th>
<th>说明</th>
<th>请求体/参数</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>GET/POST /status</code></td>
<td>查看状态</td>
<td>无参数</td>
</tr>
<tr>
<td><code>GET /help</code></td>
<td>查看帮助信息（HTML格式）</td>
<td>无参数</td>
</tr>
<tr>
<td><code>POST /help</code></td>
<td>获取所有可用 API 端点格式列表（请求体结构参考）</td>
<td>无参数</td>
</tr>
<tr>
<td><code>GET/POST /folders</code></td>
<td>枚举文件夹路径列表</td>
<td>无参数</td>
</tr>
<tr>
<td><code>GET/POST /scripts</code></td>
<td>枚举脚本列表</td>
<td><code>?folder=&lt;路径&gt;</code>（可选）</td>
</tr>
<tr>
<td><code>POST /folder/add</code></td>
<td>增加路径</td>
<td><code>{"path":"C:/scripts"}</code></td>
</tr>
<tr>
<td><code>POST /folder/remove</code></td>
<td>移除路径</td>
<td><code>{"path":"C:/scripts"}</code></td>
</tr>
<tr>
<td><code>POST /script/run</code></td>
<td>运行脚本</td>
<td><code>{"folder":"C:/scripts","script":"test0.ps1"}</code></td>
</tr>
<tr>
<td><code>GET/POST /terminals</code></td>
<td>枚举终端界面（含ID）</td>
<td>无参数</td>
</tr>
<tr>
<td><code>POST /terminal/stop</code></td>
<td>终止终端</td>
<td><code>{"id":0}</code> 或 <code>{"name":"test0.ps1"}</code></td>
</tr>
<tr>
<td><code>POST /terminal/stop_all</code></td>
<td>终止所有终端</td>
<td>无需参数</td>
</tr>
<tr>
<td><code>GET/POST /terminal/output</code></td>
<td>查看终端输出</td>
<td><code>?id=0</code> 或 <code>?name=test0.ps1</code></td>
</tr>
<tr>
<td><code>POST /terminal/clear</code></td>
<td>清空终端输出</td>
<td><code>{"id":0}</code></td>
</tr>
<tr>
<td><code>POST /terminal/input</code></td>
<td>向终端发送字符串</td>
<td><code>{"id":0,"text":"hello\n"}</code></td>
</tr>
<tr>
<td><code>GET/POST /shutdown</code></td>
<td>关闭 PsLauncher</td>
<td>无参数</td>
</tr>
</tbody>
</table>
<h4>使用示例（完整演示流程）</h4>
<p>所有示例假设您已启动 PsLauncher，并将以下 <code>E:\\project_file\\limitless\\PsLauncher\\test_script</code> 替换为您的 <code>test_script</code> 文件夹的<strong>绝对路径</strong>。</p>
<p>当前仓库自带几个测试用的脚本, 可以直接使用. (可能需要下载源代码, 而非release版本, 因为release不包含任何测试脚本)</p>
<blockquote>
<p><strong>PowerShell 注意</strong>：PowerShell 解析参数的方式与 CMD 不同，推荐使用 <code>--%</code>（停止解析符号）。以下示例均采用 <code>--%</code> 写法，并用 <code>\</code> 表示路径分隔符和转义。下面的例子基于PowerShell语法规则，在Windows11上执行通过测试。</p>
</blockquote>
<ul>
<li>检查服务状态</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/status
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;status&quot;: &quot;ok&quot;, &quot;version&quot;: &quot;v2.0.1&quot;, &quot;app&quot;: &quot;PsLauncher&quot;}
</code></pre>
<ul>
<li>获取所有可用 API 端点格式列表(美观格式化)</li>
</ul>
<pre><code class="language-powershell">curl.exe -X POST http://127.0.0.1:13025/help?pretty=true
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{
  &quot;success&quot;: true,
  &quot;endpoints&quot;: [
    {
      &quot;method&quot;: &quot;GET&quot;,
      &quot;path&quot;: &quot;/status&quot;,
      &quot;description&quot;: &quot;检查服务器状态&quot;,
      &quot;params&quot;: null,
      &quot;body&quot;: null,
      &quot;response&quot;: {
        &quot;status&quot;: &quot;ok&quot;,
        &quot;version&quot;: &quot;x.x.x&quot;,
        &quot;app&quot;: &quot;PsLauncher&quot;
      }
    },
    ..... // 省略多行
  ]
}
</code></pre>
<ul>
<li>添加 test_script 文件夹到扫描列表</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/folder/add -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;path\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;已添加文件夹: E:\\project_file\\limitless\\PsLauncher\\test_script&quot;}
</code></pre>
<ul>
<li>列出所有可运行脚本</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/scripts
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;scripts&quot;: [{&quot;folder&quot;: &quot;E:/project_file/limitless/PsLauncher/test_script&quot;, &quot;name&quot;: &quot;test0.ps1&quot;, ...}....}
</code></pre>
<ul>
<li>运行 test0.ps1（基础输出 + 显示工作目录）</li>
</ul>
<blockquote>
<p>test0.ps1 内容：输出三行文本，然后显示当前工作路径</p>
</blockquote>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/script/run -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;folder\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;,\&quot;script\&quot;:\&quot;test0.ps1\&quot;}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;terminal_id&quot;: 0, &quot;message&quot;: &quot;已启动脚本: test0.ps1&quot;}
</code></pre>
<p>同时PsLauncher GUI启动对应脚本</p>
<ul>
<li>查看终端列表（记录终端 ID）</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/terminals
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;terminals&quot;: [{&quot;id&quot;: 0, &quot;name&quot;: &quot;test0.ps1&quot;, &quot;script&quot;: &quot;E:\\project_file\\limitless\\PsLauncher\\test_script\\test0.ps1&quot;, &quot;running&quot;: false}]}
</code></pre>
<ul>
<li>查看终端输出（id=0 是上一步运行的 test0.ps1）</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/terminal/output?id=0&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;id&quot;: 0, &quot;name&quot;: &quot;test0.ps1&quot;, &quot;output&quot;: &quot;[PsLauncher 2026-06-30 21:40:20] start: E:\\project_file\\limitless\\PsLauncher\\test_script\\test0.ps1\ntest0-1\ntest0-2\ntest0-3\nCurrent work path: E:\\project_file\\limitless\\PsLauncher\\test_script\n\n[PsLauncher 2026-06-30 21:40:20] Process terminated.\n&quot;}
</code></pre>
<ul>
<li>运行 test2.ps1（交互式输入演示）</li>
</ul>
<blockquote>
<p>test2.ps1 内容：输出三行后通过 Read-Host 等待键盘输入</p>
</blockquote>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/script/run -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;folder\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;,\&quot;script\&quot;:\&quot;test2.ps1\&quot;}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;terminal_id&quot;: 1, &quot;message&quot;: &quot;已启动脚本: test2.ps1&quot;}
</code></pre>
<ul>
<li>查看新终端列表（此时应有 id=0 和 id=1 两个终端）</li>
</ul>
<pre><code class="language-powershell">curl.exe http://127.0.0.1:13025/terminals
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;terminals&quot;: [{&quot;id&quot;: 0, &quot;name&quot;: &quot;test0.ps1&quot;, &quot;script&quot;: &quot;E:\\project_file\\limitless\\PsLauncher\\test_script\\test0.ps1&quot;, &quot;running&quot;: false}, {&quot;id&quot;: 1, &quot;name&quot;: &quot;test2.ps1&quot;, &quot;script&quot;: &quot;E:\\project_file\\limitless\\PsLauncher\\test_script\\test2.ps1&quot;, &quot;running&quot;: true}]}
</code></pre>
<ul>
<li>向 id=1（test2.ps1）发送输入</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/input -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;id\&quot;:1,\&quot;text\&quot;:\&quot;Hello PsLauncher\&quot;}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;已向终端 ID=1 发送输入&quot;}
</code></pre>
<ul>
<li>查看 test2.ps1 的输出（应包含刚输入的内容）</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/terminal/output?id=1&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;id&quot;: 1, &quot;name&quot;: &quot;test2.ps1&quot;, &quot;output&quot;: &quot;[PsLauncher 2026-06-30 21:41:29] start: E:\\project_file\\limitless\\PsLauncher\\test_script\\test2.ps1\ntest2-1\ntest2-2\ntest2-3\nHello PsLauncher\nYou entered: Hello PsLauncher\n\n[PsLauncher 2026-06-30 21:41:44] Process terminated.\n&quot;}
</code></pre>
<ul>
<li>运行 test3.bat（批处理脚本演示）</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/script/run -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;folder\&quot;:\&quot;E:\\project_file\\limitless\\PsLauncher\\test_script\&quot;,\&quot;script\&quot;:\&quot;test3.bat\&quot;}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;terminal_id&quot;: 2, &quot;message&quot;: &quot;已启动脚本: test3.bat&quot;}
</code></pre>
<ul>
<li>查看 test3.bat 的输出</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/terminal/output?id=2&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;id&quot;: 2, &quot;name&quot;: &quot;test3.bat&quot;, &quot;output&quot;: &quot;[PsLauncher 2026-06-30 21:41:55] start: E:\\project_file\\limitless\\PsLauncher\\test_script\\test3.bat\nbat test3-1\nbat test3-2\nbat test3-3\n\n[PsLauncher 2026-06-30 21:41:55] Process terminated.\n&quot;}
</code></pre>
<ul>
<li>清空 test3.bat 的终端输出</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/clear -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;id\&quot;:2}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;已清空终端 ID=2 的输出&quot;}
</code></pre>
<ul>
<li>终止 id=1（test2.ps1）的终端进程</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/stop -H &quot;Content-Type: application/json&quot; -d &quot;{\&quot;id\&quot;:1}&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;已终止终端 ID=1&quot;}
</code></pre>
<ul>
<li>终止所有终端进程</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/terminal/stop_all
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;已终止 2 个终端&quot;}
</code></pre>
<ul>
<li>关闭 PsLauncher</li>
</ul>
<pre><code class="language-powershell">curl.exe --% -X POST http://127.0.0.1:13025/shutdown
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;success&quot;: true, &quot;message&quot;: &quot;PsLauncher 正在关闭...&quot;}
</code></pre>
<blockquote>
<p>同时，PsLauncher结束并退出。</p>
</blockquote>
<h3>TCP事件服务器</h3>
<p>PsLauncher 启动后默认在 <code>127.0.0.1:13026</code> 暴露 TCP 长连接事件服务器，用于将程序内部的状态变更实时推送给已连接的客户端。</p>
<blockquote>
<p><strong>适用场景</strong>：实时监控脚本状态变化、终端输出流、脚本列表/路径变更等，免去轮询 HTTP API 的开销。例如一个自动化运维监控系统或 LLM Agent 可以通过一条长连接实时感知终端输出的提示信息和状态变化，从而做出同步响应。</p>
</blockquote>
<h4>TCP 事件服务器配置</h4>
<p>在 <code>launcher_config.json</code> 中配置：</p>
<pre><code class="language-json">{
    &quot;tcp_event_server&quot;: {
        &quot;enabled&quot;: true,            // 是否启用 TCP 事件服务器（默认启用）
        &quot;bind_ip&quot;: &quot;127.0.0.1&quot;,     // 绑定 IP（127.0.0.1 不响应公网请求）
        &quot;bind_port&quot;: 13026          // 绑定端口
    }
}
</code></pre>
<h4>协议说明</h4>
<ul>
<li><strong>传输层</strong>：纯 TCP，使用新行分隔的 JSON（每个 JSON 对象占一行，以 <code>\n</code> 结尾）</li>
<li><strong>编码</strong>：UTF-8</li>
<li><strong>客户端订阅</strong>（可选）：客户端连接后可以发送订阅消息来只接收特定类型的事件</li>
</ul>
<h5>客户端订阅消息格式</h5>
<p>客户端连接成功后，发送一条 JSON：</p>
<pre><code class="language-json">{&quot;subscribe&quot;: [&quot;path_changed&quot;, &quot;terminal_status&quot;]}
</code></pre>
<ul>
<li>不发送订阅消息 = 接收所有事件</li>
<li><code>{"subscribe": ["*"]}</code> = 重置为所有事件</li>
<li><code>{"subscribe": []}</code> = 取消所有订阅</li>
<li><code>{"subscribe": ["path_changed", "terminal_output"]}</code> = 只接收路径变化和终端输出事件</li>
</ul>
<h5>服务器事件推送格式</h5>
<pre><code class="language-json">{
    &quot;event&quot;: &quot;path_changed&quot;,
    &quot;timestamp&quot;: &quot;2026-06-30 22:00:00&quot;,
    &quot;data&quot;: { ... }
}
</code></pre>
<h4>事件类型一览</h4>
<table>
<thead>
<tr>
<th>事件类型</th>
<th>触发时机</th>
<th>data 字段</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>path_changed</code></td>
<td>添加或移除文件夹路径</td>
<td><code>{"folders": ["path1", "path2", ...]}</code></td>
</tr>
<tr>
<td><code>script_changed</code></td>
<td>新建/重命名/复制/移动/删除脚本</td>
<td><code>{"folder": "C:/scripts", "scripts": [{"name": "file.ps1", "path": "..."}]}</code></td>
</tr>
<tr>
<td><code>terminal_output</code></td>
<td>终端有新的 stdout/stderr 输出</td>
<td><code>{"terminal_id": 0, "script": "C:/scripts/test.ps1", "text": "Hello World\n"}</code></td>
</tr>
<tr>
<td><code>terminal_status</code></td>
<td>终端进程状态变化</td>
<td><code>{"terminal_id": 0, "script": "C:/scripts/test.ps1", "status": "started\|finished\|stopped\|closed"}</code></td>
</tr>
</tbody>
</table>
<p><code>terminal_status</code> 的状态值说明：</p>
<ul>
<li><code>started</code>：脚本进程已启动</li>
<li><code>finished</code>：脚本进程正常结束</li>
<li><code>stopped</code>：脚本进程被强制终止</li>
<li><code>closed</code>：终端标签页被关闭（进程已不再运行）</li>
</ul>
<h4>使用监听脚本</h4>
<p>项目提供了 <code>test_event_listener.py</code> 监听脚本，用于快速测试并理解功能，可直接运行以观察实时事件：</p>
<pre><code class="language-bash"># 监听所有事件
python test_event_listener.py

# 只监听路径变化和终端状态变化
python test_event_listener.py --subscribe path_changed terminal_status

# 指定地址和端口
python test_event_listener.py --host 127.0.0.1 --port 13026
</code></pre>
<p>示例输出：</p>
<pre><code>PsLauncher TCP 事件监听器
连接至: 127.0.0.1:13026
订阅事件: 所有
等待接收事件... (按 Ctrl+C 退出)
------------------------------------------------------------

[2026-06-30 22:05:00] 事件类型: terminal_status
  终端 ID: 0
  脚本: C:/scripts/test0.ps1
  状态: 🚀 已启动

[2026-06-30 22:05:01] 事件类型: terminal_output
  终端 ID: 0
  脚本: C:/scripts/test0.ps1
  输出: Hello World

[2026-06-30 22:05:02] 事件类型: path_changed
  文件夹列表 (共 1 个):
    - C:/my_scripts

[2026-06-30 22:05:05] 事件类型: terminal_status
  终端 ID: 0
  脚本: C:/scripts/test0.ps1
  状态: ✅ 已正常结束
</code></pre>
<h4>使用 telnet / nc 等工具手动测试</h4>
<pre><code class="language-bash"># 使用 telnet（需要 Windows 开启 telnet 客户端）
telnet 127.0.0.1 13026

# 使用 ncat（推荐，可从 nmap 获取）
ncat 127.0.0.1 13026

# 使用 PowerShell
$client = New-Object System.Net.Sockets.TcpClient('127.0.0.1', 13026)
$stream = $client.GetStream()
$reader = New-Object System.IO.StreamReader($stream)
while (($line = $reader.ReadLine()) -ne $null) { Write-Host $line }
</code></pre>
<p>连接后终端将不断显示推送的事件 JSON 行。</p>
<h3>使用美化输出（人类可读）</h3>
<p>加上<code>?pretty=true</code>参数后，将会变得易于人类阅读。</p>
<ul>
<li>加上<code>?pretty=true</code>参数：</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/status?pretty=true&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{
  &quot;status&quot;: &quot;ok&quot;,
  &quot;version&quot;: &quot;v2.0.1&quot;,
  &quot;app&quot;: &quot;PsLauncher&quot;
}
</code></pre>
<ul>
<li>不加<code>?pretty=true</code>参数：</li>
</ul>
<pre><code class="language-powershell">curl.exe &quot;http://127.0.0.1:13025/status&quot;
</code></pre>
<p>预期输出：</p>
<pre><code class="language-jsonc">{&quot;status&quot;: &quot;ok&quot;, &quot;version&quot;: &quot;v2.0.1&quot;, &quot;app&quot;: &quot;PsLauncher&quot;}
</code></pre>
<h3>注意事项</h3>
<ul>
<li>如果需要源码执行, 请确保系统已安装 Python 3.x 和 Qt5/Qt6.</li>
<li>一些情况下, 程序可能运行时需要管理员权限（视脚本内容而定）.</li>
<li>(目前已知问题): 一些情况下终端字符着色似乎是错的</li>
<li>(目前已知问题): 编辑时编辑器背景颜色应该会变以提示用户, 但是现在有时候会完全没有这个视觉效果.</li>
</ul>
<h3>常见问题解答</h3>
<p><strong>Q: 如何复制终端输出内容？</strong>
A: 使用工具栏的 <code>📋复制</code> 按钮复制选中文本（或直接按 <code>Ctrl+C</code>），或使用 <code>📄复制全部</code> 复制整个标签页内容。现在 <code>Ctrl+C</code> 已由全局事件过滤器处理，有选中文本时复制，无选中时复制标签页全部内容。</p>
<p><strong>Q: 编辑模式保存失败怎么办？</strong>
A: 可能是文件权限问题，请尝试以管理员权限运行程序，或检查文件是否被其他程序占用。</p>
<p><strong>Q: 如何调整界面字体大小？</strong>
A: 通过命令行参数 <code>--scale</code> 启动程序，或在配置文件中修改 <code>font_scale</code> 值。</p>
<p><strong>Q: 脚本运行后没有输出怎么办？</strong>
A: 检查脚本是否需要交互式输入，终端支持交互式操作，尝试在输入区域键入命令后按 <code>Enter键</code>。</p>
<p><strong>Q: 如何彻底删除脚本文件？</strong>
A: 使用 <code>脚本管理</code>→<code>删除脚本</code> 功能，注意此操作直接删除文件，不经过回收站。</p>
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
<li>运行自动测试：<code>python -m pytest test/ -q --tb=long -p no:warnings</code> 确保没问题</li>
<li>执行<code>python check_i18n_coverage.py</code>确认 i18n 覆盖率.</li>
<li>执行<code>python get_help_page.py</code>编译多语言帮助页面（读取 <code>README.md</code> 生成英文、<code>README_CN.md</code> 生成中文等）</li>
<li>如果ico更新了,执行<code>python get_ico.py</code>编译一遍ico</li>
<li>执行<code>pyinstaller -w ./PsLauncher.py -i ./logo.ico -y --distpath ./exe  --paths ./</code>编译文件</li>
<li>如果有必要, 将帮助文档也放一份.</li>
<li>运行<code>get_zip_release.ps1</code>打包.</li>
</ol>
<p>正确的发布版本结构:</p>
<pre><code class="language-PowerShell">exe/
   PsLauncher.exe
   _internal/*    # 必要的动态链接库
</code></pre>
<h3>多语言支持</h3>
<p>本程序使用了一个自制的i18n模组实现多国语言兼容。可以查看<code>i18n</code>文件夹下的代码，来了解其原理。这十分的简单。</p>
<p>HTTP API 服务器同样支持 i18n：<code>POST /help</code> 中的所有端点描述、错误消息和操作响应消息，以及所有 API 端点返回的错误消息，都会根据配置的 <code>language</code> 设置自动切换语言。</p>
<h3>自动化测试</h3>
<p>项目已搭建完整的自动化测试体系，基于 <code>pytest</code> + <code>pytest-qt</code> + <code>pytest-xdist</code>，支持 headless 并行执行。</p>
<h4>测试目录结构</h4>
<pre><code class="language-text">test/
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
├── test_tcp_event.py        # 功能层：TCP 事件服务器协议与格式测试
└── fixtures/
    ├── __init__.py
    ├── config_factory.py    # 构造不同 config.json 场景
    └── temp_scripts.py      # 临时脚本目录
</code></pre>
<h4>三层测试分层说明</h4>
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
<h4>执行命令</h4>
<p><strong>精简版</strong>（CI 与本地统一使用）：</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=short -p no:warnings --no-header
</code></pre>
<p><strong>详细版</strong>（本地调试用）：</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=long -p no:warnings
</code></pre>
<p><strong>仅运行非 GUI 测试</strong>（快速回归）：</p>
<pre><code class="language-bash">python -m pytest test/ -q --tb=short -p no:warnings --no-header -m &quot;not gui&quot;
</code></pre>
<p>参数说明：</p>
<ul>
<li><code>-q</code>/<code>--no-header</code>：精简输出，节省 token。如果你是人类那么可能<code>-v</code>更合适。</li>
<li><code>--tb=short</code>：简短回溯，避免大量堆栈</li>
<li><code>-p no:warnings</code>：屏蔽 Python 警告</li>
<li><code>-n auto</code>：启用 pytest-xdist 按 CPU 核心数并行分发</li>
<li><code>-m "not gui"</code>：跳过 GUI 标记用例</li>
</ul>
<h4>Headless 环境要求</h4>
<p>pytest-qt 在无显示环境（CI/服务器）下运行需设置：</p>
<pre><code class="language-bash">export QT_QPA_PLATFORM=offscreen   # Linux/macOS
set QT_QPA_PLATFORM=offscreen      # Windows CMD
$env:QT_QPA_PLATFORM=&quot;offscreen&quot;   # Windows PowerShell
</code></pre>
<p>已在 <code>conftest.py</code> 顶部自动设置。如需指定 Qt API 绑定：</p>
<pre><code class="language-bash">export PYTEST_QT_API=pyqt5
</code></pre>
<h4>AI Agent 注意事项</h4>
<ul>
<li>AI 完成测试代码后只需 <code>py_compile</code> 校验，或者pytest测试流程，<strong>AI不得自行执行 GUI 用例</strong>（会导致agent loop阻塞）。任何GUI only的测试应告诉并令人类协助测试确认。</li>
<li>禁止读取 <code>source_ico.py</code>等<code>source</code>开头的文件，这些文件是通过编译器自动生成的，很大。</li>
<li>GUI 用例在 offscreen 下覆盖有限，托盘/拖动等需人工复核。</li>
<li>开发完成后必须 <code>python -m pytest test/ -q --tb=long -p no:warnings</code> 自动测试执行一遍确认没有问题.</li>
<li>开发完成后，如有必要，请修改readme以及添加自动测试用例，以覆盖新功能</li>
</ul>
<h4>人类开发者须知（测试清单）</h4>
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
