# Create a version that actually works
cat > src/count_rules.py << 'EOF'
#!/usr/bin/env python3
"""
Working AWS Config Rule Counter
"""
import boto3

def main():
    print("🔍 Counting AWS Config Rules...")
    
    # Focus on us-east-1 where we know Config is enabled
    try:
        config = boto3.client('configservice', region_name='us-east-1')
        response = config.describe_config_rules()
        rules = response['ConfigRules']
        count = len(rules)
        
        print(f"us-east-1: {count} rules")
        
        # Check other regions too
        total = count
        ec2 = boto3.client('ec2')
        regions = [r['RegionName'] for r in ec2.describe_regions()['Regions'] if r['RegionName'] != 'us-east-1']
        
        for region in regions:
            try:
                config_region = boto3.client('configservice', region_name=region)
                response_region = config_region.describe_config_rules()
                region_count = len(response_region['ConfigRules'])
                if region_count > 0:
                    print(f"{region}: {region_count} rules")
                    total += region_count
            except Exception as e:
                # Skip regions where Config isn't enabled
                continue
        
        print(f"\n🎯 TOTAL: {total} rules")
        return total
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

if __name__ == "__main__":
    main()
EOF
