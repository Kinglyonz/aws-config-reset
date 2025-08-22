#!/usr/bin/env python3
"""
AWS Config Reset (Pre-NIST Cleanup) — CloudShell Compatible - FIXED VERSION

Deletes AWS Config artifacts in a safe, region-aware sequence.
FIXED: Uses correct boto3 API calls that actually exist!
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
def bclient(service: str, region: str, profile: Optional[str] = None):
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
            if code in {"ResourceInUseException", "ThrottlingException", "TooManyRequestsException"} or "rate exceeded" in msg:
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
        names.extend(p["ConformancePackName"] for p in resp.get("ConformancePackDetails", []))
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


def list_config_rules(cfg) -> List[str]:
    """This one was already correct"""
    names, token = [], None
    try:
        while True:
            kwargs = {"NextToken": token} if token else {}
            resp = cfg.describe_config_rules(**kwargs)
            names.extend(r["ConfigRuleName"] for r in resp.get("ConfigRules", []))
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


def list_remediation_configs(cfg) -> List[str]:
    """FIXED: Better error handling"""
    names = []
    try:
        resp = cfg.describe_remediation_configurations()
        for rc in resp.get("RemediationConfigurations", []):
            n = rc.get("ConfigRuleName")
            if n:
                names.append(n)
    except Exception as e:
        print(f"Warning: Could not list remediation configs: {e}")
    return sorted(set(names))


def delete_remediation_configs(cfg, dry_run: bool, report: dict, include: List[str], exclude: List[str]):
    for name in list_remediation_configs(cfg):
        if not matches(name, include, exclude):
            continue
        report["remediations"].append({"rule": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_remediation_configuration, ConfigRuleName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"remediation:{name}", "error": str(e)})


def list_aggregators(cfg) -> List[str]:
    """This one was already correct"""
    names = []
    try:
        resp = cfg.describe_configuration_aggregators()
        names.extend(a["ConfigurationAggregatorName"] for a in resp.get("ConfigurationAggregators", []))
    except Exception as e:
        print(f"Warning: Could not list aggregators: {e}")
    return names


def delete_aggregators(cfg, dry_run: bool, report: dict):
    for name in list_aggregators(cfg):
        report["aggregators"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_configuration_aggregator, ConfigurationAggregatorName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"aggregator:{name}", "error": str(e)})


# ----------------------
# Region workflow
# ----------------------
def region_reset(region: str, profile: Optional[str], args) -> dict:
    cfg = bclient("config", region, profile)
    report = {
        "region": region,
        "recorders": [],
        "delivery_channels": [],
        "conformance_packs": [],
        "remediations": [],
        "rules": [],
        "aggregators": [],
        "errors": [],
        "notes": [
            "Note: Org/StackSet-managed artifacts must be removed from the management account."
        ],
    }

    print(f"Processing region: {region}")

    # 1) Stop recorders
    stop_recorders(cfg, args.dry_run, report)

    # 2) Optionally delete delivery channels
    if args.full_disable:
        delete_delivery_channels(cfg, args.dry_run, report)

    # 3) Delete conformance packs
    delete_conformance_packs(cfg, args.dry_run, report, args.include, args.exclude)

    # 4) Delete remediation configs
    delete_remediation_configs(cfg, args.dry_run, report, args.include, args.exclude)

    # 5) Delete config rules
    delete_config_rules(cfg, args.dry_run, report, args.include, args.exclude)

    # 6) Optionally delete aggregators
    if args.delete_aggregators:
        delete_aggregators(cfg, args.dry_run, report)

    return report


# ----------------------
# CLI
# ----------------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Pre-NIST AWS Config Reset - FIXED VERSION")
    ap.add_argument("--profile", help="AWS named profile")
    ap.add_argument("--regions", nargs="*", help="Specific regions (space-separated)")
    ap.add_argument("--all-regions", action="store_true", help="Sweep all enabled regions")
    ap.add_argument("--include", nargs="*", default=[], help="Glob include patterns for rule/pack names")
    ap.add_argument("--exclude", nargs="*", default=[], help="Glob exclude patterns for rule/pack names")
    ap.add_argument("--dry-run", action="store_true", default=True, help="Dry run (default ON). Use --no-dry-run to execute.")
    ap.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    ap.add_argument("--full-disable", action="store_true", help="Also delete delivery channels (disables Config data delivery)")
    ap.add_argument("--delete-aggregators", action="store_true", help="Attempt to delete configuration aggregators")
    ap.add_argument("--json-report", default="config_reset_report.json", help="Path to JSON report output")
    args = ap.parse_args()

    # Region selection
    if not args.all_regions and not args.regions:
        session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
        cur_region = session.region_name or "us-east-1"
        print(f"INFO: No regions provided. Defaulting to current session region: {cur_region}")
        args.regions = [cur_region]
    if args.all_regions:
        args.regions = list_regions(profile=args.profile)
        print(f"INFO: Discovered enabled regions: {', '.join(args.regions)}")

    # Execute regions in parallel
    results = []
    errors = 0
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        futures = {ex.submit(region_reset, r, args.profile, args): r for r in args.regions}
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                errors += 1
                results.append({"region": futures[fut], "errors": [str(e)]})

    # Persist a single report file
    with open(args.json_report, "w") as f:
        json.dump({"dry_run": args.dry_run, "regions": results}, f, indent=2)

    print(f"\n=== Done. Report written to {args.json_report} ===")
    if args.dry_run:
        print("NOTE: Dry run only. Re-run with --no-dry-run to execute deletions.")

    return 0 if errors == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
