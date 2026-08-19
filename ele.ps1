#!/usr/bin/env pwsh
# ELE Agent — PowerShell launcher
param([Parameter(ValueFromRemainingArguments)][string[]]$Args)
python "$PSScriptRoot\ele.py" @Args