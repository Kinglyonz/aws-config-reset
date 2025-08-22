#!/usr/bin/env python3
"""
Human-Readable AWS Config Report Generator
Converts technical JSON into beautiful business-friendly reports
"""
import json
from datetime import datetime
from collections import defaultdict

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
    """Create executive-friendly summary"""
    region_data = data['regions'][0]  # Assuming single region for now
    total_rules = len(region_data['rules'])
    conformance_packs = len(region_data['conformance_packs'])
    
    # Calculate business metrics
    manual_hours = (total_rules * 2) / 60  # 2 minutes per rule
    cost_savings = manual_hours * 240  # $240/hour rate (updated from $180)
    
    summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    AWS CONFIG CLEANUP ANALYSIS REPORT                       ║
║                           Easy-to-Read Summary                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

📊 DISCOVERY RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Total Config Rules Found: {total_rules}
📦 Conformance Packs Found: {conformance_packs}
🌍 Regions Analyzed: {region_data['region']}
🔍 Analysis Type: {'Dry Run (Safe Analysis)' if data['dry_run'] else 'Live Cleanup Executed'}

💰 BUSINESS VALUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐 Manual Cleanup Time: {manual_hours:.1f} hours
💵 Labor Cost at $240/hour: ${cost_savings:,.0f}
⚡ Our Automated Service: 15 minutes
💰 Time Savings Value: ${cost_savings - 100:,.0f}

🎯 WHAT THIS MEANS FOR YOUR BUSINESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Your AWS account has significant Config rule complexity
• Manual cleanup would require {manual_hours:.1f} hours of careful technical work
• High risk of accidentally breaking critical security configurations
• Our automated service eliminates this risk and saves massive time
• Perfect preparation for NIST 800-171 compliance deployment

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
        percentage = (count / len(rules)) * 100
        
        breakdown += f"""
🔹 {category.upper()}
   Total Rules: {count} ({percentage:.1f}% of all rules)
   
   Sample Rules:
"""
        
        # Show first 3 rules as examples
        for i, rule in enumerate(rule_list[:3]):
            # Clean up rule name for display
            clean_name = rule.replace('securityhub-', '').replace('-conformance-pack-rcn2awzbq', '')
            clean_name = clean_name.replace('-', ' ').title()
            breakdown += f"   • {clean_name}\n"
        
        if len(rule_list) > 3:
            breakdown += f"   • ... and {len(rule_list) - 3} more similar rules\n"
        
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
✅ Full understanding of cleanup scope established

🧹 PHASE 2: EXECUTE CLEANUP (Recommended)
⚡ Run automated cleanup in 15 minutes
🛡️ Professional-grade safety protocols
📊 Real-time progress monitoring
📄 Detailed completion documentation

🏛️ PHASE 3: DEPLOY NIST 800-171 (Optional)
🎯 Clean baseline ready for compliance framework
📋 Professional NIST 800-171 conformance pack deployment
🔒 Enterprise-grade security configuration
📈 Ongoing compliance monitoring setup

💰 SERVICE PACKAGE OPTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 Basic Cleanup: $1,500
   • Single region cleanup
   • Essential reporting
   • Standard execution

🏢 Enterprise Cleanup: $3,500  
   • Multi-region cleanup
   • Professional categorized reporting
   • Executive documentation

👑 Premium Package: $5,500
   • Everything in Enterprise
   • NIST 800-171 consultation
   • Deployment planning session

💬 READY TO PROCEED?
Contact us to schedule your cleanup service.
ROI: Save $2,000-5,000+ vs manual cleanup costs.
"""
    else:
        guide = """
✅ CLEANUP COMPLETED SUCCESSFULLY!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎉 Your AWS Config cleanup has been completed successfully!
🧹 All identified rules have been safely removed
🎯 Your account is now ready for NIST 800-171 deployment

🚀 RECOMMENDED NEXT STEPS
📋 Deploy NIST 800-171 conformance pack
🔒 Configure security monitoring and alerting  
📊 Set up compliance reporting dashboard
📅 Schedule quarterly compliance reviews

💼 ADDITIONAL SERVICES AVAILABLE
🏛️ NIST 800-171 deployment and configuration ($2,000)
📈 Ongoing compliance monitoring ($500/month)
🔍 Monthly security posture reviews ($1,000/month)
📊 Executive compliance reporting ($300/month)

Contact us for ongoing compliance and monitoring services.
"""
    
    return guide

def generate_human_readable_report(json_file):
    """Main function to generate human-readable report"""
    
    # Load JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    
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
Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

For questions or to schedule services:
📧 Email: [Your Email]
📞 Phone: [Your Phone]
🌐 Web: [Your Website]

Service Packages: $1,500 (Basic) | $3,500 (Enterprise) | $5,500 (Premium)
═══════════════════════════════════════════════════════════════════════════════
"""
    
    # Save human-readable report
    output_file = 'Human_Readable_Config_Report.txt'
    with open(output_file, 'w') as f:
        f.write(final_report)
    
    print(f"✅ Human-readable report created: {output_file}")
    print(f"📄 This report is perfect for sharing with non-technical stakeholders!")
    
    # Also create a one-page executive summary
    exec_summary = f"""
EXECUTIVE SUMMARY - AWS CONFIG CLEANUP ANALYSIS
═══════════════════════════════════════════════

🔍 DISCOVERY: {len(data['regions'][0]['rules'])} Config rules found requiring cleanup

💰 BUSINESS IMPACT:
• Manual cleanup: {((len(data['regions'][0]['rules']) * 2) / 60):.1f} hours
• Labor cost: ${((len(data['regions'][0]['rules']) * 2) / 60) * 240:,.0f}
• Our service: 15 minutes
• Net savings: ${(((len(data['regions'][0]['rules']) * 2) / 60) * 240) - 100:,.0f}

🎯 RECOMMENDATION: Proceed with automated cleanup service

💰 INVESTMENT OPTIONS:
• Basic Cleanup: $1,500 (single region)
• Enterprise Cleanup: $3,500 (multi-region + professional reports)  
• Premium Package: $5,500 (everything + NIST consultation)

Timeline: 15 minutes
Risk: Zero (professional automated process)
Result: Clean AWS environment ready for NIST 800-171

Prepared by: AWS Config Cleanup Service
Date: {datetime.now().strftime('%B %d, %Y')}
"""
    
    with open('Executive_Summary.txt', 'w') as f:
        f.write(exec_summary)
    
    print(f"✅ Executive summary created: Executive_Summary.txt")
    print(f"📊 Perfect for forwarding to decision makers!")

if __name__ == "__main__":
    generate_human_readable_report('config_reset_report.json')
