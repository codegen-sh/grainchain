"""
Simple data analysis example using Grainchain.

This example demonstrates basic data analysis without external dependencies
that might cause installation issues.
"""

import asyncio

from grainchain import Sandbox


async def simple_data_analysis():
    """Perform simple data analysis using only built-in Python libraries."""
    print("📊 Simple Data Analysis with Grainchain")
    print("=" * 50)

    # Create a simple data analysis script using only built-in libraries
    analysis_script = """
import json
import csv
import random
from collections import defaultdict
from datetime import datetime, timedelta

# Generate sample sales data
def generate_sample_data():
    products = ['Product A', 'Product B', 'Product C', 'Product D']
    data = []

    # Generate 30 days of data
    start_date = datetime(2023, 1, 1)
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        for product in products:
            sales = random.randint(50, 150)
            price = random.uniform(10, 50)
            data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'product': product,
                'sales': sales,
                'price': round(price, 2),
                'revenue': round(sales * price, 2)
            })

    return data

# Analyze the data
def analyze_data(data):
    # Calculate totals by product
    product_totals = defaultdict(lambda: {'sales': 0, 'revenue': 0})
    daily_totals = defaultdict(lambda: {'sales': 0, 'revenue': 0})

    for record in data:
        product = record['product']
        date = record['date']
        sales = record['sales']
        revenue = record['revenue']

        product_totals[product]['sales'] += sales
        product_totals[product]['revenue'] += revenue

        daily_totals[date]['sales'] += sales
        daily_totals[date]['revenue'] += revenue

    return product_totals, daily_totals

# Main analysis
if __name__ == '__main__':
    print("Generating sample sales data...")
    data = generate_sample_data()
    print(f"Generated {len(data)} records")

    # Save to CSV
    with open('sales_data.csv', 'w', newline='') as csvfile:
        fieldnames = ['date', 'product', 'sales', 'price', 'revenue']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    print("\\nAnalyzing data...")
    product_totals, daily_totals = analyze_data(data)

    print("\\n=== PRODUCT PERFORMANCE ===")
    for product, totals in sorted(product_totals.items()):
        print(f"{product}: {totals['sales']} units, ${totals['revenue']:.2f} revenue")

    print("\\n=== TOP 5 REVENUE DAYS ===")
    top_days = sorted(daily_totals.items(),
                     key=lambda x: x[1]['revenue'], reverse=True)[:5]
    for date, totals in top_days:
        print(f"{date}: ${totals['revenue']:.2f}")

    # Calculate summary statistics
    total_revenue = sum(record['revenue'] for record in data)
    total_sales = sum(record['sales'] for record in data)
    avg_price = sum(record['price'] for record in data) / len(data)

    print(f"\\n=== SUMMARY ===")
    print(f"Total Revenue: ${total_revenue:.2f}")
    print(f"Total Sales: {total_sales} units")
    print(f"Average Price: ${avg_price:.2f}")
    print(f"Average Revenue per Day: ${total_revenue/30:.2f}")

    # Save results to JSON
    results = {
        'summary': {
            'total_revenue': total_revenue,
            'total_sales': total_sales,
            'average_price': avg_price,
            'average_daily_revenue': total_revenue/30
        },
        'product_performance': dict(product_totals),
        'top_revenue_days': dict(top_days)
    }

    with open('analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("\\n✅ Analysis complete! Results saved to analysis_results.json")
"""

    async with Sandbox(provider="local") as sandbox:
        print(f"🏗️  Created sandbox: {sandbox.sandbox_id}")

        # Upload and run the analysis script
        await sandbox.upload_file("simple_analysis.py", analysis_script)
        result = await sandbox.execute("python simple_analysis.py")

        if result.success:
            print("✅ Analysis completed successfully:")
            print(result.stdout)

            # Download the results
            try:
                results_content = await sandbox.download_file("analysis_results.json")
                print("\n📊 Analysis Results:")
                print("=" * 30)
                print(results_content.decode())
            except Exception as e:
                print(f"Could not download results: {e}")

        else:
            print(f"❌ Analysis failed: {result.stderr}")


async def file_operations_example():
    """Demonstrate file operations with Grainchain."""
    print("\n📁 File Operations Example")
    print("=" * 30)

    async with Sandbox(provider="local") as sandbox:
        # Create multiple files
        files_to_create = {
            "config.json": '{"app_name": "MyApp", "version": "1.0.0"}',
            "data.txt": "Sample data line 1\\nSample data line 2\\nSample data line 3",
            "script.py": "print('Hello from uploaded script!')",
        }

        print("Creating files...")
        for filename, content in files_to_create.items():
            await sandbox.upload_file(filename, content)
            print(f"  ✅ Created {filename}")

        # List all files
        files = await sandbox.list_files(".")
        print(f"\n📋 Files in sandbox: {[f.name for f in files if not f.is_directory]}")

        # Read and display file contents
        for filename in files_to_create.keys():
            content = await sandbox.download_file(filename)
            print(f"\n📄 Content of {filename}:")
            print(content.decode())

        # Execute the Python script
        result = await sandbox.execute("python script.py")
        print(f"\n🐍 Script output: {result.stdout.strip()}")


async def main():
    """Run all simple examples."""
    try:
        await simple_data_analysis()
        await file_operations_example()
        print("\n🎉 All examples completed successfully!")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
