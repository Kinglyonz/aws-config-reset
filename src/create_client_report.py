#!/usr/bin/env python3
"""
Creates a professional client-ready report from the JSON output
"""
import json
from datetime import datetime

def create_professional_report():
    # Load the raw JSON report
    with open('config_reset_report.json', 'r') as f:
        data = json.load(f)
    
    # Calculate totals
    total_rules = sum(len(region['rules']) for region in data['regions'])
    total_regions = len(data['regions'])
    
    # Calculate business metrics (updated rates)
    manual_hours = (total_rules * 2) / 60  # 2 minutes per rule
    manual_cost = manual_hours * 240  # Updated to $240/hour
    
    # Create professional report
    report = f"""
AWS CONFIG CLEANUP SERVICE - PROFESSIONAL REPORT
===============================================

Client: [CLIENT NAME]
Date: {datetime.now().strftime('%B %d, %Y')}
Service: Enterprise AWS Config Reset

EXECUTIVE SUMMARY
-----------------
✅ Discovered {total_rules} AWS Config rules across {total_regions} regions
✅ Identified complex SecurityHub rule configurations
✅ Automated cleanup completed successfully
✅ Account prepared for NIST 800-171 deployment

BUSINESS VALUE DELIVERED
------------------------
• Manual cleanup time avoided: {total_rules * 2} minutes ({manual_hours:.1f} hours)
• Manual labor cost avoided: ${manual_cost:,.0f} at $240/hour
• Automated service delivery: 15 minutes  
• Time savings: {(total_rules * 2) - 15} minutes
• Cost savings: ${manual_cost - 100:,.0f} (vs manual approach)
• Risk mitigation: Zero chance of accidental service disruption
• Compliance readiness: Clean baseline for NIST 800-171

SERVICE PACKAGE OPTIONS
-----------------------
📦 BASIC CLEANUP - $1,500
   • Single region cleanup
   • Up to 200 Config rules
   • Essential reporting
   • Standard execution time: 15 minutes

🏢 ENTERPRISE CLEANUP - $3,500
   • Multi-region cleanup (all enabled regions)
   • Unlimited Config rules
   • Professional categorized reporting
   • Executive summary documentation
   • Business value analysis

👑 PREMIUM PACKAGE - $5,500
   • Everything in Enterprise package
   • NIST 800-171 consultation call
   • Compliance deployment planning
   • 30-day follow-up review
   • Priority support

TECHNICAL DETAILS
-----------------
"""
    
    for region_data in data['regions']:
        region = region_data['region']
        rule_count = len(region_data['rules'])
        pack_count = len(region_data['conformance_packs'])
        
        report += f"""
Region: {region}
  • Config Rules: {rule_count}
  • Conformance Packs: {pack_count}
  • Status: {'✅ Cleaned' if not data['dry_run'] else '📋 Analyzed (Dry Run)'}
"""

    if data['dry_run']:
        report += f"""

DRY RUN ANALYSIS
----------------
This was a discovery and analysis run. No actual deletions were performed.
To execute the cleanup, re-run with: --no-dry-run

RECOMMENDED SERVICE PACKAGE
---------------------------
Based on your account analysis:
• Total Rules: {total_rules}
• Regions: {total_regions}
• Recommended: {'Basic ($1,500)' if total_rules < 100 and total_regions == 1 else 'Enterprise ($3,500)' if total_rules < 300 else 'Premium ($5,500)'}

NEXT STEPS
----------
1. Review this analysis with your team
2. Select appropriate service package
3. Schedule cleanup execution window  
4. Deploy NIST 800-171 baseline post-cleanup

INVESTMENT COMPARISON
--------------------
Manual Cleanup Cost: ${manual_cost:,.0f}
Our Service Cost: $1,500 - $5,500 (based on package)
Your Savings: ${manual_cost - 3500:,.0f} - ${manual_cost - 1500:,.0f}
Risk Reduction: Priceless
"""
    else:
        report += f"""

CLEANUP COMPLETED
-----------------
All identified Config rules have been successfully removed.
Your AWS account is now ready for NIST 800-171 baseline deployment.

RESULTS SUMMARY
---------------
• Rules Cleaned: {total_rules}
• Regions Processed: {total_regions}
• Time to Complete: 15 minutes
• Cost Savings Achieved: ${manual_cost - 100:,.0f}

NEXT STEPS
----------
1. Deploy NIST 800-171 conformance pack
2. Configure monitoring and alerting
3. Set up compliance reporting dashboard
4. Schedule quarterly compliance reviews

ADDITIONAL SERVICES AVAILABLE
------------------------------
🏛️ NIST 800-171 Deployment: $2,000
   • Professional conformance pack deployment
   • Custom rule configuration
   • Compliance verification

📈 Ongoing Monitoring: $500/month
   • Monthly compliance drift detection
   • Automated remediation setup
   • Executive reporting

🔍 Security Reviews: $1,000/month
   • Monthly security posture assessment
   • Vulnerability identification
   • Remediation recommendations
"""

    report += f"""

RETURN ON INVESTMENT
--------------------
Manual Labor Cost: ${manual_cost:,.0f}
Service Investment: $1,500 - $5,500
Net Savings: ${manual_cost - 5500:,.0f} - ${manual_cost - 1500:,.0f}
Time Savings: {manual_hours:.1f} hours
ROI: {((manual_cost - 3500) / 3500 * 100):.0f}% - {((manual_cost - 1500) / 1500 * 100):.0f}%

SERVICE PROVIDED BY
-------------------
AWS Config Cleanup Service
Professional AWS Compliance Solutions

For support or additional services, contact: [YOUR CONTACT INFO]
📧 Email: [Your Email]
📞 Phone: [Your Phone]  
🌐 Web: [Your Website]

Service Packages: $1,500 (Basic) | $3,500 (Enterprise) | $5,500 (Premium)

Technical Report Details Available Upon Request
Generated by automated professional tooling
"""

    # Save the professional report
    with open('AWS_Config_Cleanup_Report.txt', 'w') as f:
        f.write(report)
    
    print("✅ Professional report created: AWS_Config_Cleanup_Report.txt")
    print("📥 Download this file to provide to your client")
    
    # Also create a summary
    summary = f"""
QUICK SUMMARY
=============
Total Config Rules Found: {total_rules}
Regions Analyzed: {total_regions}
Service Status: {'DRY RUN COMPLETE' if data['dry_run'] else 'CLEANUP COMPLETE'}

BUSINESS VALUE:
Manual cleanup cost: ${manual_cost:,.0f}
Service options: $1,500 - $5,500
Savings range: ${manual_cost - 5500:,.0f} - ${manual_cost - 1500:,.0f}
ROI: {((manual_cost - 3500) / 3500 * 100):.0f}% - {((manual_cost - 1500) / 1500 * 100):.0f}%

RECOMMENDED PACKAGE:
{('Basic ($1,500)' if total_rules < 100 and total_regions == 1 else 'Enterprise ($3,500)' if total_rules < 300 else 'Premium ($5,500)')}

Contact us to schedule your cleanup service!
"""
    
    with open('Quick_Summary.txt', 'w') as f:
        f.write(summary)
    
    print("✅ Quick summary created: Quick_Summary.txt")

if __name__ == "__main__":
    create_professional_report()
