@echo off
if exist "%~dp0cli\agy.js" (
    node "%~dp0cli\agy.js" %*
) else (
    node "C:\Users\HP\AppData\Roaming\npm\node_modules\ele-agent-cli\agy.js" %*
)
