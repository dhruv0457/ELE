# ═══════════════════════════════════════════════════════════════
#  HIGH ACCURACY CONTINUOUS MICROPHONE LISTENER FOR JARVIS
# ═══════════════════════════════════════════════════════════════
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

try {
    Add-Type -AssemblyName System.Speech

    $installed = [System.Speech.Recognition.SpeechRecognitionEngine]::InstalledRecognizers()
    if ($installed.Count -eq 0) {
        Write-Output "JARVIS_MIC_ERROR: No speech recognizers installed"
        [Console]::Out.Flush()
        exit 1
    }

    # Use first installed English or system recognizer
    $recognizerInfo = $installed[0]
    foreach ($r in $installed) {
        if ($r.Culture.Name -like "en*") {
            $recognizerInfo = $r
            break
        }
    }

    $engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine($recognizerInfo.Culture)

    # 1. Load Universal Dictation Grammar for freeform conversation
    $dictGrammar = New-Object System.Speech.Recognition.DictationGrammar
    $dictGrammar.Name = "UniversalDictation"
    $engine.LoadGrammar($dictGrammar)

    # 2. Load High-Confidence Command Choices for Autonomous Actions
    $commands = @(
        "open claude", "open cloud", "go to claude", "open claude in chrome",
        "generate christmas speech", "write christmas speech", "christmas speech",
        "generate a speech", "write a python script", "open vs code", "open vscode",
        "open chrome", "open browser", "search google", "automate",
        "switch model", "list models", "help", "clear chat", "exit", "quit",
        "what can you do", "hello jarvis", "hey jarvis", "start speech"
    )
    $choices = New-Object System.Speech.Recognition.Choices($commands)
    $gb = New-Object System.Speech.Recognition.GrammarBuilder($choices)
    $gb.Culture = $recognizerInfo.Culture
    $cmdGrammar = New-Object System.Speech.Recognition.Grammar($gb)
    $cmdGrammar.Name = "AgentCommands"
    $cmdGrammar.Priority = 1
    $engine.LoadGrammar($cmdGrammar)

    # Configure audio input
    $engine.SetInputToDefaultAudioDevice()

    Write-Output "JARVIS_MIC_ACTIVE: $($recognizerInfo.Culture.Name) - $($recognizerInfo.Description)"
    [Console]::Out.Flush()

    # Continuous Recognition Loop
    while ($true) {
        try {
            $result = $engine.Recognize([TimeSpan]::FromSeconds(4))
            if ($result -and $result.Text) {
                $trimmed = $result.Text.Trim()
                if ($trimmed.Length -gt 0 -and $result.Confidence -gt 0.20) {
                    Write-Output "VOICE_TRANSCRIBED: $trimmed"
                    [Console]::Out.Flush()
                }
            }
        } catch [System.InvalidOperationException] {
            Start-Sleep -Milliseconds 150
        } catch {
            Start-Sleep -Milliseconds 200
        }
    }
} catch {
    Write-Output "JARVIS_MIC_FALLBACK: $($_.Exception.Message)"
    [Console]::Out.Flush()
}
