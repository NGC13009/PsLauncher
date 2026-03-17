# coding = utf-8
# Arch   = manyArch
#
# @File name:       get_help_page.py
# @brief:           自动将readme编译成程序内需要的内容
# @attention:       None
# @Author:          NGC13009
# @History:         2026-03-17		Create

import markdown

# 1. 准备你的 Markdown 文本
with open('readme.md', 'r', encoding='utf-8') as f:
    md_text = f.read()

# 2. 将 Markdown 编译为 HTML
# extensions参数可以添加额外的解析功能，如表格(tables)、代码高亮(fenced_code)等
html_text = markdown.markdown(md_text, extensions=['extra'])

# 3. 构造要写入的 Python 代码字符串
# 为了防止 HTML 文本中碰巧包含三个单引号（'''）导致生成的Python语法错误，
# 我们做一个简单的替换转义（防御性编程）
safe_html_text = html_text.replace("'''", "\\'\\'\\'")

# 按照要求，将 HTML 文本包裹在 html_content = '''...''' 中
# 开头的 '''\n 中的反斜杠是为了让生成的 HTML 代码不要在第一行产生多余的空行
python_code = f"html_content = '''\\\n{safe_html_text}'''\n"

# 4. 将拼接好的代码写入到目标文件 source_help_page.py
with open('source_help_page.py', 'w', encoding='utf-8') as f:
    f.write(python_code)

print("✅ 转换完成！已成功生成 source_help_page.py 文件。")
