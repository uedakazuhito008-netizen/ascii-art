<#
.SYNOPSIS
    ASCII Art Generator - Interactive terminal toy
    No dependencies. Requires PowerShell 5.1 + Windows Terminal.
#>

# ── Setup ─────────────────────────────────────────────────────────────────────
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding           = [System.Text.Encoding]::UTF8

$ESC = [char]27
$RST = "${ESC}[0m"

# Rainbow palette (true-color ANSI)
$RAINBOW = @(
    "${ESC}[38;2;255;80;80m",
    "${ESC}[38;2;255;180;0m",
    "${ESC}[38;2;230;230;50m",
    "${ESC}[38;2;50;230;50m",
    "${ESC}[38;2;60;160;255m",
    "${ESC}[38;2;200;60;255m"
)

function Get-Color {
    param([string]$name)
    switch ($name) {
        'red'     { return "${ESC}[91m" }
        'green'   { return "${ESC}[92m" }
        'yellow'  { return "${ESC}[93m" }
        'blue'    { return "${ESC}[94m" }
        'magenta' { return "${ESC}[95m" }
        'cyan'    { return "${ESC}[96m" }
        'white'   { return "${ESC}[97m" }
        default   { return '' }
    }
}

function Colorize {
    param([string]$text, [string]$color)
    return "$(Get-Color $color)${text}${RST}"
}

function Rainbow-String {
    param([string]$text, [int]$offset = 0)
    $out = ''
    $i = $offset
    foreach ($ch in $text.ToCharArray()) {
        if ($ch -ne ' ') {
            $out += $RAINBOW[$i % $RAINBOW.Count] + $ch + $RST
            $i++
        } else {
            $out += ' '
        }
    }
    return $out
}

# ── 5x5 Bitmap Font (5-bit row masks, MSB = leftmost pixel) ──────────────────
$FONT = @{}
$FONT['A'] = @(14, 17, 31, 17, 17)
$FONT['B'] = @(30, 17, 30, 17, 30)
$FONT['C'] = @(14, 16, 16, 16, 14)
$FONT['D'] = @(30, 17, 17, 17, 30)
$FONT['E'] = @(31, 16, 30, 16, 31)
$FONT['F'] = @(31, 16, 30, 16, 16)
$FONT['G'] = @(14, 16, 19, 17, 14)
$FONT['H'] = @(17, 17, 31, 17, 17)
$FONT['I'] = @(31,  4,  4,  4, 31)
$FONT['J'] = @(31,  1,  1, 17, 14)
$FONT['K'] = @(17, 18, 28, 18, 17)
$FONT['L'] = @(16, 16, 16, 16, 31)
$FONT['M'] = @(17, 27, 21, 17, 17)
$FONT['N'] = @(17, 25, 21, 19, 17)
$FONT['O'] = @(14, 17, 17, 17, 14)
$FONT['P'] = @(30, 17, 30, 16, 16)
$FONT['Q'] = @(14, 17, 17, 19, 15)
$FONT['R'] = @(30, 17, 30, 18, 17)
$FONT['S'] = @(15, 16, 14,  1, 30)
$FONT['T'] = @(31,  4,  4,  4,  4)
$FONT['U'] = @(17, 17, 17, 17, 14)
$FONT['V'] = @(17, 17, 17, 10,  4)
$FONT['W'] = @(17, 17, 21, 27, 17)
$FONT['X'] = @(17, 10,  4, 10, 17)
$FONT['Y'] = @(17, 10,  4,  4,  4)
$FONT['Z'] = @(31,  2,  4,  8, 31)
$FONT['0'] = @(14, 19, 21, 25, 14)
$FONT['1'] = @( 4, 12,  4,  4, 14)
$FONT['2'] = @(14, 17,  6,  8, 31)
$FONT['3'] = @(30,  1, 14,  1, 30)
$FONT['4'] = @(17, 17, 31,  1,  1)
$FONT['5'] = @(31, 16, 30,  1, 30)
$FONT['6'] = @(14, 16, 30, 17, 14)
$FONT['7'] = @(31,  1,  2,  4,  4)
$FONT['8'] = @(14, 17, 14, 17, 14)
$FONT['9'] = @(14, 17, 15,  1, 14)
$FONT[' '] = @( 0,  0,  0,  0,  0)
$FONT['!'] = @( 4,  4,  4,  0,  4)
$FONT['?'] = @(14, 17,  6,  0,  4)
$FONT['.'] = @( 0,  0,  0,  0,  4)
$FONT['-'] = @( 0,  0, 14,  0,  0)

function Render-BigText {
    param([string]$text, [char]$fill = [char]0x2588)
    $rows = @('', '', '', '', '')
    foreach ($ch in $text.ToUpper().ToCharArray()) {
        $key = [string]$ch
        $bmp = if ($FONT.ContainsKey($key)) { $FONT[$key] } else { $FONT[' '] }
        for ($row = 0; $row -lt 5; $row++) {
            $bits = $bmp[$row]
            $rowStr = ''
            for ($bit = 4; $bit -ge 0; $bit--) {
                if ($bits -band (1 -shl $bit)) { $rowStr += $fill } else { $rowStr += ' ' }
            }
            $rows[$row] += $rowStr + ' '
        }
    }
    return $rows
}

# ── Utilities ─────────────────────────────────────────────────────────────────
function Clear-Screen {
    Write-Host "${ESC}[2J${ESC}[H" -NoNewline
}

function Ask {
    param([string]$prompt)
    Write-Host -NoNewline (Colorize $prompt 'yellow')
    return [Console]::ReadLine()
}

function Separator {
    param([string]$color = 'cyan')
    $w = [Console]::WindowWidth
    $dash = ([string][char]0x2500) * [Math]::Min(($w - 4), 50)
    Write-Host (Colorize ("  " + $dash) $color)
}

function Print-Header {
    Clear-Screen
    $lines = @(
        "  ___   ___ ___ ___ ___   _   ___ _____",
        " /_\ \ / / __/ __|_ _|_ _| /_\ | _ \_ _|",
        "/ _ \ V /\__ \__ \| | | |/ _ \|   / | | ",
        "/_/ \_\_/ |___/___/___|___/_/ \_\_|_\ |_| "
    )
    $off = 0
    foreach ($line in $lines) {
        Write-Host (Rainbow-String $line $off)
        $off += 7
    }
    Write-Host ''
    Separator
    Write-Host ''
}

# ── Mode 1: Text to ASCII Art ─────────────────────────────────────────────────
function Show-AsciiArt {
    Print-Header
    Write-Host (Colorize "  Text to ASCII Art`n" 'cyan')

    $text = Ask "  Enter text > "
    if (-not $text) { return }

    Write-Host ''
    Write-Host (Colorize "  Color mode:" 'cyan')
    Write-Host "    $(Colorize '1' 'yellow'). Rainbow"
    Write-Host "    $(Colorize '2' 'yellow'). Cyan"
    Write-Host "    $(Colorize '3' 'yellow'). Green"
    Write-Host "    $(Colorize '4' 'yellow'). Yellow"
    Write-Host "    $(Colorize '5' 'yellow'). Magenta"
    Write-Host "    $(Colorize '6' 'yellow'). White"
    Write-Host ''

    $choice = Ask "  Select [1-6] > "
    $art = Render-BigText $text

    Write-Host ''
    $w = [Console]::WindowWidth
    $sep = (Colorize ("  " + ([string][char]0x2500) * [Math]::Min(($w - 4), 60)) 'cyan')
    Write-Host $sep
    Write-Host ''

    foreach ($row in $art) {
        switch ($choice) {
            '1' { Write-Host (Rainbow-String "  $row") }
            '2' { Write-Host (Colorize "  $row" 'cyan') }
            '3' { Write-Host (Colorize "  $row" 'green') }
            '4' { Write-Host (Colorize "  $row" 'yellow') }
            '5' { Write-Host (Colorize "  $row" 'magenta') }
            default { Write-Host (Colorize "  $row" 'white') }
        }
        Start-Sleep -Milliseconds 45
    }

    Write-Host ''
    Write-Host $sep
    Write-Host ''
    Ask "  [Enter] to return to menu" | Out-Null
}

# ── Mode 2: Matrix Rain ───────────────────────────────────────────────────────
$MatrixChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%'.ToCharArray()

function Show-MatrixRain {
    Clear-Screen
    $cols = [Console]::WindowWidth
    $rows = [Console]::WindowHeight - 2
    [Console]::CursorVisible = $false

    $drops = New-Object 'System.Collections.Generic.List[hashtable]'
    for ($col = 0; $col -lt $cols; $col++) {
        if ((Get-Random -Maximum 10) -lt 7) {
            $d = @{
                col = $col
                pos = [double](Get-Random -Minimum (-$rows) -Maximum 0)
                spd = (Get-Random -Minimum 4 -Maximum 22) / 10.0
                len = (Get-Random -Minimum 6 -Maximum 22)
            }
            $drops.Add($d)
        }
    }

    [Console]::SetCursorPosition(0, $rows + 1)
    Write-Host -NoNewline (Colorize "  Press any key to return to menu" 'green')

    try {
        while (-not [Console]::KeyAvailable) {
            $sb = New-Object System.Text.StringBuilder 4096

            foreach ($d in $drops) {
                $col  = [int]$d.col
                $head = [int]$d.pos
                $len  = [int]$d.len

                if ($head -ge 0 -and $head -lt $rows) {
                    $ch = $MatrixChars[(Get-Random -Maximum $MatrixChars.Count)]
                    [void]$sb.Append("${ESC}[$($head+1);$($col+1)H${ESC}[97m${ch}${RST}")
                }

                for ($i = 1; $i -le $len; $i++) {
                    $r = $head - $i
                    if ($r -ge 0 -and $r -lt $rows) {
                        $ch = $MatrixChars[(Get-Random -Maximum $MatrixChars.Count)]
                        if ($i -eq 1) {
                            $cc = "${ESC}[92m"
                        } elseif ($i -lt ($len / 2)) {
                            $cc = "${ESC}[32m"
                        } else {
                            $cc = "${ESC}[2;32m"
                        }
                        [void]$sb.Append("${ESC}[$($r+1);$($col+1)H${cc}${ch}${RST}")
                    }
                }

                $er = $head - $len - 1
                if ($er -ge 0 -and $er -lt $rows) {
                    [void]$sb.Append("${ESC}[$($er+1);$($col+1)H ")
                }

                $d.pos += $d.spd
                if (($d.pos - $d.len) -gt $rows) {
                    $d.pos = [double](Get-Random -Minimum (-([int]($rows / 2))) -Maximum 0)
                    $d.spd = (Get-Random -Minimum 4 -Maximum 22) / 10.0
                    $d.len = (Get-Random -Minimum 6 -Maximum 22)
                }
            }
            [Console]::Write($sb.ToString())
            Start-Sleep -Milliseconds 50
        }
        if ([Console]::KeyAvailable) { [Console]::ReadKey($true) | Out-Null }
    } finally {
        [Console]::CursorVisible = $true
        Clear-Screen
    }
}

# ── Mode 3: Rainbow Banner ────────────────────────────────────────────────────
function Show-RainbowBanner {
    Print-Header
    Write-Host (Colorize "  Rainbow Banner`n" 'cyan')
    $text = Ask "  Enter text > "
    if (-not $text) { $text = "HELLO" }

    $art    = Render-BigText $text ([char]0x2588)
    $cols   = [Console]::WindowWidth
    $height = [Console]::WindowHeight
    $artH   = $art.Count
    $artW   = $art[0].Length
    $startR = [Math]::Max(3, [int](($height - $artH) / 2))
    $startC = [Math]::Max(1, [int](($cols  - $artW) / 2))

    [Console]::CursorVisible = $false
    Clear-Screen

    try {
        $cycle = 0
        while (-not [Console]::KeyAvailable) {
            $sb = New-Object System.Text.StringBuilder 2048
            [void]$sb.Append("${ESC}[1;1H")
            [void]$sb.Append((Colorize "  Press any key to stop" 'cyan'))
            [void]$sb.Append(' ' * 20)

            for ($i = 0; $i -lt $art.Count; $i++) {
                [void]$sb.Append("${ESC}[$($startR + $i);${startC}H")
                $j = 0
                foreach ($ch in $art[$i].ToCharArray()) {
                    if ($ch -ne ' ') {
                        $idx = ($i * 4 + $j + $cycle * 2) % $RAINBOW.Count
                        [void]$sb.Append($RAINBOW[$idx] + $ch + $RST)
                        $j++
                    } else {
                        [void]$sb.Append(' ')
                    }
                }
            }
            [Console]::Write($sb.ToString())
            Start-Sleep -Milliseconds 60
            $cycle++
        }
        if ([Console]::KeyAvailable) { [Console]::ReadKey($true) | Out-Null }
    } finally {
        [Console]::CursorVisible = $true
        Clear-Screen
    }
}

# ── Main Loop ─────────────────────────────────────────────────────────────────
while ($true) {
    Print-Header
    Write-Host "    $(Colorize '1' 'yellow'). Text to ASCII Art"
    Write-Host "    $(Colorize '2' 'yellow'). Matrix Rain"
    Write-Host "    $(Colorize '3' 'yellow'). Rainbow Banner"
    Write-Host "    $(Colorize '4' 'yellow'). Exit"
    Write-Host ''
    Separator
    $choice = Ask "  Select [1-4] > "

    switch ($choice) {
        '1' { Show-AsciiArt }
        '2' { Show-MatrixRain }
        '3' { Show-RainbowBanner }
        '4' {
            Clear-Screen
            Write-Host (Rainbow-String "  See you next time!")
            Write-Host ''
            return
        }
    }
}
