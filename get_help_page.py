# coding = utf-8
# Arch   = manyArch
#
# @File name:       get_help_page.py
# @brief:           自动将readme编译成程序内需要的内容（支持多语言）
# @attention:       None
# @Author:          NGC13009
# @History:         2026-03-17		Create
#                   2026-06-29      支持多语言生成

import markdown

# 配置文件：(readme文件, 输出的py文件)
LANGUAGES = [
    ("README.md", "i18n/source_help_page.py"),
    ("README_CN.md", "i18n/source_help_page_zh_CN.py"),
]

for md_file, out_file in LANGUAGES:
    # 1. 准备 Markdown 文本
    with open(md_file, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # 2. 将 Markdown 编译为 HTML
    html_text = markdown.markdown(md_text, extensions=['extra'])

    # 3. 转义可能引发语法问题的三个单引号
    safe_html_text = html_text.replace("'''", "\\'\\'\\'")

    # 4. 构造 Python 代码字符串
    python_code = f"html_content = '''\\\n{safe_html_text}'''\n"
    comments = f'''# coding = utf-8
# Arch   = manyArch
#
# @File name:       {out_file}
# @brief:           帮助页面文本
# @attention:       None
# @Author:          get_help_page.py 脚本自动生成, 请勿直接编辑该文件
# @History:         2026-06-29		Create

'''

    # 5. 写入目标文件
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(comments + python_code)

    print(f"✅ 转换完成！已成功生成 {out_file} 文件。")
