param(
    [Parameter(Mandatory=$true)]
    [string]$Text
)

try {
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.Rate = 1
    $synth.Speak($Text)
} catch {
    # Fallback to SAPI.SpVoice
    try {
        $voice = New-Object -ComObject SAPI.SpVoice
        $voice.Speak($Text)
    } catch {
        # Silently exit if audio device is busy
    }
}
