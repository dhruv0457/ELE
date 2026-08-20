$agyScript = "D:\ELE\cli\agy.js"
if (-not (Test-Path $agyScript)) {
    $agyScript = "$env:APPDATA\npm\node_modules\ele-agent-cli\agy.js"
}
& node "$agyScript" $args
