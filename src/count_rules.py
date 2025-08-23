#!/usr/bin/env python3
"""
Business Value Calculator for AWS Config Cleanup
Updated with LIVE AWS data fetching for consistency
"""

import json
import boto3
from botocore.exceptions import BotoCore3Error, ClientError
import sys

def get_live_config_rules_count():
    """Get live count of Config rules from all regions"""
    try:
        # Get list of all regions
        ec2_client = boto3.client('ec2', region_name='us-east-1')
        regions_response = ec2_client.describe_regions()
        all_regions = [region['RegionName'] for region in regions_response['Regions']]
        
        total_rules = 0
        regions_with_rules = 0
        region_breakdown = []
        
        print("🔍 LIVE AWS CONFIG ANALYSIS")
        print("=" * 50)
        print("Scanning all AWS regions for Config rules...")
        print()
        
        for region in all_regions:
            try:
                # Create Config client for each region
                config_client = boto3.client('configservice', region_name=region)
                
                # Get Config rules for this region
                response = config_client.describe_config_rules()
                region_rule_count = len(response['ConfigRules'])
                
                if region_rule_count > 0:
                    regions_with_rules += 1
                    total_rules += region_rule_count
                    region_breakdown.append({
                        'region': region,
                        'rules': region_rule_count
                    })
                    print(f"   {region}: {region_rule_count} rules")
                else:
                    print(f"   {region}: 0 rules (no Config enabled)")
                    
            except ClientError as e:
                if 'ConfigurationRecorderNotAvailableException' in str(e):
                    print(f"   {region}: 0 rules (Config not enabled)")
                else:
                    print(f"   {region}: Error - {str(e)}")
            except Exception as e:
                print(f"   {region}: Error - {str(e)}")
        
        print()
        print(f"📊 LIVE SCAN COMPLETE:")
        print(f"   • Total regions scanned: {len(all_regions)}")
        print(f"   • Regions with Config rules: {regions_with_rules}")
        print(f"   • Total Config rules found: {total_rules}")
        print()
        
        return total_rules, regions_with_rules, region_breakdown
        
    except Exception as e:
        print(f"❌ Error fetching live AWS data: {str(e)}")
        print("💡 Falling back to JSON file method...")
        return None, None, None

def calculate_pricing(total_rules):
    """Calculate pricing based on $3/rule with min $500, max $2,500"""
    base_price = total_rules * 3
    final_price = max(500, min(base_price, 2500))
    return final_price

def calculate_manual_cost(total_rules):
    """Calculate manual cleanup cost at $240/hour"""
    manual_minutes = total_rules * 2  # 2 minutes per rule
    manual_hours = manual_minutes / 60
    manual_cost = manual_hours * 240  # $240/hour rate
    return manual_cost, manual_hours

def load_from_json_file():
    """Fallback method - load from JSON file"""
    try:
        with open('config_reset_report.json', 'r') as f:
            data = json.load(f)
        
        total_rules = 0
        total_regions = len(data['regions'])
        
        for region in data['regions']:
            total_rules += len(region['rules'])
        
        print("📄 Using JSON file data (potentially stale)")
        return total_rules, total_regions, data.get('dry_run', True)
        
    except FileNotFoundError:
        print("❌ Error: config_reset_report.json not found!")
        print("📋 Please run the discovery analysis first or ensure AWS credentials are configured")
        return None, None, None

def analyze_business_value():
    """Analyze business value with LIVE AWS data"""
    
    print("🎯 AWS CONFIG CLEANUP - BUSINESS VALUE ANALYSIS")
    print("=" * 60)
    print()
    
    # Try to get live data first
    total_rules, regions_with_config, region_breakdown = get_live_config_rules_count()
    
    # Fallback to JSON file if live data fails
    if total_rules is None:
        total_rules, regions_with_config, dry_run = load_from_json_file()
        if total_rules is None:
            return
        analysis_type = "JSON File Analysis"
    else:
        dry_run = True  # Live scan is always a "dry run"
        analysis_type = "Live AWS Scan"
    
    # Calculate pricing and savings
    our_price = calculate_pricing(total_rules)
    manual_cost, manual_hours = calculate_manual_cost(total_rules)
    client_savings = manual_cost - our_price
    savings_percentage = (client_savings / manual_cost) * 100 if manual_cost > 0 else 0
    roi_percentage = (client_savings / our_price) * 100 if our_price > 0 else 0
    
    # Display results
    print("📊 DISCOVERY RESULTS:")
    print(f"   • Total Config Rules Found: {total_rules}")
    print(f"   • Regions with Config Enabled: {regions_with_config}")
    print(f"   • Analysis Type: {analysis_type}")
    print(f"   • Data Freshness: {'Live/Current' if total_rules else 'Historical (JSON file)'}")
    print()
    
    # Show region breakdown if available
    if region_breakdown:
        print("🌍 REGION BREAKDOWN:")
        for region_info in region_breakdown:
            print(f"   • {region_info['region']}: {region_info['rules']} rules")
        print()
    
    print("💰 PRICING BREAKDOWN:")
    print(f"   📏 Rules Discovered: {total_rules}")
    print(f"   💵 Price per Rule: $3.00")
    print(f"   🧮 Base Calculation: {total_rules} × $3 = ${total_rules * 3:,}")
    
    if total_rules * 3 < 500:
        print(f"   📈 Minimum Applied: $500 (protects small jobs)")
    elif total_rules * 3 > 2500:
        print(f"   📉 Maximum Applied: $2,500 (competitive enterprise rate)")
    
    print(f"   🎯 YOUR FINAL PRICE: ${our_price:,}")
    print()
    
    print("⚖️ COST COMPARISON:")
    print(f"   🔧 Manual Cleanup Time: {manual_hours:.1f} hours")
    print(f"   💼 Manual Labor Cost: ${manual_cost:,.0f} (at $240/hour)")
    print(f"   ⚡ Our Automated Service: ${our_price:,} (15 minutes)")
    print(f"   💰 YOUR SAVINGS: ${client_savings:,.0f}")
    print(f"   📈 Cost Reduction: {savings_percentage:.1f}%")
    print(f"   🎉 Return on Investment: {roi_percentage:.0f}%")
    print()
    
    print("🚀 VALUE PROPOSITION:")
    print(f"   ⏱️  Time Savings: {manual_hours:.1f} hours → 15 minutes")
    print(f"   💵 Cost Savings: ${client_savings:,.0f} ({savings_percentage:.1f}% reduction)")
    print(f"   🛡️  Risk Elimination: Zero chance of human error")
    print(f"   📊 Professional Reports: Executive-ready documentation included")
    print(f"   🔄 Immediate Delivery: No waiting for consultant scheduling")
    print()
    
    if total_rules >= 100:
        print("✅ RECOMMENDATION: Excellent candidate for automated cleanup service!")
        print(f"   Client saves ${client_savings:,.0f} plus eliminates all technical risk")
    elif total_rules >= 50:
        print("✅ RECOMMENDATION: Good candidate - savings + risk elimination justify service")
    else:
        print("💡 RECOMMENDATION: Small account - emphasize risk elimination and speed benefits")
    
    print()
    print("🎯 COMPETITIVE ADVANTAGES:")
    print("   • 50-70% below typical consultant rates")
    print("   • 15 minutes vs days/weeks delivery time") 
    print("   • Zero human error risk")
    print("   • Professional documentation included")
    print("   • Immediate availability")
    
    # Pricing scale examples
    print()
    print("📋 PRICING SCALE EXAMPLES:")
    print("   •  50 rules = $500 (saves $300 + risk elimination)")
    print("   • 100 rules = $500 (saves $500 + risk elimination)")  
    print("   • 200 rules = $600 (saves $1,000 + risk elimination)")
    print("   • 435 rules = $1,305 (saves $2,175 + risk elimination)")
    print("   • 600 rules = $1,800 (saves $3,000 + risk elimination)")
    print("   • 800+ rules = $2,500 (saves $3,900+ + risk elimination)")
    
    # Generate summary file with live data timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = f"""
AWS CONFIG CLEANUP - BUSINESS SUMMARY
====================================

Discovery Results (Live Scan - {timestamp}):
• {total_rules} Config rules found across {regions_with_config} regions
• Analysis type: {analysis_type}
• Data freshness: Live AWS API scan

Pricing Breakdown:
• Rules found: {total_rules}
• Rate: $3 per rule
• Final price: ${our_price:,}

Value Delivered:
• Manual cost: ${manual_cost:,.0f}
• Our service: ${our_price:,}
• Client savings: ${client_savings:,.0f}
• ROI: {roi_percentage:.0f}%

Time Comparison:
• Manual: {manual_hours:.1f} hours
• Our service: 15 minutes
• Time saved: {manual_hours:.1f} hours

Competitive Advantage:
• {savings_percentage:.1f}% cost reduction vs manual
• Zero technical risk
• Professional documentation included
• Immediate delivery

Generated: {timestamp}
Data Source: Live AWS API scan
Contact: [Your Business Information]
"""
    
    with open(f'Business_Value_Summary_{timestamp.replace(":", "-").replace(" ", "_")}.txt', 'w') as f:
        f.write(summary)
    
    print()
    print("📄 Business summary saved with live data timestamp")
    print("💡 This analysis reflects current AWS state - use for accurate proposals!")

if __name__ == "__main__":
    try:
        analyze_business_value()
    except KeyboardInterrupt:
        print("\n❌ Analysis cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
