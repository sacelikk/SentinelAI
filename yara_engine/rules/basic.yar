rule Suspicious_Strings
{
    meta:
        description = "Detects common suspicious strings often found in malware"
        author = "SentinelAI"
        date = "2026-10-10"
        severity = "Medium"

    strings:
        $s1 = "cmd.exe /c" ascii wide nocase
        $s2 = "powershell.exe -ExecutionPolicy Bypass" ascii wide nocase
        $s3 = "WScript.Shell" ascii wide nocase
        $s4 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run" ascii wide nocase
        
    condition:
        any of them
}

rule Packed_UPX
{
    meta:
        description = "Detects UPX packed executables"
        author = "SentinelAI"
        severity = "Low"

    strings:
        $upx1 = "UPX0" ascii
        $upx2 = "UPX1" ascii
        $upx3 = "UPX!" ascii
        
    condition:
        uint16(0) == 0x5A4D and all of them
}
