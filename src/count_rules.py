#!/usr/bin/env python3
"""
Business Value Calculator for AWS Config Cleanup
Updated with $3/rule pricing model
"""

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

def analyze_business_value():
    """Analyze business value from config reset report"""
    
    try:
        # Load the raw JSON report
        with open('config_reset_report.json', 'r') as f:
            data = json.load(f)
        
        # Calculate totals across all regions
        total_rules = 0
        total_regions = len(data['regions'])
        
        for region in data['regions']:
            total_rules += len(region['rules'])
        
        # Calculate pricing and savings
        our_price = calculate_pricing(total_rules)
        manual_cost, manual_hours = calculate_manual_cost(total_rules)
        client_savings = manual_cost - our_price
        savings_percentage = (client_savings / manual_cost) * 100 if manual_cost > 0 else 0
        roi_percentage = (client_savings / our_price) * 100 if our_price > 0 else 0
        
        # Display results
        print("🎯 AWS CONFIG CLEANUP - BUSINESS VALUE ANALYSIS")
        print("=" * 60)
        print()
        
        print("📊 DISCOVERY RESULTS:")
        print(f"   • Total Config Rules Found: {total_rules}")
        print(f"   • Regions Analyzed: {total_regions}")
        print(f"   • Analysis Type: {'Dry Run (Safe Analysis)' if data['dry_run'] else 'Live Cleanup Completed'}")
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
        
        # Generate summary file
        summary = f"""
AWS CONFIG CLEANUP - BUSINESS SUMMARY
====================================

Discovery Results:
• {total_rules} Config rules found across {total_regions} regions
• Analysis completed: {'Dry run' if data['dry_run'] else 'Live cleanup'}

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

Generated: AWS Config Cleanup Business Tool
Contact: [Your Business Information]
"""
        
        with open('Business_Value_Summary.txt', 'w') as f:
            f.write(summary)
        
        print()
        print("📄 Business summary saved to: Business_Value_Summary.txt")
        print("💡 Use this summary for client presentations and proposals!")
        
    except FileNotFoundError:
        print("❌ Error: config_reset_report.json not found!")
        print("📋 Please run the discovery analysis first:")
        print("   python3 aws_config_reset.py --all-regions")
    except Exception as e:
        print(f"❌ Error analyzing business value: {str(e)}")

if __name__ == "__main__":
    analyze_business_value()

