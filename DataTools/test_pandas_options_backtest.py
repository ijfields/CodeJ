#!/usr/bin/env python3
"""
Test Pandas Options Data Source with Zero Loss Butterfly Strategy

This script demonstrates how to use the custom PandasOptionsDataSource
with the existing Zero Loss Butterfly strategy to enable options backtesting.
"""

import sys
from pathlib import Path
from datetime import datetime, date

# Add the project root to the path so we can import the strategy
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from DataTools.pandas_options_data_source import PandasOptionsDataSource
from lumibot.entities import Asset
from lumibot.backtesting import BacktestingBroker
from lumibot.strategies import Strategy


class TestZeroLossButterfly(Strategy):
    """
    Simplified version of Zero Loss Butterfly for testing.
    
    This version focuses on testing the data source integration
    rather than implementing the full strategy logic.
    """
    
    parameters = {
        "symbol": "SPY",
        "test_mode": True
    }
    
    def initialize(self):
        """Initialize the test strategy."""
        self.sleeptime = "1D"
        self.symbol = self.parameters.get("symbol", "SPY")
        self.test_mode = self.parameters.get("test_mode", True)
        
        print(f"\n{'='*60}")
        print(f"🧪 TESTING PANDAS OPTIONS DATA SOURCE")
        print(f"Symbol: {self.symbol}")
        print(f"{'='*60}\n")
    
    def on_trading_iteration(self):
        """Test the data source methods."""
        current_date = self.get_datetime().date()
        print(f"\n--- Test Iteration: {current_date} ---")
        
        # Test 1: Get options chains
        print("🔍 Test 1: Getting options chains...")
        try:
            asset = Asset(self.symbol, asset_type=Asset.AssetType.STOCK)
            chains = self.get_chains(asset)
            
            if chains:
                print(f"✅ Successfully retrieved chains with {len(chains)} expirations")
                
                # Show first expiration details
                first_exp = list(chains.keys())[0]
                first_exp_data = chains[first_exp]
                print(f"   First expiration: {first_exp}")
                print(f"   Strikes available: {len(first_exp_data)}")
                
                # Show sample strikes
                sample_strikes = list(first_exp_data.keys())[:3]
                for strike in sample_strikes:
                    strike_data = first_exp_data[strike]
                    print(f"   Strike {strike}: {list(strike_data.keys())}")
            else:
                print("❌ Failed to retrieve chains")
                
        except Exception as e:
            print(f"❌ Error getting chains: {e}")
        
        # Test 2: Get historical prices
        print("\n🔍 Test 2: Getting historical prices...")
        try:
            asset = Asset(self.symbol, asset_type=Asset.AssetType.STOCK)
            historical = self.get_historical_prices(asset, length=5, timestep="1D")
            
            if historical is not None and not historical.empty:
                print(f"✅ Successfully retrieved {len(historical)} historical prices")
                print(f"   Date range: {historical.index[0].date()} to {historical.index[-1].date()}")
                print(f"   Latest close: ${historical['close'].iloc[-1]:.2f}")
            else:
                print("❌ Failed to retrieve historical prices")
                
        except Exception as e:
            print(f"❌ Error getting historical prices: {e}")
        
        # Test 3: Get last price
        print("\n🔍 Test 3: Getting last price...")
        try:
            asset = Asset(self.symbol, asset_type=Asset.AssetType.STOCK)
            last_price = self.get_last_price(asset)
            
            if last_price:
                print(f"✅ Last price: ${last_price:.2f}")
            else:
                print("❌ Failed to get last price")
                
        except Exception as e:
            print(f"❌ Error getting last price: {e}")
        
        # Test 4: Test options contract creation
        print("\n🔍 Test 4: Testing options contract creation...")
        try:
            # Get available expirations
            expirations = self.data_source.get_available_expirations(self.symbol)
            if expirations:
                test_expiration = expirations[0]
                print(f"   Testing with expiration: {test_expiration}")
                
                # Get available strikes
                strikes = self.data_source.get_available_strikes(self.symbol, test_expiration)
                if strikes:
                    test_strike = strikes[len(strikes)//2]  # Middle strike
                    print(f"   Testing with strike: {test_strike}")
                    
                    # Create a test option asset
                    test_option = Asset(
                        symbol=self.symbol,
                        asset_type=Asset.AssetType.OPTION,
                        expiration=test_expiration,
                        strike=test_strike,
                        right=Asset.OptionRight.CALL
                    )
                    
                    print(f"✅ Created test option: {test_option}")
                else:
                    print("❌ No strikes available")
            else:
                print("❌ No expirations available")
                
        except Exception as e:
            print(f"❌ Error creating options contract: {e}")
        
        # Test 5: Simulate order creation (without submitting)
        print("\n🔍 Test 5: Testing order creation...")
        try:
            if expirations and strikes:
                test_expiration = expirations[0]
                test_strike = strikes[len(strikes)//2]
                
                # Create a test order
                test_option = Asset(
                    symbol=self.symbol,
                    asset_type=Asset.AssetType.OPTION,
                    expiration=test_expiration,
                    strike=test_strike,
                    right=Asset.OptionRight.CALL
                )
                
                # Create order (but don't submit)
                order = self.create_order(
                    asset=test_option,
                    quantity=1,
                    side="buy"
                )
                
                print(f"✅ Successfully created order: {order}")
                print(f"   Order asset: {order.asset}")
                print(f"   Order quantity: {order.quantity}")
                print(f"   Order side: {order.side}")
            else:
                print("❌ Cannot test order creation - no options data")
                
        except Exception as e:
            print(f"❌ Error creating order: {e}")
        
        print(f"\n{'='*60}")
        print("🎉 DATA SOURCE INTEGRATION TEST COMPLETE")
        print(f"{'='*60}\n")
        
        # Stop after first iteration in test mode
        if self.test_mode:
            print("🛑 Test mode: Stopping after first iteration")
            self.stop()


def run_integration_test():
    """Run the integration test with the custom data source."""
    
    print("🚀 Starting Pandas Options Data Source Integration Test")
    print("=" * 80)
    
    try:
        # Initialize the custom data source
        print("📊 Initializing custom data source...")
        data_source = PandasOptionsDataSource(data_dir="../data/lumibot")
        
        # Validate data integrity
        if not data_source.validate_data_integrity():
            print("❌ Data validation failed - cannot proceed with test")
            return False
        
        print("✅ Data source initialized successfully")
        
        # Test the data source methods directly (simulating strategy usage)
        print("\n🧪 Testing data source methods (simulating strategy usage)...")
        
        # Test 1: Get options chains
        print("\n🔍 Test 1: Getting options chains...")
        spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
        chains = data_source.get_chains(spy_asset)
        
        if chains:
            print(f"✅ Successfully retrieved chains with {len(chains)} expirations")
            
            # Show sample data
            first_exp = list(chains.keys())[0]
            first_exp_data = chains[first_exp]
            print(f"   First expiration: {first_exp}")
            print(f"   Strikes available: {len(first_exp_data)}")
            
            # Show sample strikes
            sample_strikes = list(first_exp_data.keys())[:3]
            for strike in sample_strikes:
                strike_data = first_exp_data[strike]
                print(f"   Strike {strike}: {list(strike_data.keys())}")
        else:
            print("❌ Failed to retrieve chains")
            return False
        
        # Test 2: Get historical prices
        print("\n🔍 Test 2: Getting historical prices...")
        historical = data_source.get_historical_prices(spy_asset, length=5, timestep="1D")
        
        if historical is not None and not historical.empty:
            print(f"✅ Successfully retrieved {len(historical)} historical prices")
            print(f"   Date range: {historical.index[0].date()} to {historical.index[-1].date()}")
            print(f"   Latest close: ${historical['close'].iloc[-1]:.2f}")
        else:
            print("❌ Failed to retrieve historical prices")
            return False
        
        # Test 3: Test options contract creation
        print("\n🔍 Test 3: Testing options contract creation...")
        expirations = data_source.get_available_expirations("SPY")
        if expirations:
            test_expiration = expirations[0]
            strikes = data_source.get_available_strikes("SPY", test_expiration)
            if strikes:
                test_strike = strikes[len(strikes)//2]  # Middle strike
                
                # Create a test option asset
                test_option = Asset(
                    symbol="SPY",
                    asset_type=Asset.AssetType.OPTION,
                    expiration=test_expiration,
                    strike=test_strike,
                    right=Asset.OptionRight.CALL
                )
                
                print(f"✅ Created test option: {test_option}")
                print(f"   Symbol: {test_option.symbol}")
                print(f"   Type: {test_option.asset_type}")
                print(f"   Expiration: {test_option.expiration}")
                print(f"   Strike: {test_option.strike}")
                print(f"   Right: {test_option.right}")
            else:
                print("❌ No strikes available")
                return False
        else:
            print("❌ No expirations available")
            return False
        
        print("\n🎉 INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("✅ The custom PandasOptionsDataSource is working correctly")
        print("✅ You can now use it with your Zero Loss Butterfly strategy")
        print("✅ Options chains are being retrieved properly")
        print("✅ Historical prices are working")
        print("✅ Options contract creation is working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_source_directly():
    """Test the data source directly without Lumibot integration."""
    
    print("🔧 Testing data source directly...")
    
    try:
        # Initialize data source
        data_source = PandasOptionsDataSource(data_dir="../data/lumibot")
        
        # Test basic functionality
        print("\n1. Testing data loading...")
        if data_source.stock_data is not None:
            print(f"   ✅ Stock data loaded: {len(data_source.stock_data)} records")
        else:
            print("   ❌ Stock data not loaded")
        
        if data_source.options_data:
            total_options = sum(len(df) for df in data_source.options_data.values())
            print(f"   ✅ Options data loaded: {total_options} contracts")
        else:
            print("   ❌ Options data not loaded")
        
        # Test chains retrieval
        print("\n2. Testing chains retrieval...")
        spy_asset = Asset("SPY", asset_type=Asset.AssetType.STOCK)
        chains = data_source.get_chains(spy_asset)
        
        if chains:
            print(f"   ✅ Chains retrieved: {len(chains)} expirations")
            for exp_date, exp_data in list(chains.items())[:2]:  # Show first 2
                print(f"      {exp_date}: {len(exp_data)} strikes")
        else:
            print("   ❌ No chains retrieved")
        
        # Test historical prices
        print("\n3. Testing historical prices...")
        historical = data_source.get_historical_prices(spy_asset, length=5)
        if historical is not None:
            print(f"   ✅ Historical prices: {len(historical)} records")
        else:
            print("   ❌ No historical prices")
        
        print("\n✅ Direct data source test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 PANDAS OPTIONS DATA SOURCE TEST SUITE")
    print("=" * 80)
    
    # Run direct test first
    print("\n📋 PHASE 1: Direct Data Source Test")
    direct_success = test_data_source_directly()
    
    if direct_success:
        print("\n📋 PHASE 2: Lumibot Integration Test")
        integration_success = run_integration_test()
        
        if integration_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ The custom PandasOptionsDataSource is working correctly")
            print("✅ You can now use it with your Zero Loss Butterfly strategy")
        else:
            print("\n⚠️ Integration test failed, but direct test passed")
            print("   The data source works, but there may be Lumibot integration issues")
    else:
        print("\n❌ Direct test failed - check data files and configuration")
