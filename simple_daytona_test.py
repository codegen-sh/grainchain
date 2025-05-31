#!/usr/bin/env python3
"""
Simple test to verify Daytona SDK works
"""

try:
    from daytona_sdk import Daytona, DaytonaConfig
    print("✅ Daytona SDK imported successfully")

    # Test configuration
    config = DaytonaConfig(
        api_key="dtn_7ff34af9c746f96e2f43ffe698e0b97af87bb5cc47b2376a1873935ac12f416a",
        api_url="https://api.daytona.io",
        target="us"
    )
    print("✅ Daytona config created successfully")

    # Test client creation
    daytona = Daytona(config)
    print("✅ Daytona client created successfully")

    print("🎉 Basic Daytona SDK test passed!")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

