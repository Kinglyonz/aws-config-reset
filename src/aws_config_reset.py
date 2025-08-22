#!/usr/bin/env python3
"""
AWS Config Reset - Clean Technical Version

Professional AWS Config cleanup with intelligent Security Hub preservation.
Deletes AWS Config artifacts in a safe, region-aware sequence.
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

# Configuration constants
DEFAULT_MAX_RETRIES = 5
DEFAULT_BACKOFF_SEC = 3
THREADS = 8

class OutputFormatter:
    """Clean technical output formatting"""
    
    @staticmethod
    def print_header(title: str):
        """Print a clean header"""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    @staticmethod
    def print_section(title: str):
        """Print a section header"""
        print(f"\n[{title}]")
        print("-" * 40)
    
    @staticmethod
    def print_success(message: str):
        """Print success message"""
        print(f"✓ {message}")
    
    @staticmethod
    def print_warning(message: str):
        """Print warning message"""
        print(f"! {message}")
    
    @staticmethod
    def print_error(message: str):
        """Print error message"""
        print(f"✗ {message}")
    
    @staticmethod
    def print_info(message: str):
        """Print info message"""
        print(f"• {message}")
    
    @staticmethod
    def print_security_analysis(total_rules: int, security_hub_rules: int):
        """Print clean security analysis"""
        print(f"\nSecurity Analysis:")
        print(f"  Total Config rules found: {total_rules}")
        print(f"  Security Hub managed rules: {security_hub_rules}")
        print(f"  Rules available for cleanup: {total_rules - security_hub_rules}")
        if security_hub_rules > 0:
            print(f"  → Security Hub rules will be preserved")

# Helper functions
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
        except Exception as e:
            raise

def list_config_rules(cfg) -> List[str]:
    """List all Config rules with Security Hub detection."""
    names, token = [], None
    security_hub_rules = []
    regular_rules = []
    
    try:
        while True:
            kwargs = {"NextToken": token} if token else {}
            resp = cfg.describe_config_rules(**kwargs)
            for rule in resp.get("ConfigRules", []):
                rule_name = rule["ConfigRuleName"]
                names.append(rule_name)
                
                # Detect Security Hub managed rules
                if (rule.get("Source", {}).get("Owner") == "AWS" and 
                    "SecurityHub" in rule_name):
                    security_hub_rules.append(rule_name)
                else:
                    regular_rules.append(rule_name)
            
            token = resp.get("NextToken")
            if not token:
                break
                
    except Exception as e:
        OutputFormatter.print_warning(f"Could not list config rules: {e}")
        return []
    
    # Display analysis
    if names:
        OutputFormatter.print_security_analysis(len(names), len(security_hub_rules))
        if security_hub_rules:
            print(f"  Security Hub rules: {', '.join(security_hub_rules[:3])}{'...' if len(security_hub_rules) > 3 else ''}")
    
    return names

def delete_config_rules(cfg, rule_names: List[str], include_patterns: List[str], exclude_patterns: List[str], dry_run: bool = False):
    """Delete Config rules (excluding Security Hub rules)."""
    if not rule_names:
        return []
    
    # Filter out Security Hub rules for safety
    safe_rules = []
    preserved_rules = []
    
    for rule_name in rule_names:
        if "SecurityHub" in rule_name:
            preserved_rules.append(rule_name)
            continue
        
        if matches(rule_name, include_patterns, exclude_patterns):
            safe_rules.append(rule_name)
    
    if preserved_rules:
        OutputFormatter.print_info(f"Preserving {len(preserved_rules)} Security Hub rules")
    
    if not safe_rules:
        OutputFormatter.print_info("No rules to delete after filtering")
        return []
    
    OutputFormatter.print_info(f"Processing {len(safe_rules)} rules for cleanup")
    
    if dry_run:
        OutputFormatter.print_info("DRY RUN - Would delete:")
        for rule in safe_rules[:10]:  # Show first 10
            print(f"  - {rule}")
        if len(safe_rules) > 10:
            print(f"  ... and {len(safe_rules) - 10} more")
        return safe_rules
    
    deleted = []
    for rule_name in safe_rules:
        try:
            retry_call(cfg.delete_config_rule, ConfigRuleName=rule_name)
            deleted.append(rule_name)
            OutputFormatter.print_success(f"Deleted rule: {rule_name}")
        except Exception as e:
            OutputFormatter.print_error(f"Failed to delete {rule_name}: {e}")
    
    return deleted

def delete_remediation_configurations(cfg, dry_run: bool = False):
    """Delete remediation configurations."""
    try:
        resp = cfg.describe_remediation_configurations()
        configs = resp.get("RemediationConfigurations", [])
        
        if not configs:
            return []
        
        OutputFormatter.print_info(f"Found {len(configs)} remediation configurations")
        
        if dry_run:
            OutputFormatter.print_info("DRY RUN - Would delete remediation configurations")
            return [c["ConfigRuleName"] for c in configs]
        
        deleted = []
        for config in configs:
            rule_name = config["ConfigRuleName"]
            try:
                retry_call(cfg.delete_remediation_configuration, ConfigRuleName=rule_name)
                deleted.append(rule_name)
                OutputFormatter.print_success(f"Deleted remediation: {rule_name}")
            except Exception as e:
                OutputFormatter.print_error(f"Failed to delete remediation {rule_name}: {e}")
        
        return deleted
    except Exception as e:
        OutputFormatter.print_warning(f"Could not process remediation configurations: {e}")
        return []

def delete_conformance_packs(cfg, dry_run: bool = False):
    """Delete conformance packs."""
    try:
        resp = cfg.describe_conformance_packs()
        packs = resp.get("ConformancePackDetails", [])
        
        if not packs:
            return []
        
        OutputFormatter.print_info(f"Found {len(packs)} conformance packs")
        
        if dry_run:
            OutputFormatter.print_info("DRY RUN - Would delete conformance packs")
            return [p["ConformancePackName"] for p in packs]
        
        deleted = []
        for pack in packs:
            pack_name = pack["ConformancePackName"]
            try:
                retry_call(cfg.delete_conformance_pack, ConformancePackName=pack_name)
                deleted.append(pack_name)
                OutputFormatter.print_success(f"Deleted conformance pack: {pack_name}")
            except Exception as e:
                OutputFormatter.print_error(f"Failed to delete pack {pack_name}: {e}")
        
        return deleted
    except Exception as e:
        OutputFormatter.print_warning(f"Could not process conformance packs: {e}")
        return []

def delete_config_recorders_and_channels(cfg, dry_run: bool = False):
    """Delete configuration recorders and delivery channels."""
    deleted_items = []
    
    try:
        # Delete recorders
        resp = cfg.describe_configuration_recorders()
        recorders = resp.get("ConfigurationRecorders", [])
        
        for recorder in recorders:
            name = recorder["name"]
            if dry_run:
                OutputFormatter.print_info(f"DRY RUN - Would delete recorder: {name}")
                deleted_items.append(f"recorder:{name}")
            else:
                try:
                    retry_call(cfg.delete_configuration_recorder, ConfigurationRecorderName=name)
                    deleted_items.append(f"recorder:{name}")
                    OutputFormatter.print_success(f"Deleted recorder: {name}")
                except Exception as e:
                    OutputFormatter.print_error(f"Failed to delete recorder {name}: {e}")
        
        # Delete delivery channels
        resp = cfg.describe_delivery_channels()
        channels = resp.get("DeliveryChannels", [])
        
        for channel in channels:
            name = channel["name"]
            if dry_run:
                OutputFormatter.print_info(f"DRY RUN - Would delete delivery channel: {name}")
                deleted_items.append(f"channel:{name}")
            else:
                try:
                    retry_call(cfg.delete_delivery_channel, DeliveryChannelName=name)
                    deleted_items.append(f"channel:{name}")
                    OutputFormatter.print_success(f"Deleted delivery channel: {name}")
                except Exception as e:
                    OutputFormatter.print_error(f"Failed to delete channel {name}: {e}")
        
    except Exception as e:
        OutputFormatter.print_warning(f"Could not process recorders/channels: {e}")
    
    return deleted_items

def region_reset(region: str, profile: Optional[str], args) -> dict:
    """Reset AWS Config in a single region."""
    OutputFormatter.print_section(f"Processing Region: {region}")
    
    cfg = bc_client("config", region, profile)
    report = {
        "region": region,
        "timestamp": time.time(),
        "rules": [],
        "remediations": [],
        "conformance_packs": [],
        "recorders_channels": [],
        "notes": []
    }
    
    try:
        # List and process rules
        rule_names = list_config_rules(cfg)
        if rule_names:
            deleted_rules = delete_config_rules(cfg, rule_names, args.include, args.exclude, args.dry_run)
            report["rules"] = deleted_rules
        
        # Process other Config resources
        deleted_remediations = delete_remediation_configurations(cfg, args.dry_run)
        report["remediations"] = deleted_remediations
        
        deleted_packs = delete_conformance_packs(cfg, args.dry_run)
        report["conformance_packs"] = deleted_packs
        
        deleted_infra = delete_config_recorders_and_channels(cfg, args.dry_run)
        report["recorders_channels"] = deleted_infra
        
        # Summary for region
        total_items = len(deleted_rules) + len(deleted_remediations) + len(deleted_packs) + len(deleted_infra)
        if total_items > 0:
            OutputFormatter.print_success(f"Region {region}: {total_items} items processed")
        else:
            OutputFormatter.print_info(f"Region {region}: No items to process")
        
    except Exception as e:
        OutputFormatter.print_error(f"Error processing region {region}: {e}")
        report["notes"].append(f"Error: {str(e)}")
    
    return report

def main():
    """Main function with clean technical output."""
    parser = argparse.ArgumentParser(
        description="AWS Config Reset - Clean Technical Version"
    )
    parser.add_argument("--profile", help="AWS profile name")
    parser.add_argument("--region", help="Single region to process")
    parser.add_argument("--all-regions", action="store_true", help="Process all enabled regions")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--include", nargs="*", default=[], help="Include patterns for rule names")
    parser.add_argument("--exclude", nargs="*", default=[], help="Exclude patterns for rule names")
    
    args = parser.parse_args()
    
    # Clean header
    OutputFormatter.print_header("AWS Config Cleanup Tool")
    if args.dry_run:
        OutputFormatter.print_info("Running in DRY RUN mode - no changes will be made")
    
    if args.all_regions:
        regions = list_regions(args.profile)
        OutputFormatter.print_info(f"Processing {len(regions)} regions")
    elif args.region:
        regions = [args.region]
        OutputFormatter.print_info(f"Processing region: {args.region}")
    else:
        OutputFormatter.print_error("Must specify either --region or --all-regions")
        sys.exit(1)
    
    # Process regions
    all_reports = []
    total_rules_processed = 0
    total_security_hub_preserved = 0
    
    for region in regions:
        try:
            report = region_reset(region, args.profile, args)
            all_reports.append(report)
            
            # Aggregate statistics
            total_rules_processed += len(report["rules"])
            
        except Exception as e:
            OutputFormatter.print_error(f"Failed to process region {region}: {e}")
    
    # Final summary
    OutputFormatter.print_header("Summary")
    OutputFormatter.print_success(f"Processed {len(regions)} regions")
    OutputFormatter.print_info(f"Total rules processed: {total_rules_processed}")
    
    # Save report
    timestamp = int(time.time())
    report_file = f"aws_config_cleanup_report_{timestamp}.json"
    with open(report_file, "w") as f:
        json.dump(all_reports, f, indent=2)
    
    OutputFormatter.print_success(f"Report saved: {report_file}")

if __name__ == "__main__":
    main()
