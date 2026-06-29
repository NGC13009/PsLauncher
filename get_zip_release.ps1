# coding = utf-8
# Arch   = manyArch
#
# @File name:       get_zip_release.ps1
# @brief:           将pyinstaller编译好的可执行文件打包为zip等
# @attention:       None
# @Author:          NGC13009
# @History:         2026-06-29		Create

# 定义 7-Zip 的路径
$7zPath = "${env:ProgramFiles}\7-Zip\7z.exe"

# 删除旧的打包文件
Remove-Item -Path ".\exe\PsLauncher.zip" -ErrorAction SilentlyContinue
Remove-Item -Path ".\exe\Setup_PsLauncher.exe" -ErrorAction SilentlyContinue

# 1. 打包为 .zip 格式
& $7zPath a -tzip ".\exe\PsLauncher.zip" ".\exe\PsLauncher\*"

# 2. 打包为自解压 .exe 格式 (SFX)
& $7zPath a -sfx ".\exe\Setup_PsLauncher.exe" ".\exe\PsLauncher\*"
