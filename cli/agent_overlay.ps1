# ═══════════════════════════════════════════════════════════════
#  ELE AGENT — REAL-TIME VISUAL SCREEN OVERLAY & GHOST CURSOR
#  Gemini / Anthropic Computer Use HUD • Glowing Ripple • Watermark
# ═══════════════════════════════════════════════════════════════
param(
    [string]$Action = "launch_app", # "launch_app", "glide_click", "banner", "ripple"
    [string]$AppName = "office",
    [string]$AppTitle = "Microsoft Office",
    [string]$Message = "Controlling PC: Automating Task...",
    [int]$TargetX = 640,
    [int]$TargetY = 360,
    [int]$DurationMs = 2000
)

Add-Type -AssemblyName PresentationFramework, PresentationCore, WindowsBase, System.Windows.Forms, System.Drawing

[System.Windows.Forms.Application]::EnableVisualStyles()
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$screenWidth = $screen.Width
$screenHeight = $screen.Height

# Function to smoothly move cursor
function Move-CursorSmooth([int]$dstX, [int]$dstY, [int]$steps = 20, [int]$delayMs = 10) {
    $cur = [System.Windows.Forms.Cursor]::Position
    $sx = $cur.X
    $sy = $cur.Y
    for ($i = 1; $i -le $steps; $i++) {
        $t = $i / $steps
        $e = (1 - [Math]::Cos($t * [Math]::PI)) / 2.0
        $nx = [int]($sx + ($dstX - $sx) * $e)
        $ny = [int]($sy + ($dstY - $sy) * $e)
        [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($nx, $ny)
        Start-Sleep -Milliseconds $delayMs
    }
}

if ($Action -eq "banner" -or $Action -eq "launch_app" -or $Action -eq "ripple" -or $Action -eq "glide_click") {
    $capsuleLeft = [int]($screenWidth / 2 - 280)
    $xaml = @"
<Window xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="ELE_Agent_HUD" WindowStyle="None" AllowsTransparency="True" Background="Transparent"
        Topmost="True" ShowInTaskbar="False" WindowStartupLocation="Manual"
        Left="0" Top="0" Width="$screenWidth" Height="$screenHeight">
    <Canvas Name="MainCanvas" Background="Transparent">
        <!-- Top Center Floating Agent Capsule -->
        <Border Name="HudCapsule" Canvas.Left="$capsuleLeft" Canvas.Top="24" Width="560" Height="62" CornerRadius="31"
                Background="#EE0A0E17" BorderBrush="#00FFE0" BorderThickness="2" Opacity="0">
            <Border.Effect>
                <DropShadowEffect Color="#00FFE0" BlurRadius="25" ShadowDepth="0" Opacity="0.85"/>
            </Border.Effect>
            <Grid Margin="18,0,18,0">
                <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="42"/>
                    <ColumnDefinition Width="*"/>
                    <ColumnDefinition Width="Auto"/>
                </Grid.ColumnDefinitions>
                
                <!-- Glowing Agent Avatar / Orb -->
                <Ellipse Grid.Column="0" Width="32" Height="32" VerticalAlignment="Center">
                    <Ellipse.Fill>
                        <RadialGradientBrush>
                            <GradientStop Color="#00FFE0" Offset="0.0"/>
                            <GradientStop Color="#A855F7" Offset="0.7"/>
                            <GradientStop Color="#0F172A" Offset="1.0"/>
                        </RadialGradientBrush>
                    </Ellipse.Fill>
                    <Ellipse.Effect>
                        <DropShadowEffect Color="#00FFE0" BlurRadius="12" ShadowDepth="0" Opacity="0.9"/>
                    </Ellipse.Effect>
                </Ellipse>
                <TextBlock Grid.Column="0" Text="⚡" FontSize="16" FontWeight="Bold" Foreground="#FFFFFF"
                           HorizontalAlignment="Center" VerticalAlignment="Center"/>

                <!-- Live Status & Target -->
                <StackPanel Grid.Column="1" VerticalAlignment="Center" Margin="10,0,0,0">
                    <StackPanel Orientation="Horizontal">
                        <TextBlock Text="ELE AI AGENT" FontSize="11" FontWeight="ExtraBold" Foreground="#00FFE0"/>
                        <TextBlock Text=" • " FontSize="11" Foreground="#64748B"/>
                        <TextBlock Name="ActionTag" Text="AUTONOMOUS CONTROL" FontSize="11" FontWeight="SemiBold" Foreground="#A855F7"/>
                    </StackPanel>
                    <TextBlock Name="StatusText" Text="$Message" FontSize="13" FontWeight="Bold" Foreground="#F8FAFC"
                               TextTrimming="CharacterEllipsis" Margin="0,2,0,0"/>
                </StackPanel>

                <!-- Status Badge -->
                <Border Grid.Column="2" CornerRadius="12" Background="#1E293B" BorderBrush="#38BDF8" BorderThickness="1"
                        Padding="10,4,10,4" VerticalAlignment="Center">
                    <TextBlock Name="StepBadge" Text="● ACTIVE" FontSize="11" FontWeight="Bold" Foreground="#38BDF8"/>
                </Border>
            </Grid>
        </Border>

        <!-- Click Ripple Circle 1 -->
        <Ellipse Name="Ripple1" Width="0" Height="0" Canvas.Left="0" Canvas.Top="0"
                 Stroke="#00FFE0" StrokeThickness="3" Opacity="0">
            <Ellipse.Effect>
                <DropShadowEffect Color="#00FFE0" BlurRadius="18" ShadowDepth="0" Opacity="0.9"/>
            </Ellipse.Effect>
        </Ellipse>

        <!-- Click Ripple Circle 2 -->
        <Ellipse Name="Ripple2" Width="0" Height="0" Canvas.Left="0" Canvas.Top="0"
                 Stroke="#A855F7" StrokeThickness="2" Opacity="0">
            <Ellipse.Effect>
                <DropShadowEffect Color="#A855F7" BlurRadius="12" ShadowDepth="0" Opacity="0.7"/>
            </Ellipse.Effect>
        </Ellipse>
    </Canvas>
</Window>
"@

    $reader = [System.Xml.XmlReader]::Create([System.IO.StringReader]::new($xaml))
    $window = [System.Windows.Markup.XamlReader]::Load($reader)

    $hudCapsule = $window.FindName("HudCapsule")
    $statusText = $window.FindName("StatusText")
    $actionTag  = $window.FindName("ActionTag")
    $stepBadge  = $window.FindName("StepBadge")
    $ripple1    = $window.FindName("Ripple1")
    $ripple2    = $window.FindName("Ripple2")

    $window.Show()

    # Animate Capsule In (Fade In)
    for ($op = 0; $op -le 10; $op++) {
        $hudCapsule.Opacity = $op / 10.0
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 10
    }

    if ($Action -eq "launch_app") {
        # STEP 1: Glide to Start Button / Taskbar
        $statusText.Text = "Step 1/3: Navigating to Start Menu for $AppTitle..."
        $stepBadge.Text = "STEP 1/3"
        [System.Windows.Forms.Application]::DoEvents()
        
        $startX = 36
        $startY = $screenHeight - 24
        Move-CursorSmooth $startX $startY 18 10

        # Trigger Click Ripple at Start Button
        for ($r = 10; $r -le 70; $r += 6) {
            $ripple1.Width = $r
            $ripple1.Height = $r
            $ripple1.Opacity = (70 - $r) / 60.0
            [System.Windows.Controls.Canvas]::SetLeft($ripple1, $startX - ($r / 2))
            [System.Windows.Controls.Canvas]::SetTop($ripple1, $startY - ($r / 2))

            $r2 = $r * 1.3
            $ripple2.Width = $r2
            $ripple2.Height = $r2
            $ripple2.Opacity = (90 - $r2) / 80.0
            [System.Windows.Controls.Canvas]::SetLeft($ripple2, $startX - ($r2 / 2))
            [System.Windows.Controls.Canvas]::SetTop($ripple2, $startY - ($r2 / 2))

            [System.Windows.Forms.Application]::DoEvents()
            Start-Sleep -Milliseconds 10
        }
        $ripple1.Opacity = 0
        $ripple2.Opacity = 0

        # STEP 2: Searching & Launching
        $statusText.Text = "Step 2/3: Launching '$AppTitle'..."
        $stepBadge.Text = "STEP 2/3"
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 350

        # STEP 3: Glide to Screen Center & Verify
        $statusText.Text = "Step 3/3: Activating Window & Focusing Workspace..."
        $stepBadge.Text = "STEP 3/3"
        $centerX = [int]($screenWidth / 2)
        $centerY = [int]($screenHeight / 2)
        Move-CursorSmooth $centerX $centerY 18 10
        
        # Center Click Ripple
        for ($r = 10; $r -le 60; $r += 6) {
            $ripple1.Width = $r
            $ripple1.Height = $r
            $ripple1.Opacity = (60 - $r) / 50.0
            [System.Windows.Controls.Canvas]::SetLeft($ripple1, $centerX - ($r / 2))
            [System.Windows.Controls.Canvas]::SetTop($ripple1, $centerY - ($r / 2))
            [System.Windows.Forms.Application]::DoEvents()
            Start-Sleep -Milliseconds 10
        }
        $ripple1.Opacity = 0

        # SUCCESS
        $statusText.Text = "✓ SUCCESS: $AppTitle is Launched & Ready!"
        $stepBadge.Text = "✓ READY"
        $hudCapsule.BorderBrush = [System.Windows.Media.Brushes]::LimeGreen
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 900
    }
    elseif ($Action -eq "glide_click") {
        $statusText.Text = "$Message"
        $stepBadge.Text = "TARGETING"
        [System.Windows.Forms.Application]::DoEvents()

        Move-CursorSmooth $TargetX $TargetY 18 10

        # Click Ripple at Target
        for ($r = 10; $r -le 70; $r += 6) {
            $ripple1.Width = $r
            $ripple1.Height = $r
            $ripple1.Opacity = (70 - $r) / 60.0
            [System.Windows.Controls.Canvas]::SetLeft($ripple1, $TargetX - ($r / 2))
            [System.Windows.Controls.Canvas]::SetTop($ripple1, $TargetY - ($r / 2))
            [System.Windows.Forms.Application]::DoEvents()
            Start-Sleep -Milliseconds 10
        }
        $ripple1.Opacity = 0
        Start-Sleep -Milliseconds 300
    }
    else {
        Start-Sleep -Milliseconds $DurationMs
    }

    # Animate Capsule Out (Fade Out)
    for ($op = 10; $op -ge 0; $op--) {
        $hudCapsule.Opacity = $op / 10.0
        [System.Windows.Forms.Application]::DoEvents()
        Start-Sleep -Milliseconds 10
    }

    $window.Close()
}
