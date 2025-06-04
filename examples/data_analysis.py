"""
Data analysis example using Grainchain.

This example demonstrates how to use Grainchain for AI-powered data analysis
tasks, similar to what you might do with Jupyter notebooks or data science environments.
"""

import asyncio

from grainchain import Sandbox, SandboxConfig


async def setup_data_environment(sandbox: Sandbox):
    """Set up a data analysis environment with required packages."""
    print("📦 Setting up data analysis environment...")

    # Install required packages with longer timeout
    print("Installing pandas and numpy...")
    result = await sandbox.execute("pip install pandas numpy")
    if not result.success:
        print(f"Failed to install pandas/numpy: {result.stderr}")
        return False

    print("Installing matplotlib...")
    result = await sandbox.execute("pip install matplotlib")
    if not result.success:
        print(f"Failed to install matplotlib: {result.stderr}")
        return False

    print("Installing seaborn...")
    result = await sandbox.execute("pip install seaborn")
    if not result.success:
        print(f"Failed to install seaborn: {result.stderr}")
        return False

    print("✅ Packages installed successfully")
    return True


async def create_sample_data(sandbox: Sandbox):
    """Create sample data for analysis."""
    print("📊 Creating sample data...")

    # Create a Python script to generate sample data
    data_script = """
import pandas as pd
import numpy as np

# Generate sample sales data
np.random.seed(42)
dates = pd.date_range('2023-01-01', periods=365, freq='D')
products = ['Product A', 'Product B', 'Product C', 'Product D']

data = []
for date in dates:
    for product in products:
        sales = np.random.normal(100, 20)  # Normal distribution around 100
        price = np.random.uniform(10, 50)  # Random price between 10-50
        data.append({
            'date': date,
            'product': product,
            'sales': max(0, sales),  # Ensure non-negative sales
            'price': price,
            'revenue': max(0, sales) * price
        })

df = pd.DataFrame(data)
df.to_csv('sales_data.csv', index=False)
print(f"Created dataset with {len(df)} rows")
print(df.head())
"""

    await sandbox.upload_file("create_data.py", data_script)
    result = await sandbox.execute("python create_data.py")

    if result.success:
        print("✅ Sample data created")
        print(result.stdout)
    else:
        print(f"❌ Data creation failed: {result.stderr}")

    return result.success


async def analyze_data(sandbox: Sandbox):
    """Perform data analysis."""
    print("🔍 Performing data analysis...")

    analysis_script = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
df = pd.read_csv('sales_data.csv')
df['date'] = pd.to_datetime(df['date'])

print("=== DATASET OVERVIEW ===")
print(f"Dataset shape: {df.shape}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Products: {df['product'].unique()}")
print()

print("=== BASIC STATISTICS ===")
print(df.describe())
print()

print("=== REVENUE BY PRODUCT ===")
revenue_by_product = df.groupby('product')['revenue'].sum().sort_values(ascending=False)
print(revenue_by_product)
print()

print("=== MONTHLY TRENDS ===")
df['month'] = df['date'].dt.to_period('M')
monthly_revenue = df.groupby('month')['revenue'].sum()
print(monthly_revenue.head(10))
print()

print("=== TOP PERFORMING DAYS ===")
daily_revenue = df.groupby('date')['revenue'].sum().sort_values(ascending=False)
print(daily_revenue.head(10))
print()

# Create visualizations
plt.figure(figsize=(15, 10))

# Revenue by product
plt.subplot(2, 2, 1)
revenue_by_product.plot(kind='bar')
plt.title('Total Revenue by Product')
plt.xticks(rotation=45)

# Monthly revenue trend
plt.subplot(2, 2, 2)
monthly_revenue.plot()
plt.title('Monthly Revenue Trend')
plt.xticks(rotation=45)

# Sales distribution
plt.subplot(2, 2, 3)
plt.hist(df['sales'], bins=30, alpha=0.7)
plt.title('Sales Distribution')
plt.xlabel('Sales')
plt.ylabel('Frequency')

# Price vs Sales scatter
plt.subplot(2, 2, 4)
plt.scatter(df['price'], df['sales'], alpha=0.5)
plt.title('Price vs Sales')
plt.xlabel('Price')
plt.ylabel('Sales')

plt.tight_layout()
plt.savefig('analysis_charts.png', dpi=150, bbox_inches='tight')
print("📊 Charts saved to analysis_charts.png")

# Advanced analysis
print("=== CORRELATION ANALYSIS ===")
correlation = df[['sales', 'price', 'revenue']].corr()
print(correlation)
print()

print("=== PRODUCT PERFORMANCE METRICS ===")
product_metrics = df.groupby('product').agg({
    'sales': ['mean', 'std', 'sum'],
    'price': ['mean', 'std'],
    'revenue': ['sum', 'mean']
}).round(2)
print(product_metrics)
"""

    await sandbox.upload_file("analyze_data.py", analysis_script)
    result = await sandbox.execute("python analyze_data.py")

    if result.success:
        print("✅ Analysis completed")
        print(result.stdout)
    else:
        print(f"❌ Analysis failed: {result.stderr}")

    return result.success


async def generate_report(sandbox: Sandbox):
    """Generate a summary report."""
    print("📝 Generating summary report...")

    report_script = """
import pandas as pd
from datetime import datetime

# Load data
df = pd.read_csv('sales_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Generate report
report = f'''
# Sales Data Analysis Report
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Executive Summary
- **Total Revenue**: ${df['revenue'].sum():,.2f}
- **Average Daily Revenue**: ${df.groupby('date')['revenue'].sum().mean():,.2f}
- **Best Performing Product**: {df.groupby('product')['revenue'].sum().idxmax()}
- **Analysis Period**: {df['date'].min().strftime("%Y-%m-%d")} to {df['date'].max().strftime("%Y-%m-%d")}

## Key Insights
1. **Product Performance**: {df.groupby('product')['revenue'].sum().idxmax()} generated the highest revenue
2. **Sales Patterns**: Average sales per transaction: {df['sales'].mean():.1f} units
3. **Pricing**: Average price point: ${df['price'].mean():.2f}

## Recommendations
1. Focus marketing efforts on top-performing products
2. Analyze seasonal trends for inventory planning
3. Consider price optimization for underperforming products

---
*This report was generated automatically using Grainchain*
'''

with open('analysis_report.md', 'w') as f:
    f.write(report)

print("📄 Report saved to analysis_report.md")
print(report)
"""

    await sandbox.upload_file("generate_report.py", report_script)
    result = await sandbox.execute("python generate_report.py")

    if result.success:
        print("✅ Report generated")
        print(result.stdout)

        # Download the report
        report_content = await sandbox.download_file("analysis_report.md")
        print("\n" + "=" * 50)
        print("DOWNLOADED REPORT:")
        print("=" * 50)
        print(report_content.decode())
    else:
        print(f"❌ Report generation failed: {result.stderr}")

    return result.success


async def data_analysis_workflow():
    """Complete data analysis workflow."""
    print("🔬 Starting Data Analysis Workflow with Grainchain")
    print("=" * 60)

    # Configure sandbox for data analysis
    config = SandboxConfig(
        timeout=300,  # 5 minutes for longer operations
        working_directory=".",
        environment_vars={
            "PYTHONPATH": ".",
            "MPLBACKEND": "Agg",  # Use non-interactive matplotlib backend
        },
    )

    try:
        async with Sandbox(provider="local", config=config) as sandbox:
            print(f"🏗️  Created sandbox: {sandbox.sandbox_id}")

            # Step 1: Setup environment
            if not await setup_data_environment(sandbox):
                return

            # Step 2: Create sample data
            if not await create_sample_data(sandbox):
                return

            # Step 3: Analyze data
            if not await analyze_data(sandbox):
                return

            # Step 4: Generate report
            if not await generate_report(sandbox):
                return

            # List all generated files
            print("\n📁 Generated files:")
            files = await sandbox.list_files(".")
            for file in files:
                if not file.is_directory:
                    print(f"  - {file.name} ({file.size} bytes)")

            print("\n🎉 Data analysis workflow completed successfully!")

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback

        traceback.print_exc()


async def ai_code_execution_example():
    """Example of executing AI-generated code."""
    print("\n🤖 AI Code Execution Example")
    print("=" * 40)

    # Simulate AI-generated code for data processing
    ai_generated_code = """
# AI-generated data processing code
import pandas as pd
import numpy as np

def process_sales_data(filename):
    '''Process sales data and return insights'''
    df = pd.read_csv(filename)

    insights = {
        'total_records': len(df),
        'total_revenue': df['revenue'].sum(),
        'avg_sales_per_day': df.groupby('date')['sales'].sum().mean(),
        'top_product': df.groupby('product')['revenue'].sum().idxmax(),
        'revenue_growth': calculate_growth_rate(df)
    }

    return insights

def calculate_growth_rate(df):
    '''Calculate month-over-month growth rate'''
    df['date'] = pd.to_datetime(df['date'])
    monthly = df.groupby(df['date'].dt.to_period('M'))['revenue'].sum()
    if len(monthly) > 1:
        return ((monthly.iloc[-1] - monthly.iloc[0]) / monthly.iloc[0] * 100)
    return 0

# Execute the analysis
if __name__ == '__main__':
    try:
        insights = process_sales_data('sales_data.csv')
        print("AI Analysis Results:")
        for key, value in insights.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    except Exception as e:
        print(f"Error in AI code: {e}")
"""

    async with Sandbox(provider="local") as sandbox:
        # First create the sample data in this sandbox
        data_script = """
import pandas as pd
import numpy as np

# Generate sample sales data
np.random.seed(42)
dates = pd.date_range('2023-01-01', periods=365, freq='D')
products = ['Product A', 'Product B', 'Product C', 'Product D']

data = []
for date in dates:
    for product in products:
        sales = np.random.normal(100, 20)  # Normal distribution around 100
        price = np.random.uniform(10, 50)  # Random price between 10-50
        data.append({
            'date': date,
            'product': product,
            'sales': max(0, sales),  # Ensure non-negative sales
            'price': price,
            'revenue': max(0, sales) * price
        })

df = pd.DataFrame(data)
df.to_csv('sales_data.csv', index=False)
print("Created sample data for AI analysis")
"""

        # Install pandas and numpy first
        await sandbox.execute("pip install pandas numpy")

        # Create the data
        await sandbox.upload_file("create_sample_data.py", data_script)
        await sandbox.execute("python create_sample_data.py")

        # Upload and execute AI-generated code
        await sandbox.upload_file("ai_analysis.py", ai_generated_code)
        result = await sandbox.execute("python ai_analysis.py")

        if result.success:
            print("✅ AI-generated code executed successfully:")
            print(result.stdout)
        else:
            print(f"❌ AI code execution failed: {result.stderr}")


async def main():
    """Run the data analysis examples."""
    await data_analysis_workflow()
    await ai_code_execution_example()


if __name__ == "__main__":
    asyncio.run(main())
