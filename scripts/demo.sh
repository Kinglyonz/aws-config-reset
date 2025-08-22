#!/bin/bash
# Professional AWS Config Cleanup Demo
# Updated for complete GitHub toolkit

echo "🚀 AWS Config Professional Analysis Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Download complete professional toolkit
echo "📥 Downloading professional toolkit..."
curl -s -O https://raw.githubusercontent.com/Kinglyonz/aws-config-reset/main/src/aws_config_reset.py
curl -s -O https://raw.githubusercontent.com/Kinglyonz/aws-config-reset/main/src/count_rules.py
curl -s -O https://raw.githubusercontent.com/Kinglyonz/aws-config-reset/main/src/read_config_report.py
curl -s -O https://raw.githubusercontent.com/Kinglyonz/aws-config-reset/main/src/create_client_report.py

echo "✅ Professional toolkit downloaded!"

# Run discovery analysis
echo "🔍 Running discovery analysis..."
python3 aws_config_reset.py --all-regions

# Calculate business value
echo "💰 Calculating business value..."
python3 count_rules.py

# Generate human-readable reports
echo "📊 Creating professional reports..."
python3 read_config_report.py

# Generate executive documentation
echo "📄 Creating executive documentation..."
python3 create_client_report.py

echo "✅ Analysis complete! Professional deliverables ready:"
ls -la *.txt *.json

echo ""
echo "📄 Client deliverables generated:"
echo "• config_reset_report.json (technical details)"
echo "• Business_Value_Summary.txt (ROI analysis)"
echo "• Human_Readable_Config_Report.txt (detailed analysis)"
echo "• Executive_Summary.txt (one-page for executives)"
echo "• AWS_Config_Cleanup_Report.txt (professional documentation)"

echo ""
echo "🎯 Ready for client presentation!"
echo "💰 Use Business_Value_Summary.txt for pricing discussions"
echo "📊 Use Executive_Summary.txt for decision makers"
echo "📋 Use Human_Readable_Config_Report.txt for technical teams"
