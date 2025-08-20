#!/usr/bin/env python3
"""
AWS Config Reset (Pre-NIST Cleanup)
Deletes AWS Config artifacts in a safe, region-aware sequence.

Features:
- Dry-run report (default): shows what WOULD be deleted
- Multi-region sweep (auto-discovers enabled regions or accept --regions)
- Safe deletion order per region:
  1) Stop recorder(s)
  2) Delete delivery channels (optional, if --full-disable)
  3) Delete conformance packs
  4) Delete config rules
  5) Delete remediation configs
  6) Delete aggregators (optional via flag)
- Retries/backoff for async DELETING states
- Exclude/Include patterns for rules/packs
- Organization/StackSet awareness hinting
- JSON and text reporting
"""

import argparse
import boto3
import botocore
import fnmatch
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SEC = 3
THREADS = 8

def bclient(service, region, profile=None):
    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)
    return session.client(service)

def list_regions(profile=None):
    # Use EC2 to discover regions that are enabled for the account
    session = boto3.Session(profile_name=profile) if profile else boto3.Session()
    ec2 = session.client("ec2")
    regions = [r["RegionName"] for r in ec2.describe_regions(AllRegions=False)["Regions"]]
    return sorted(regions)

def matches(name, include_patterns, exclude_patterns):
    if include_patterns:
        inc = any(fnmatch.fnmatch(name, p) for p in include_patterns)
        if not inc:
            return False
    if exclude_patterns:
        exc = any(fnmatch.fnmatch(name, p) for p in exclude_patterns)
        if exc:
            return False
    return True

def retry_call(fn, *args, **kwargs):
    max_retries = kwargs.pop("max_retries", DEFAULT_MAX_RETRIES)
    backoff = kwargs.pop("backoff", DEFAULT_BACKOFF_SEC)
    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except botocore.exceptions.ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("ResourceInUseException", "ThrottlingException", "TooManyRequestsException") or "rate exceeded" in str(e).lower():
                if attempt < max_retries:
                    time.sleep(backoff * attempt)
                    continue
            raise

def stop_recorders(cfg, dry_run, report):
    resp = cfg.describe_configuration_recorders()
    recs = resp.get("ConfigurationRecorders", [])
    if not recs:
        return []
    stopped = []
    for r in recs:
        name = r["name"]
        report["recorders"].append({"name": name, "action": "stop"})
        if not dry_run:
            try:
                cfg.stop_configuration_recorder(ConfigurationRecorderName=name)
                stopped.append(name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"recorder:{name}", "error": str(e)})
    return stopped

def delete_delivery_channels(cfg, dry_run, report):
    resp = cfg.describe_delivery_channels()
    chans = resp.get("DeliveryChannels", [])
    deleted = []
    for c in chans:
        name = c["name"]
        report["delivery_channels"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                cfg.delete_delivery_channel(DeliveryChannelName=name)
                deleted.append(name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"delivery_channel:{name}", "error": str(e)})
    return deleted

def list_conformance_packs(cfg):
    packs = []
    token = None
    while True:
        kwargs = {}
        if token:
            kwargs["NextToken"] = token
        resp = cfg.list_conformance_packs(**kwargs)
        packs.extend([p["ConformancePackName"] for p in resp.get("ConformancePackSummaries", [])])
        token = resp.get("NextToken")
        if not token:
            break
    return packs

def delete_conformance_packs(cfg, dry_run, report, include, exclude):
    names = list_conformance_packs(cfg)
    deleted = []
    for name in names:
        if not matches(name, include, exclude):
            continue
        report["conformance_packs"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_conformance_pack, ConformancePackName=name)
                deleted.append(name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"conformance_pack:{name}", "error": str(e)})
    return deleted

def list_config_rules(cfg):
    names = []
    token = None
    while True:
        kwargs = {}
        if token:
            kwargs["NextToken"] = token
        resp = cfg.describe_config_rules(**kwargs)
        for r in resp.get("ConfigRules", []):
            names.append(r["ConfigRuleName"])
        token = resp.get("NextToken")
        if not token:
            break
    return names

def delete_config_rules(cfg, dry_run, report, include, exclude):
    names = list_config_rules(cfg)
    deleted = []
    for name in names:
        if not matches(name, include, exclude):
            continue
        report["rules"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_config_rule, ConfigRuleName=name)
                deleted.append(name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"rule:{name}", "error": str(e)})
    return deleted

def list_remediation_configs(cfg):
    names = []
    token = None
    while True:
        kwargs = {}
        if token:
            kwargs["NextToken"] = token
        resp = cfg.describe_remediation_configurations(**kwargs)
        for rc in resp.get("RemediationConfigurations", []):
            if "ConfigRuleName" in rc:
                names.append(rc["ConfigRuleName"])
        token = resp.get("NextToken")
        if not token:
            break
    return list(set(names))

def delete_remediation_configs(cfg, dry_run, report, include, exclude):
    names = list_remediation_configs(cfg)
    deleted = []
    for name in names:
        if not matches(name, include, exclude):
            continue
        report["remediations"].append({"rule": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_remediation_configuration, ConfigRuleName=name)
                deleted.append(name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"remediation:{name}", "error": str(e)})
    return deleted

def list_aggregators(cfg):
    names = []
    token = None
    while True:
        kwargs = {}
        if token:
            kwargs["NextToken"] = token
        resp = cfg.describe_configuration_aggregators(**kwargs)
        for a in resp.get("ConfigurationAggregators", []):
            names.append(a["ConfigurationAggregatorName"])
        token = resp.get("NextToken")
        if not token:
            break
    return names

def delete_aggregators(cfg, dry_run, report):
    names = list_aggregators(cfg)
    deleted = []
    for name in names:
        report["aggregators"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_configuration_aggregator, ConfigurationAggregatorName=name)
                deleted.append(name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"aggregator:{name}", "error": str(e)})
    return deleted

def region_reset(region, profile, args):
    cfg = bclient("config", region, profile)
    report = {
        "region": region,
        "recorders": [],
        "delivery_channels": [],
        "conformance_packs": [],
        "rules": [],
        "remediations": [],
        "aggregators": [],
        "errors": [],
        "notes": []
    }

    # Org/StackSet hint: quick probe (won’t break execution if not authorized)
    try:
        _ = cfg.list_conformance_pack_statuses(Limit=1)
    except botocore.exceptions.ClientError as e:
        if "AccessDenied" in str(e):
            report["notes"].append("Limited perms: some org/stackset-managed packs may be undeletable here.")

    # 1) Stop recorders
    stop_recorders(cfg, args.dry_run, report)

    # 2) Optionally delete delivery channels (only if fully disabling)
    if args.full_disable:
        delete_delivery_channels(cfg, args.dry_run, report)

    # 3) Delete conformance packs
    delete_conformance_packs(cfg, args.dry_run, report, args.include, args.exclude)

    # 4) Delete remediation configs (before or after rules is fine; do early)
    delete_remediation_configs(cfg, args.dry_run, report, args.include, args.exclude)

    # 5) Delete rules
    delete_config_rules(cfg, args.dry_run, report, args.include, args.exclude)

    # 6) Optionally delete aggregators (often mgmt/central)
    if args.delete_aggregators:
        delete_aggregators(cfg, args.dry_run, report)

    return report

def main():
    ap = argparse.ArgumentParser(description="Pre-NIST AWS Config Reset")
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

    if not args.all_regions and not args.regions:
        print("Tip: No regions specified. Use --all-regions to sweep or --regions us-east-1 us-west-2 ...")
        # default to current session region
        session = boto3.Session(profile_name=args.profile) if args.profile else boto3.Session()
        cur_region = session.region_name or "us-east-1"
        args.regions = [cur_region]

    if args.all_regions:
        args.regions = list_regions(profile=args.profile)

    results = []
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        futures = {ex.submit(region_reset, r, args.profile, args): r for r in args.regions}
        for fut in as_completed(futures):
            results.append(fut.result())

    # Write a single consolidated report
    with open(args.json_report, "w") as f:
        json.dump({"dry_run": args.dry_run, "regions": results}, f, indent=2)
    print(f"\n=== Done. Report written to {args.json_report} ===")
    if args.dry_run:
        print("NOTE: Dry run only. Re-run with --no-dry-run to execute deletions.")

if __name__ == "__main__":
    main()
