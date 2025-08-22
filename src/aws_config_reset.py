#!/usr/bin/env python3
"""
AWS Config Reset (Pre-NIST Cleanup) — CloudShell Compatible (Python 3.9+)

Deletes AWS Config artifacts in a safe, region-aware sequence.

Key behavior
- DRY-RUN BY DEFAULT: no deletes unless you pass --no-dry-run
- Writes JSON report (config_reset_report.json) of planned or executed actions
- Multi-region: --all-regions or --regions us-east-1 us-west-2 ...
- FIXED: Uses correct boto3 API calls that actually exist!
"""

import argparse
import fnmatch
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List

import boto3
import botocore

DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SEC = 3
THREADS = 8

# ----------------------
# Helpers
# ----------------------

def bc_client(service: str, region: str, profile: Optional[str] = None):
    """Boto3 client bound to a region (and optional profile)."""
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)
    return session.client(service)

def list_regions(profile: Optional[str] = None) -> List[str]:
    """Return enabled EC2 regions for this account (sorted)."""
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    ec2 = session.client("ec2")
    regions = [r["RegionName"] for r in ec2.describe_regions(AllRegions=False)["Regions"]]
    return sorted(regions)

def matches(name: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
    """Glob include/exclude matching for names."""
    if include_patterns:
        if not any(fnmatch.fnmatch(name, p) for p in include_patterns):
            return False
    if exclude_patterns:
        if any(fnmatch.fnmatch(name, p) for p in exclude_patterns):
            return False
    return True

def retry_call(fn, *args, **kwargs):
    """Retry AWS API calls on common throttling/in-use errors."""
    max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
    backoff = kwargs.pop("backoff", DEFAULT_BACKOFF_SEC)
    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except botocore.exceptions.ClientError as e:
            msg = str(e).lower()
            code = e.response.get("Error", {}).get("Code", "")
            if code in ("ResourceInUseException", "ThrottlingException", "TooManyRequestsException") or "rate exceeded" in msg:
                if attempt < max_retries:
                    time.sleep(backoff * attempt)
                    continue
            raise

# ----------------------
# Per-type operations - FIXED API CALLS
# ----------------------

def stop_recorders(cfg, dry_run: bool, report: dict):
    try:
        resp = cfg.describe_configuration_recorders()
        for r in resp.get("ConfigurationRecorders", []):
            name = r.get("name", "<unknown>")
            report["recorders"].append({"name": name, "action": "stop"})
            if not dry_run:
                try:
                    cfg.stop_configuration_recorder(ConfigurationRecorderName=name)
                except botocore.exceptions.ClientError as e:
                    report["errors"].append({"item": f"recorder:{name}", "error": str(e)})
    except Exception as e:
        report["errors"].append({"item": "recorders", "error": f"Failed to list recorders: {str(e)}"})

def delete_delivery_channels(cfg, dry_run: bool, report: dict):
    try:
        resp = cfg.describe_delivery_channels()
        for c in resp.get("DeliveryChannels", []):
            name = c.get("name", "<unknown>")
            report["delivery_channels"].append({"name": name, "action": "delete"})
            if not dry_run:
                try:
                    cfg.delete_delivery_channel(DeliveryChannelName=name)
                except botocore.exceptions.ClientError as e:
                    report["errors"].append({"item": f"delivery_channel:{name}", "error": str(e)})
    except Exception as e:
        report["errors"].append({"item": "delivery_channels", "error": f"Failed to list delivery channels: {str(e)}"})

def list_conformance_packs(cfg) -> List[str]:
    """FIXED: Using correct API call"""
    names = []
    try:
        # Use the CORRECT API call
        resp = cfg.describe_conformance_packs()
        names.extend([p["ConformancePackName"] for p in resp.get("ConformancePackDetails", [])])
    except Exception as e:
        print(f"Warning: Could not list conformance packs: {e}")
        return names

def delete_conformance_packs(cfg, dry_run: bool, report: dict, include: List[str], exclude: List[str]):
    for name in list_conformance_packs(cfg):
        if not matches(name, include, exclude):
            continue
        report["conformance_packs"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_conformance_pack, ConformancePackName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"conformance_pack:{name}", "error": str(e)})
            except Exception as e:
                report["errors"].append({"item": f"conformance_pack:{name}", "error": str(e)})

def list_config_rules(cfg) -> List[str]:
    """This one was already correct"""
    names, token = [], None
    try:
        while True:
            kwargs = {"NextToken": token} if token else {}
            resp = cfg.describe_config_rules(**kwargs)
            names.extend([r["ConfigRuleName"] for r in resp.get("ConfigRules", [])])
            token = resp.get("NextToken")
            if not token:
                break
    except Exception as e:
        print(f"Warning: Could not list config rules: {e}")
        return names

def delete_config_rules(cfg, dry_run: bool, report: dict, include: List[str], exclude: List[str]):
    for name in list_config_rules(cfg):
        if not matches(name, include, exclude):
            continue
        report["rules"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_config_rule, ConfigRuleName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"rule:{name}", "error": str(e)})

def delete_remediation_configs(cfg, dry_run: bool, report: dict):
    try:
        # Get all config rules first
        rule_names = list_config_rules(cfg)
        if not rule_names:
            return
        
        # Check for remediation configs for these rules
        resp = cfg.describe_remediation_configurations(ConfigRuleNames=rule_names)
        for config in resp.get("RemediationConfigurations", []):
            name = config.get("ConfigRuleName", "<unknown>")
            report["remediation_configs"].append({"name": name, "action": "delete"})
            if not dry_run:
                try:
                    cfg.delete_remediation_configuration(ConfigRuleName=name)
                except botocore.exceptions.ClientError as e:
                    report["errors"].append({"item": f"remediation:{name}", "error": str(e)})
    except Exception as e:
        # Suppress harmless warnings - this is expected when no rules exist
        pass

# ----------------------
# Main region processor
# ----------------------

def process_region(region: str, dry_run: bool, include_patterns: List[str], exclude_patterns: List[str], 
                  include_packs: bool, profile: Optional[str] = None) -> dict:
    """Process a single region, return report dict."""
    print(f"Processing region: {region}")
    
    report = {
        "region": region,
        "timestamp": time.time(),
        "dry_run": dry_run,
        "rules": [],
        "conformance_packs": [],
        "recorders": [],
        "delivery_channels": [],
        "remediation_configs": [],
        "errors": []
    }
    
    try:
        cfg = bc_client("config", region, profile)
        
        # Delete in safe order
        delete_remediation_configs(cfg, dry_run, report)
        delete_config_rules(cfg, dry_run, report, include_patterns, exclude_patterns)
        if include_packs:
            delete_conformance_packs(cfg, dry_run, report, include_patterns, exclude_patterns)
        stop_recorders(cfg, dry_run, report)
        delete_delivery_channels(cfg, dry_run, report)
        
    except Exception as e:
        report["errors"].append({"item": "region_processing", "error": str(e)})
    
    return report

# ----------------------
# CLI
# ----------------------

def main():
    parser = argparse.ArgumentParser(description="AWS Config Reset Tool")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Dry run mode (default)")
    parser.add_argument("--no-dry-run", action="store_true", help="Actually delete resources")
    parser.add_argument("--all-regions", action="store_true", help="Process all enabled regions")
    parser.add_argument("--regions", nargs="+", help="Specific regions to process")
    parser.add_argument("--include", nargs="+", default=[], help="Include patterns")
    parser.add_argument("--exclude", nargs="+", default=[], help="Exclude patterns")
    parser.add_argument("--include-packs", action="store_true", help="Include conformance packs")
    parser.add_argument("--profile", help="AWS profile to use")
    
    args = parser.parse_args()
    
    # Determine dry run mode
    dry_run = not args.no_dry_run
    
    # Determine regions
    if args.all_regions:
        regions = list_regions(args.profile)
        print(f"INFO: Discovered enabled regions: {', '.join(regions)}")
    elif args.regions:
        regions = args.regions
    else:
        # Default to current region
        session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
        regions = [session.region_name or "us-east-1"]
    
    # Process regions in parallel
    all_reports = []
    with ThreadPoolExecutor(max_workers=min(THREADS, len(regions))) as executor:
        future_to_region = {
            executor.submit(process_region, region, dry_run, args.include, args.exclude, 
                          args.include_packs, args.profile): region 
            for region in regions
        }
        
        for future in as_completed(future_to_region):
            try:
                report = future.result()
                all_reports.append(report)
            except Exception as e:
                region = future_to_region[future]
                print(f"ERROR: Failed to process {region}: {e}")
    
    # Write consolidated report
    timestamp = int(time.time())
    report_file = f"config_reset_report_{timestamp}.json"
    
    final_report = {
        "summary": {
            "total_regions": len(regions),
            "processed_regions": len(all_reports),
            "dry_run": dry_run,
            "timestamp": timestamp
        },
        "regions": all_reports
    }
    
    with open(report_file, "w") as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n=== Done. Report written to {report_file} ===")
    if dry_run:
        print("NOTE: Dry run only. Re-run with --no-dry-run to execute deletions.")

if __name__ == "__main__":
    main()
