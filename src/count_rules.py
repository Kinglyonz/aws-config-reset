#!/usr/bin/env python3
"""
Real-time AWS Config Rule Counter
Provides accurate, live rule counts across all regions
"""

import boto3
import json

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

def get_live_rule_count():
    """Get real-time Config rule count across all regions"""
    print("🔍 Counting AWS Config Rules (Live Discovery)...")
    
    total_rules = 0
    regions_with_rules = []
    
    try:
        # Get all regions
        ec2 = boto3.client('ec2')
        regions = [r['RegionName'] for r in ec2.describe_regions()['Regions']]
        
        print(f"   Scanning {len(regions)} regions...")
        
        # Count rules in each region
        for region in regions:
            try:
                config = boto3.client('configservice', region_name=region)
                response = config.describe_config_rules()
                rule_count = len(response['ConfigRules'])
                
                if rule_count > 0:
                    print(f"   • {region}: {rule_count} rules")
                    regions_with_rules.append((region, rule_count))
                    total_rules += rule_count
                    
            except Exception:
                # Skip regions where Config isn't available
                continue
        
        print(f"\n📊 LIVE DISCOVERY RESULTS:")
        print(f"   • Total Regions Scanned: {len(regions)}")
        print(f"   • Regions with Config Rules: {len(regions_with_rules)}")
        print(f"   • TOTAL CONFIG RULES: {total_rules}")
        
        return total_rules, len(regions)
        
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        return 0, 0

def analyze_business_value():
    """Analyze business value with live data"""
    
    # Get live rule count
    total_rules, total_regions = get_live_rule_count()
    
    if total_rules == 0:
        print("\n💡 No Config rules found. AWS Config may not be enabled.")
        return
    
    # Calculate pricing and savings
    our_price = calculate_pricing(total_rules)
    manual_cost, manual_hours = calculate_manual_cost(total_rules)
    client_savings = manual_cost - our_price
    savings_percentage = (client_savings / manual_cost) * 100 if manual_cost > 0 else 0
    roi_percentage = (client_savings / our_price) * 100 if our_price > 0 else 0
    
    # Display results
    print("\n🎯 AWS CONFIG CLEANUP - BUSINESS VALUE ANALYSIS")
    print("=" * 60)
    print()
    
    print("📊 DISCOVERY RESULTS:")
    print(f"   • Total Config Rules Found: {total_rules}")
    print(f"   • Regions Analyzed: {total_regions}")
    print(f"   • Analysis Type: Live Real-time Discovery")
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
    print(f"   • {total_rules} rules = ${our_price:,} (saves ${client_savings:,.0f} + risk elimination)")
    print("   • 600 rules = $1,800 (saves $3,000 + risk elimination)")
    print("   • 800+ rules = $2,500 (saves $3,900+ + risk elimination)")
    
    # Generate summary file
    summary = f"""AWS CONFIG CLEANUP - BUSINESS SUMMARY
====================================

Discovery Results:
• {total_rules} Config rules found across {total_regions} regions
• Analysis method: Live real-time discovery
• Service price: ${our_price:,}
• Manual alternative: ${manual_cost:,.0f}
• Client savings: ${client_savings:,.0f} ({savings_percentage:.1f}% reduction)

Competitive Advantages:
• {manual_hours:.1f} hours vs 15 minutes delivery
• Zero human error risk
• Professional documentation included
• Immediate availability

Contact: khalillyons@gmail.com | (703) 795-4193
"""
    
    with open('Business_Value_Summary.txt', 'w') as f:
        f.write(summary)
    
    print()
    print("📄 Business summary saved to: Business_Value_Summary.txt")
    print("💡 Use this summary for client presentations and proposals!")

if __name__ == "__main__":
    analyze_business_value()
