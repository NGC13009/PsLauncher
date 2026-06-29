# 定义 7-Zip 的路径
$7zPath = "${env:ProgramFiles}\7-Zip\7z.exe"

# 1. 打包为 .zip 格式
& $7zPath a -tzip ".\exe\PsLauncher.zip" ".\exe\PsLauncher\*"

# 2. 打包为自解压 .exe 格式 (SFX)
& $7zPath a -sfx ".\exe\Setup_PsLauncher.exe" ".\exe\PsLauncher\*"
