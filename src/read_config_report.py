#!/usr/bin/env python3
"""
Human-Readable AWS Config Report Generator - MARKET-VALIDATED VERSION
Converts technical JSON into beautiful business-friendly reports
Updated with $25/rule manual pricing based on market research
"""

import json
from datetime import datetime
from collections import defaultdict

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

def analyze_rules(rules):
    """Categorize and analyze rules by type"""
    categories = defaultdict(list)
    
    for rule in rules:
        rule_name = rule['name']
        if rule_name.startswith('securityhub-'):
            categories['Security Hub Rules'].append(rule_name)
        elif rule_name.endswith('-conformance-pack-rcn2awzbq'):
            categories['NIST Conformance Pack Rules'].append(rule_name)
        elif 'iam-' in rule_name:
            categories['Identity & Access Management'].append(rule_name)
        elif any(x in rule_name for x in ['s3-', 'bucket']):
            categories['S3 Storage Security'].append(rule_name)
        elif any(x in rule_name for x in ['ec2-', 'instance']):
            categories['EC2 Compute Security'].append(rule_name)
        elif any(x in rule_name for x in ['rds-', 'database']):
            categories['Database Security'].append(rule_name)
        elif any(x in rule_name for x in ['cloudtrail', 'cloud-trail']):
            categories['Audit & Logging'].append(rule_name)
        elif any(x in rule_name for x in ['vpc-', 'network', 'elb-', 'alb-']):
            categories['Network Security'].append(rule_name)
        else:
            categories['Other Security Rules'].append(rule_name)
    
    return categories

def create_business_summary(data):
    """Create executive-friendly summary with market-validated pricing"""
    region_data = data['regions'][0]  # Assuming single region for now
    total_rules = len(region_data['rules'])
    conformance_packs = len(region_data['conformance_packs'])
    
    # Calculate business metrics with market-validated pricing
    service_price = calculate_pricing(total_rules)
    manual_cost, equivalent_hours = calculate_manual_cost(total_rules)
    
    # FIXED: Prevent division by zero
    if manual_cost > 0:
        client_savings = manual_cost - service_price
        cost_reduction_pct = (client_savings / manual_cost) * 100
        roi_pct = (client_savings / service_price) * 100 if service_price > 0 else 0
    else:
        client_savings = 0
        cost_reduction_pct = 0
        roi_pct = 0
    
    summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AWS CONFIG CLEANUP ANALYSIS REPORT                       ║
║                      Market-Validated Business Analysis                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 DISCOVERY RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Total Config Rules Found: {total_rules}
📦 Conformance Packs Found: {conformance_packs}
🌍 Regions Analyzed: {region_data['region']}
🔍 Analysis Type: {'Dry Run (Safe Analysis)' if data['dry_run'] else 'Live Cleanup Executed'}

💰 BUSINESS VALUE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Manual Cost per Rule: $25 (market-validated consultant rates)
🧮 Manual Total Cost: {total_rules} × $25 = ${manual_cost:,}
⏱️  Equivalent Consultant Time: {equivalent_hours:.1f} hours (at $200/hour)
⚡ Our Automated Service: ${service_price:,} (75 minutes)
💰 Your Savings: ${client_savings:,}
📈 Cost Reduction: {cost_reduction_pct:.1f}%
🎉 Return on Investment: {roi_pct:.0f}%

🎯 WHAT THIS MEANS FOR YOUR BUSINESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Your AWS account has significant Config rule complexity
- Manual consultant cleanup would cost ${manual_cost:,}
- High risk of accidentally breaking critical security configurations
- Our intelligent automation preserves SecurityHub monitoring
- Perfect preparation for NIST 800-171 compliance deployment
- Professional documentation and executive reporting included

💰 SERVICE PACKAGE OPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 Intelligent Config Cleanup: ${service_price:,}
   • Multi-region intelligent cleanup
   • SecurityHub preservation
   • Professional documentation
   • 30-minute automated execution
   • Zero risk guarantee

🏛️ Complete NIST 800-171 Package: ${service_price + 7500:,} ⭐ MOST POPULAR
   • Everything in Config Cleanup Service
   • NIST 800-171 conformance pack deployment
   • 100+ compliance monitoring rules
   • Executive compliance documentation
   • 75-minute total delivery time

🏆 Premium Package + 6mo Monitoring: ${service_price + 12000:,}
   • Everything in Complete NIST Package
   • 6 months ongoing compliance monitoring
   • Monthly executive reporting
   • Quarterly compliance reviews
   • Priority support access

📅 Ongoing Services Available:
   • Monthly compliance monitoring: $500-$1,000/month
   • Quarterly security reviews: $1,000/quarter
   • Annual compliance certification: $2,500/year
   • Violation remediation: $200/hour

📞 PROFESSIONAL SERVICES CONTACT:
   📧 Email: khalillyons@gmail.com
   📱 Phone: (703) 795-4193
   🕐 Service Hours: 24/7 for delivery and support

"""
    
    return summary

def create_detailed_breakdown(rules):
    """Create detailed rule breakdown by category"""
    categories = analyze_rules(rules)
    
    breakdown = """
📋 DETAILED RULE BREAKDOWN BY CATEGORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    # Sort categories by count (largest first)
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    for category, rule_list in sorted_categories:
        count = len(rule_list)
        if len(rules) > 0:  # FIXED: Prevent division by zero
            percentage = (count / len(rules)) * 100
        else:
            percentage = 0
        
        # Calculate manual vs service cost for this category
        manual_cost_category = count * 25
        service_cost_category = count * 3
        savings_category = manual_cost_category - service_cost_category
            
        breakdown += f"""
🔹 {category.upper()}
Total Rules: {count} ({percentage:.1f}% of all rules)
Manual Cost: ${manual_cost_category:,} ({count} × $25/rule)
Service Cost: ${service_cost_category:,} ({count} × $3/rule)
Category Savings: ${savings_category:,}

Sample Rules:
"""
        
        # Show first 3 rules as examples
        for i, rule in enumerate(rule_list[:3]):
            # Clean up rule name for display
            clean_name = rule.replace('securityhub-', '').replace('-conformance-pack-rcn2awzbq', '')
            clean_name = clean_name.replace('-', ' ').title()
            breakdown += f"  • {clean_name}\n"
        
        if len(rule_list) > 3:
            breakdown += f"  • ... and {len(rule_list) - 3} more similar rules\n"
        
        breakdown += "\n"
    
    return breakdown

def create_next_steps_guide(data):
    """Create actionable next steps"""
    is_dry_run = data['dry_run']
    
    if is_dry_run:
        guide = """
🚀 RECOMMENDED NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 PHASE 1: REVIEW & APPROVE (This Analysis)
✅ You are here - Safe discovery analysis completed
✅ No changes made to your AWS environment  
✅ Full understanding of cleanup scope and savings established

🧹 PHASE 2: EXECUTE INTELLIGENT CLEANUP (Recommended)
⚡ Run intelligent cleanup in 30 minutes
🛡️ Professional-grade safety protocols
🔒 SecurityHub monitoring preservation
📊 Real-time progress monitoring
📄 Detailed completion documentation

🏛️ PHASE 3: DEPLOY NIST 800-171 (Highly Recommended)
🎯 Clean baseline ready for compliance framework
📋 Professional NIST 800-171 conformance pack deployment
🔒 Enterprise-grade security configuration
📈 Ongoing compliance monitoring setup
⏱️  Additional 45 minutes delivery time

💬 READY TO PROCEED?
Contact us to schedule your service delivery.

📧 Email: khalillyons@gmail.com
📞 Phone: (703) 795-4193
⏱️  Typical scheduling: Within 72 hours
💰 Investment: As calculated above

🎯 COMPETITIVE ADVANTAGES:
   • 75-90% cost savings vs manual consultants
   • 75 minutes vs weeks delivery time
   • Intelligent SecurityHub preservation
   • Zero human error risk
   • Professional documentation included
   • NIST 800-171 ready deployment

"""
    else:
        guide = """
✅ CLEANUP COMPLETED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 Your AWS Config cleanup has been completed successfully!
🧹 All identified rules have been safely removed
🔒 SecurityHub monitoring has been preserved
🎯 Your account is now ready for NIST 800-171 deployment

🚀 RECOMMENDED NEXT STEPS
📋 Deploy NIST 800-171 conformance pack
🔒 Configure enhanced security monitoring
📊 Set up compliance reporting dashboard
📅 Schedule quarterly compliance reviews

💼 ADDITIONAL SERVICES AVAILABLE
🏛️ NIST 800-171 deployment and configuration
📈 Ongoing compliance monitoring
🔍 Monthly security posture reviews
📊 Executive compliance reporting

Contact us for Phase 3 services and ongoing support.

📧 Email: khalillyons@gmail.com
📞 Phone: (703) 795-4193

"""
    
    return guide

def generate_human_readable_report(json_file):
    """Main function to generate human-readable report"""
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Handle empty regions gracefully
    if not data['regions'] or len(data['regions']) == 0:
        print("❌ No regions found in report data.")
        return
    
    # Generate all sections
    summary = create_business_summary(data)
    breakdown = create_detailed_breakdown(data['regions'][0]['rules'])
    next_steps = create_next_steps_guide(data)
    
    # Combine into final report
    final_report = f"""
{summary}

{breakdown}

{next_steps}

═══════════════════════════════════════════════════════════════════════════════
PROFESSIONAL AWS CONFIG CLEANUP SERVICE
Market-Validated Pricing | Intelligent Automation | Professional Delivery

Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

For questions or to schedule service delivery:
📧 Email: khalillyons@gmail.com
📞 Phone: (703) 795-4193
🌐 Service: AWS Config Professional Services
⏱️  Service Hours: 24/7 for delivery and support

Professional. Intelligent. Security-Preserving.
═══════════════════════════════════════════════════════════════════════════════

"""
    
    # Save human-readable report
    output_file = 'Human_Readable_Config_Report.txt'
    with open(output_file, 'w') as f:
        f.write(final_report)
    
    print(f"✅ Human-readable report created: {output_file}")
    print(f"📄 This report is perfect for sharing with non-technical stakeholders!")
    
    # Also create a one-page executive summary with market-validated pricing
    total_rules = len(data['regions'][0]['rules']) if data['regions'] else 0
    service_price = calculate_pricing(total_rules)
    manual_cost, equivalent_hours = calculate_manual_cost(total_rules)
    
    # FIXED: Safe calculation
    if manual_cost > 0 and service_price > 0:
        savings = manual_cost - service_price
        savings_pct = (savings / manual_cost) * 100
    else:
        savings = 0
        savings_pct = 0
    
    exec_summary = f"""
EXECUTIVE SUMMARY - AWS CONFIG CLEANUP ANALYSIS
═══════════════════════════════════════════════

🔍 DISCOVERY: {total_rules} Config rules found requiring cleanup

💰 BUSINESS IMPACT:
  - Manual consultant cost: ${manual_cost:,} ({total_rules} × $25/rule)
  - Equivalent consultant time: {equivalent_hours:.1f} hours
  - Our automated service: ${service_price:,}
  - Net savings: ${savings:,} ({savings_pct:.1f}% reduction)

🎯 RECOMMENDATION: Proceed with Complete NIST Package

Investment: ${service_price + 7500:,} (cleanup + NIST deployment)
Timeline: 75 minutes total
Risk: Zero (intelligent automation with SecurityHub preservation)
Result: Clean environment + complete NIST 800-171 compliance

🏆 COMPETITIVE ADVANTAGES:
  • {savings_pct:.0f}% cost savings vs manual consultants
  • 75 minutes vs weeks delivery time
  • Zero human error risk
  • Professional documentation included
  • Ongoing support available

📞 CONTACT: khalillyons@gmail.com | (703) 795-4193

Prepared by: AWS Config Professional Services
Date: {datetime.now().strftime('%B %d, %Y')}
Analysis: Market-validated pricing and competitive positioning

"""
    
    with open('Executive_Summary.txt', 'w') as f:
        f.write(exec_summary)
    
    print(f"✅ Executive summary created: Executive_Summary.txt")
    print(f"📊 Perfect for forwarding to decision makers!")
    print("")
    print("🚀 Ready to schedule service delivery?")
    print("   Contact: khalillyons@gmail.com | (703) 795-4193")

if __name__ == "__main__":
    generate_human_readable_report('config_reset_report.json')
