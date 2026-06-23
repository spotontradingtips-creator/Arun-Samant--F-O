"""Tests for Implied Volatility (IV) calculation"""

import pytest
import numpy as np
from datetime import datetime, timedelta
from src.indicators import TechnicalIndicators


class TestIVCalculation:
    """Test Implied Volatility calculation accuracy"""

    def test_historical_volatility_calculation(self):
        """Test that historical volatility is calculated correctly"""
        # Create sample price data with known volatility
        prices = np.array([100, 102, 101, 103, 102, 104, 103, 105, 104, 106])

        hv = TechnicalIndicators.calculate_historical_volatility(prices)

        assert isinstance(hv, float), "HV should return a float"
        assert 0 <= hv <= 1, "HV should be between 0 and 1 (annualized)"
        assert hv > 0, "HV should be positive for price series with changes"

    def test_historical_volatility_flat_prices(self):
        """Test that HV is zero or near-zero for flat prices"""
        prices = np.array([100.0] * 10)

        hv = TechnicalIndicators.calculate_historical_volatility(prices)

        assert hv == 0 or hv < 0.001, "HV should be zero for flat prices"

    def test_historical_volatility_period_parameter(self):
        """Test HV with different periods"""
        prices = np.array([100 + i * 0.5 for i in range(100)])

        hv_short = TechnicalIndicators.calculate_historical_volatility(prices, period=10)
        hv_long = TechnicalIndicators.calculate_historical_volatility(prices, period=30)

        assert isinstance(hv_short, float), "Should return float"
        assert isinstance(hv_long, float), "Should return float"
        assert hv_short > 0 and hv_long > 0, "Both should be positive"

    def test_historical_volatility_insufficient_data(self):
        """Test behavior with insufficient data points"""
        prices = np.array([100, 101])

        hv = TechnicalIndicators.calculate_historical_volatility(prices, period=10)

        # Should handle gracefully
        assert isinstance(hv, float), "Should still return a float"
        assert hv >= 0, "Should be non-negative"

    def test_implied_volatility_reasonable_values(self):
        """Test that implied volatility returns reasonable values"""
        # Option parameters
        spot = 100
        strike = 100  # ATM call
        expiry_days = 30
        rate = 0.05  # 5% risk-free rate
        option_price = 2.5  # Market price of call option

        iv = TechnicalIndicators.calculate_implied_volatility(
            spot=spot,
            strike=strike,
            expiry_days=expiry_days,
            rate=rate,
            option_price=option_price,
            option_type="CALL"
        )

        assert isinstance(iv, float), "IV should return a float"
        assert 0 <= iv <= 1, "IV should be between 0 and 1 (0% to 100%)"
        assert iv > 0, "IV should be positive for traded options"

    def test_implied_volatility_puts_and_calls(self):
        """Test IV calculation for both calls and puts"""
        spot = 100
        strike = 105
        expiry_days = 30
        rate = 0.05

        call_price = 1.5
        put_price = 6.0  # Put should be more expensive for OTM call

        iv_call = TechnicalIndicators.calculate_implied_volatility(
            spot, strike, expiry_days, rate, call_price, "CALL"
        )
        iv_put = TechnicalIndicators.calculate_implied_volatility(
            spot, strike, expiry_days, rate, put_price, "PUT"
        )

        assert isinstance(iv_call, float), "Call IV should be float"
        assert isinstance(iv_put, float), "Put IV should be float"
        assert iv_call > 0 and iv_put > 0, "Both should be positive"

    def test_implied_volatility_itm_otm(self):
        """Test IV for ITM and OTM options"""
        spot = 100
        expiry_days = 30
        rate = 0.05

        # ITM call (strike = 95)
        itm_iv = TechnicalIndicators.calculate_implied_volatility(
            spot, 95, expiry_days, rate, 6.0, "CALL"
        )

        # OTM call (strike = 105)
        otm_iv = TechnicalIndicators.calculate_implied_volatility(
            spot, 105, expiry_days, rate, 0.5, "CALL"
        )

        assert itm_iv > 0, "ITM IV should be positive"
        assert otm_iv > 0, "OTM IV should be positive"

    def test_historical_volatility_annualization(self):
        """Test that volatility is properly annualized"""
        # Create 252 trading days of data (1 year)
        np.random.seed(42)
        returns = np.random.normal(0.0003, 0.01, 252)
        prices = 100 * np.exp(np.cumsum(returns))

        hv = TechnicalIndicators.calculate_historical_volatility(prices)

        # Should be roughly 10% annualized (based on 1% daily std)
        assert 0.05 < hv < 0.20, "Annualized HV should be in reasonable range"

    def test_iv_zero_option_price(self):
        """Test behavior with zero option price (edge case)"""
        iv = TechnicalIndicators.calculate_implied_volatility(
            spot=100,
            strike=100,
            expiry_days=30,
            rate=0.05,
            option_price=0.0,
            option_type="CALL"
        )

        # Should return a value, likely near zero
        assert isinstance(iv, float), "Should handle zero price gracefully"
        assert 0 <= iv <= 1, "IV should still be in valid range"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
