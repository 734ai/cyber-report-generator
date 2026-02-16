"""
Synthetic log generator for demo and augmentation.
Produces sample security logs and JSON alerts.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# Sample templates for synthetic generation
ALERT_TEMPLATES = [
    {"event_type": "malware_detected", "severity": "high", "source_ip": "192.168.1.105", "dest_ip": "10.0.0.42"},
    {"event_type": "brute_force", "severity": "medium", "source_ip": "203.0.113.22", "target": "ssh"},
    {"event_type": "phishing_email", "severity": "high", "indicator": "suspicious_link"},
    {"event_type": "lateral_movement", "severity": "critical", "technique": "T1021.002"},
    {"event_type": "c2_beacon", "severity": "critical", "domain": "malware-c2.example.com"},
]

IOC_SAMPLES = {
    "ips": ["192.168.1.105", "10.0.0.42", "203.0.113.22", "198.51.100.1"],
    "hashes": ["5d41402abc4b2a76b9719d911017c592", "098f6bcd4621d373cade4e832627b4f6"],
    "domains": ["evil.example.com", "malware-c2.example.com", "phishing.site"],
    "cves": ["CVE-2023-1234", "CVE-2024-5678"],
    "ttps": ["T1021.002", "T1566.001", "T1071.001"],
}


def generate_single_log(timestamp: Optional[datetime] = None) -> str:
    """Generate one synthetic log line."""
    ts = timestamp or datetime.utcnow()
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S UTC")
    tpl = random.choice(ALERT_TEMPLATES)
    event = tpl.copy()
    event["timestamp"] = ts_str
    
    # Add random IOC
    ioc_type = random.choice(list(IOC_SAMPLES.keys()))
    event["ioc"] = random.choice(IOC_SAMPLES[ioc_type])
    
    return json.dumps(event)


def generate_synthetic_dataset(
    num_samples: int = 50,
    output_path: Optional[str] = None,
    start_time: Optional[datetime] = None,
) -> list[str]:
    """
    Generate a synthetic incident dataset (log lines).
    
    Args:
        num_samples: Number of log entries
        output_path: Optional path to save as JSONL
        start_time: Base timestamp (default: 24h ago)
    
    Returns:
        List of log strings
    """
    base = start_time or (datetime.utcnow() - timedelta(hours=24))
    logs: list[str] = []
    
    for i in range(num_samples):
        ts = base + timedelta(minutes=random.randint(0, 1440))
        logs.append(generate_single_log(ts))
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write("\n".join(logs))
    
    return logs


def get_sample_text() -> str:
    """Return sample text input for the demo UI."""
    lines = generate_synthetic_dataset(5)
    return "\n".join(lines)


def get_sample_json() -> str:
    """Return sample JSON array for the demo UI."""
    lines = generate_synthetic_dataset(3)
    parsed = [json.loads(ln) for ln in lines]
    return json.dumps(parsed, indent=2)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Generate synthetic security logs")
    ap.add_argument("-n", "--num", type=int, default=50, help="Number of samples")
    ap.add_argument("-o", "--output", default="data/synth/sample_logs.jsonl")
    args = ap.parse_args()
    generate_synthetic_dataset(num_samples=args.num, output_path=args.output)
    print(f"Generated {args.num} samples -> {args.output}")
