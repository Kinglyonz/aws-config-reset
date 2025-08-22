#!/usr/bin/env python3
"""
Business Value Calculator for AWS Config Cleanup
Updated with market-validated $25/rule manual pricing
"""

import json

def calculate_pricing(total_rules):
    """Calculate pricing based on $3/rule with min $500, max $2,500"""
    base_price = total_rules * 3
    final_price = max(500, min(base_price, 2500))
    return final_price

def calculate_manual_cost(total_rules):
    """Calculate manual cleanup cost at $25 per rule (market-validated)"""
    # Market research shows consultants charge $25-150 per rule
    # Using conservative $25 per rule for defensible comparison
    manual_cost_per_rule = 25
    manual_cost = total_rules * manual_cost_per_rule
    
    # Calculate equivalent hours for display (at $200/hour market rate)
    equivalent_hours = manual_cost / 200 if manual_cost > 0 else 0
    
    return manual_cost, equivalent_hours

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
        manual_cost, equivalent_hours = calculate_manual_cost(total_rules)
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
        
        print("💰 OUR SERVICE PRICING:")
        print(f"   📏 Rules Discovered: {total_rules}")
        print(f"   💵 Price per Rule: $3.00")
        print(f"   🧮 Base Calculation: {total_rules} × $3 = ${total_rules * 3:,}")
        
        if total_rules * 3 < 500:
            print(f"   📈 Minimum Applied: $500 (protects small jobs)")
        elif total_rules * 3 > 2500:
            print(f"   📉 Maximum Applied: $2,500 (competitive enterprise rate)")
        
        print(f"   🎯 YOUR FINAL PRICE: ${our_price:,}")
        print()
        
        print("⚖️ COST COMPARISON vs MANUAL CLEANUP:")
        print(f"   📊 Manual Cost per Rule: $25 (market-validated)")
        print(f"   🧮 Manual Total Cost: {total_rules} × $25 = ${manual_cost:,}")
        print(f"   ⏱️  Equivalent Consultant Hours: {equivalent_hours:.1f} hours (at $200/hour)")
        print(f"   ⚡ Our Automated Service: ${our_price:,} (75 minutes)")
        print(f"   💰 YOUR SAVINGS: ${client_savings:,}")
        print(f"   📈 Cost Reduction: {savings_percentage:.1f}%")
        print(f"   🎉 Return on Investment: {roi_percentage:.0f}%")
        print()
        
        print("🚀 VALUE PROPOSITION:")
        print(f"   ⏱️  Time Savings: {equivalent_hours:.1f} hours → 75 minutes")
        print(f"   💵 Cost Savings: ${client_savings:,} ({savings_percentage:.1f}% reduction)")
        print(f"   🛡️  Risk Elimination: Zero chance of human error")
        print(f"   📊 Professional Reports: Executive-ready documentation included")
        print(f"   🔄 Immediate Delivery: No waiting for consultant scheduling")
        print(f"   🤖 Intelligent Cleanup: Preserves SecurityHub monitoring")
        print()
        
        # Enhanced recommendations based on savings
        if client_savings >= 5000:
            print("🏆 RECOMMENDATION: EXCELLENT ROI candidate for immediate service!")
            print(f"   Massive savings: ${client_savings:,} + complete risk elimination")
            print("   Consider Premium Package with 6-month monitoring ($15,000)")
        elif client_savings >= 2000:
            print("✅ RECOMMENDATION: Strong candidate for Complete Compliance Package!")
            print(f"   Significant savings: ${client_savings:,} + professional delivery")
            print("   Perfect for Complete NIST Package ($9,000)")
        elif client_savings >= 500:
            print("✅ RECOMMENDATION: Good candidate - emphasize speed and risk benefits")
            print("   Focus on 75-minute delivery vs weeks of consultant time")
        else:
            print("💡 RECOMMENDATION: Small environment - emphasize zero-risk automation")
            print("   Position as insurance against manual errors and immediate delivery")
        
        print()
        print("🎯 COMPETITIVE ADVANTAGES:")
        print("   • 75-90% below typical consultant costs")
        print("   • 75 minutes vs days/weeks delivery time") 
        print("   • Zero human error risk")
        print("   • Professional documentation included")
        print("   • Intelligent SecurityHub preservation")
        print("   • NIST 800-171 ready deployment")
        
        # Updated pricing scale examples with new calculations
        print()
        print("📋 PRICING SCALE EXAMPLES:")
        example_counts = [50, 100, 200, 435, 600, 800]
        for count in example_counts:
            service_cost = calculate_pricing(count)
            manual_cost_example = count * 25
            savings_example = manual_cost_example - service_cost
            print(f"   • {count:3d} rules = ${service_cost:,} (saves ${savings_example:,} vs ${manual_cost_example:,} manual)")
        
        print()
        print("📞 PROFESSIONAL SERVICES CONTACT:")
        print("   📧 Email: khalillyons@gmail.com")
        print("   📱 Phone: (703) 795-4193")
        print("   🕐 Service Hours: 24/7 for delivery and support")
        
        # Generate enhanced summary file
        summary = f"""
AWS CONFIG CLEANUP - BUSINESS VALUE ANALYSIS
===========================================

DISCOVERY RESULTS:
• {total_rules} Config rules found across {total_regions} regions
• Analysis completed: {'Dry run (safe)' if data['dry_run'] else 'Live cleanup'}

PRICING COMPARISON:
• Manual cleanup cost: ${manual_cost:,} ({total_rules} rules × $25/rule)
• Our automated service: ${our_price:,}
• Client savings: ${client_savings:,}
• Cost reduction: {savings_percentage:.1f}%
• ROI: {roi_percentage:.0f}%

TIME COMPARISON:
• Manual consultant time: {equivalent_hours:.1f} hours
• Our service delivery: 75 minutes
• Time saved: {equivalent_hours:.1f} hours

VALUE DELIVERED:
• Intelligent SecurityHub preservation
• Professional compliance documentation
• Zero technical risk
• Immediate NIST 800-171 readiness
• Executive-ready reporting

COMPETITIVE ADVANTAGES:
• {savings_percentage:.1f}% cost reduction vs manual consultants
• 75 minutes vs weeks delivery time
• Automated precision vs human error risk
• Professional documentation included
• 24/7 availability vs consultant scheduling

RECOMMENDATION:
{"Excellent ROI candidate - immediate service recommended" if client_savings >= 5000 else
 "Strong candidate for Complete Compliance Package" if client_savings >= 2000 else
 "Good candidate - emphasize speed and risk benefits" if client_savings >= 500 else
 "Focus on zero-risk automation and immediate delivery"}

CONTACT INFORMATION:
Email: khalillyons@gmail.com
Phone: (703) 795-4193
Service Hours: 24/7 delivery and support

Generated: {data.get('timestamp', 'N/A')}
AWS Config Professional Services - Market-Validated Pricing
"""
        
        with open('Business_Value_Summary.txt', 'w') as f:
            f.write(summary)
        
        print()
        print("📄 Business summary saved to: Business_Value_Summary.txt")
        print("💡 Use this summary for client presentations and proposals!")
        print()
        print("🚀 Ready to schedule service delivery?")
        print("   Contact: khalillyons@gmail.com | (703) 795-4193")
        
    except FileNotFoundError:
        print("❌ Error: config_reset_report.json not found!")
        print("📋 Please run the discovery analysis first:")
        print("   python3 aws_config_reset.py --all-regions")
    except Exception as e:
        print(f"❌ Error analyzing business value: {str(e)}")

if __name__ == "__main__":
    analyze_business_value()
