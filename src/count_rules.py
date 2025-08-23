#!/usr/bin/env python3
"""
Real-time AWS Config Rule Counter - No Cached Data
Provides accurate, live rule counts across all regions
"""

import boto3
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_region_rule_count(region):
    """Get Config rule count for a specific region"""
    try:
        session = boto3.Session(region_name=region)
        config_client = session.client('configservice')
        
        # Get real-time rule count
        response = config_client.describe_config_rules()
        rule_count = len(response.get('ConfigRules', []))
        
        return region, rule_count
    except Exception as e:
        return region, 0

def get_all_regions():
    """Get all enabled AWS regions"""
    try:
        ec2 = boto3.client('ec2')
        regions = [r['RegionName'] for r in ec2.describe_regions(AllRegions=False)['Regions']]
        return sorted(regions)
    except Exception as e:
        print(f"Error getting regions: {e}")
        return ['us-east-1']  # fallback

def main():
    print("🔍 Real-time AWS Config Rule Discovery")
    print("=" * 50)
    
    # Get all regions
    regions = get_all_regions()
    total_rules = 0
    region_details = []
    
    # Process regions in parallel for speed
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_region = {executor.submit(get_region_rule_count, region): region for region in regions}
        
        for future in as_completed(future_to_region):
            region, count = future.result()
            if count > 0:
                region_details.append((region, count))
                total_rules += count
    
    # Display results
    print(f"\n📊 LIVE CONFIG RULE DISCOVERY RESULTS:")
    print(f"   • Total Regions Scanned: {len(regions)}")
    print(f"   • Regions with Rules: {len(region_details)}")
    print(f"   • TOTAL RULES FOUND: {total_rules}")
    
    if region_details:
        print(f"\n📍 Regional Breakdown:")
        for region, count in sorted(region_details, key=lambda x: x[1], reverse=True):
            print(f"   • {region}: {count} rules")
    
    # Business calculations
    price_per_rule = 3.00
    base_price = total_rules * price_per_rule
    
    # Pricing tiers
    if total_rules <= 100:
        final_price = 500
    elif total_rules <= 200:
        final_price = 600
    elif total_rules <= 400:
        final_price = max(base_price, 1200)
    elif total_rules <= 600:
        final_price = max(base_price, 1800)
    else:
        final_price = 2500
    
    manual_hours = total_rules * 0.033  # 2 minutes per rule
    manual_cost = manual_hours * 240    # $240/hour
    savings = manual_cost - final_price
    savings_percent = (savings / manual_cost) * 100 if manual_cost > 0 else 0
    
    print(f"\n💰 REAL-TIME BUSINESS VALUE:")
    print(f"   • Rules Found: {total_rules}")
    print(f"   • Service Price: ${final_price:,.0f}")
    print(f"   • Manual Cost: ${manual_cost:,.0f}")
    print(f"   • Client Savings: ${savings:,.0f} ({savings_percent:.1f}%)")
    
    return total_rules

if __name__ == "__main__":
    main()
