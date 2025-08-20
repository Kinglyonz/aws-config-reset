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
  4) Delete remediation configs
  5) Delete config rules
  6) Delete aggregators (optional via flag)
- Retries/backoff for async DELETING states / throttling
- Exclude/Include patterns for rule/pack names
- JSON report output
"""

import argparse
import boto3
import botocore
import fnmatch
import json
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
    for r in recs:
        name = r["name"]
        report["recorders"].append({"name": name, "action": "stop"})
        if not dry_run:
            try:
                cfg.stop_configuration_recorder(ConfigurationRecorderName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"recorder:{name}", "error": str(e)})

def delete_delivery_channels(cfg, dry_run, report):
    resp = cfg.describe_delivery_channels()
    chans = resp.get("DeliveryChannels", [])
    for c in chans:
        name = c["name"]
        report["delivery_channels"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                cfg.delete_delivery_channel(DeliveryChannelName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"delivery_channel:{name}", "error": str(e)})

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
    for name in names:
        if not matches(name, include, exclude):
            continue
        report["conformance_packs"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_conformance_pack, ConformancePackName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"conformance_pack:{name}", "error": str(e)})

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
    for name in names:
        if not matches(name, include, exclude):
            continue
        report["rules"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_config_rule, ConfigRuleName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"rule:{name}", "error": str(e)})

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
    for name in names:
        if not matches(name, include, exclude):
            continue
        report["remediations"].append({"rule": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_remediation_configuration, ConfigRuleName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"remediation:{name}", "error": str(e)})

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
    for name in names:
        report["aggregators"].append({"name": name, "action": "delete"})
        if not dry_run:
            try:
                retry_call(cfg.delete_configuration_aggregator, ConfigurationAggregatorName=name)
            except botocore.exceptions.ClientError as e:
                report["errors"].append({"item": f"aggregator:{name}", "error": str(e)})

def region_reset(region, profile, args):
    cfg = bclient("config", region, profile)
    report = {
        "region": region,
        "recorders": [], "delivery_channels": [],
        "conformance_packs": [], "rules": [],
        "remediations": [], "aggregators": [],
        "errors": [], "notes": []
    }

    # NOTE: removed list_conformance_pack_statuses probe for CloudShell compatibility.

    # 1) Stop recorder(s)
    stop_recorders(cfg, args.d_
