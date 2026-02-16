"""
MITRE ATT&CK-style report templates for dataset augmentation.
Curated writeups based on public ATT&CK technique descriptions.
"""

# Technique ID -> short narrative (for training targets)
ATTACK_WRITEUPS: dict[str, str] = {
    "T1021.002": "SMB/Windows Admin Shares - adversary used SMB to connect to remote shares for lateral movement",
    "T1566.001": "Phishing: Spearphishing Attachment - malicious attachment delivered via email",
    "T1071.001": "Application Layer Protocol: Web Protocols - C2 traffic over HTTP/HTTPS",
    "T1059.001": "Command and Scripting Interpreter: PowerShell - executed malicious scripts",
    "T1047": "Windows Management Instrumentation - used WMI for execution and discovery",
    "T1003.001": "OS Credential Dumping: LSASS Memory - extracted credentials from LSASS",
    "T1027": "Obfuscated Files or Information - employed encoding/encryption to evade detection",
}

# Incident narrative templates (logs -> report)
INCIDENT_TEMPLATES: list[tuple[str, str]] = [
    (
        "multiple brute force attempts from external IP followed by successful auth",
        "External brute force attack succeeded. Recommend blocking source IP and rotating credentials.",
    ),
    (
        "malware hash detected on endpoint, C2 beacon to external domain",
        "Malware infection with C2 callback. Isolate host, collect artifacts, and hunt for lateral movement.",
    ),
    (
        "phishing email with malicious link, user clicked",
        "Phishing compromise. Reset user credentials, review mailbox rules, check for data exfiltration.",
    ),
]
