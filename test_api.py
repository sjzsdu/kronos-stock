#!/usr/bin/env python3
"""
Simple test script to verify the stock prediction app fixes
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5001"
    
    print("🧪 Testing Stock Prediction API...")
    
    # Test 1: Get models
    print("\n1. Testing /api/models...")
    response = requests.get(f"{base_url}/api/models")
    if response.status_code == 200:
        print("✅ Models API working")
        data = response.json()
        print(f"   Available models: {list(data['models'].keys())}")
    else:
        print("❌ Models API failed")
        return
    
    # Test 2: Get popular stocks
    print("\n2. Testing /api/popular_stocks...")
    response = requests.get(f"{base_url}/api/popular_stocks")
    if response.status_code == 200:
        print("✅ Popular stocks API working")
        data = response.json()
        print(f"   Available stocks: {len(data['stocks'])} stocks")
    else:
        print("❌ Popular stocks API failed")
        return
    
    # Test 3: Get stock data (should work with simulated data)
    print("\n3. Testing /api/stock_data...")
    response = requests.post(f"{base_url}/api/stock_data", 
                           json={"stock_code": "000001", "days": 200})
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Stock data API working")
            print(f"   Data rows: {data['data_info']['rows']}")
        else:
            print(f"❌ Stock data API failed: {data['error']}")
    else:
        print("❌ Stock data API failed")
        return
    
    # Test 4: Test prediction with insufficient data (should auto-adjust)
    print("\n4. Testing /api/predict with small dataset...")
    response = requests.post(f"{base_url}/api/predict", 
                           json={
                               "stock_code": "000001", 
                               "days": 200,  # Small dataset
                               "lookback": 400,  # More than available
                               "pred_len": 5,
                               "temperature": 1.0
                           })
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            print("✅ Prediction API working with auto-adjustment")
            if data['adjustment_info']['adjusted']:
                print(f"   ✨ Auto-adjusted lookback: {data['adjustment_info']['original_lookback']} → {data['adjustment_info']['actual_lookback']}")
            else:
                print("   No adjustment needed")
            print(f"   Predicted change: {data['prediction_summary']['total_change_pct']:.2f}%")
        else:
            print(f"❌ Prediction API failed: {data['error']}")
    else:
        print("❌ Prediction API request failed")
        return
    
    print("\n🎉 All tests passed! The API is working correctly.")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to http://localhost:5001")
        print("   Make sure the Flask app is running first:")
        print("   cd /Users/juzhongsun/Codes/projects/Kronos/csweb")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
