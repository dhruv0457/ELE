#!/usr/bin/env pwsh
# ELE Agent - Single Command Launcher
param([Parameter(ValueFromRemainingArguments)][string[]]$Args)
python "$PSScriptRoot\ele.py" @Args