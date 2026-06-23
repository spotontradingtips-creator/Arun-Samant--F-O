"""Tests for order fill confirmation logic"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from src.order_manager import OrderManager, Order, OrderStatus
from src.trading_config import TradingConfig


class TestOrderFillConfirmation:
    """Test order fill confirmation and polling"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock trading config for testing"""
        config = Mock(spec=TradingConfig)
        config.live_trading = False  # Start in paper mode
        return config

    @pytest.fixture
    def order_manager(self, mock_config):
        """Create order manager instance"""
        return OrderManager(mock_config)

    @pytest.fixture
    def mock_api(self):
        """Create a mock API for testing"""
        api = Mock()
        api.place_order = Mock(return_value="ORDER_123")
        api.get_quote = Mock(return_value={"instrument_token": "12345"})
        return api

    def test_order_fill_polling_timeout(self, order_manager, mock_api):
        """Test that polling times out gracefully"""
        # Mock API to return no fill status
        mock_api.get_order_status = Mock(return_value=None)

        order = Order(
            order_id="TEST_001",
            symbol="BANKNIFTY23000CE",
            underlying="BANKNIFTY",
            strike=23000,
            option_type="CE",
            qty=1,
            side="BUY",
            order_time=datetime.now(),
            status=OrderStatus.PLACED,
            broker_order_id="BROKER_123"
        )

        # Call polling with short timeout
        result = order_manager._poll_order_fill(mock_api, order, timeout_seconds=1)

        # Should remain PLACED after timeout (not filled)
        assert result.status == OrderStatus.PLACED
        assert result.broker_order_id == "BROKER_123"

    def test_order_fill_success(self, order_manager, mock_api):
        """Test successful order fill detection"""
        # Mock API to return filled status
        mock_api.get_order_status = Mock(return_value={
            'status': 'FILLED',
            'filled_price': 250.5,
            'price': 250.5
        })

        order = Order(
            order_id="TEST_002",
            symbol="BANKNIFTY23000CE",
            underlying="BANKNIFTY",
            strike=23000,
            option_type="CE",
            qty=1,
            side="BUY",
            order_time=datetime.now(),
            status=OrderStatus.PLACED,
            broker_order_id="BROKER_124"
        )

        result = order_manager._poll_order_fill(mock_api, order, timeout_seconds=5)

        assert result.status == OrderStatus.FILLED
        assert result.filled_price == 250.5

    def test_order_rejection_detection(self, order_manager, mock_api):
        """Test rejection detection during polling"""
        # Mock API to return rejected status
        mock_api.get_order_status = Mock(return_value={
            'status': 'REJECTED',
            'reason': 'Insufficient funds'
        })

        order = Order(
            order_id="TEST_003",
            symbol="BANKNIFTY23000CE",
            underlying="BANKNIFTY",
            strike=23000,
            option_type="CE",
            qty=1,
            side="BUY",
            order_time=datetime.now(),
            status=OrderStatus.PLACED,
            broker_order_id="BROKER_125"
        )

        result = order_manager._poll_order_fill(mock_api, order, timeout_seconds=5)

        assert result.status == OrderStatus.REJECTED
        assert "REJECTED" in result.rejection_reason

    def test_order_cancellation_detection(self, order_manager, mock_api):
        """Test order cancellation detection"""
        mock_api.get_order_status = Mock(return_value={
            'status': 'CANCELLED',
            'reason': 'User cancelled'
        })

        order = Order(
            order_id="TEST_004",
            symbol="BANKNIFTY23000CE",
            underlying="BANKNIFTY",
            strike=23000,
            option_type="CE",
            qty=1,
            side="BUY",
            order_time=datetime.now(),
            status=OrderStatus.PLACED,
            broker_order_id="BROKER_126"
        )

        result = order_manager._poll_order_fill(mock_api, order, timeout_seconds=5)

        assert result.status == OrderStatus.REJECTED
        assert "CANCELLED" in result.rejection_reason

    def test_polling_with_api_error(self, order_manager, mock_api):
        """Test that polling handles API errors gracefully"""
        # Mock API to raise an exception
        mock_api.get_order_status = Mock(side_effect=Exception("API Error"))

        order = Order(
            order_id="TEST_005",
            symbol="BANKNIFTY23000CE",
            underlying="BANKNIFTY",
            strike=23000,
            option_type="CE",
            qty=1,
            side="BUY",
            order_time=datetime.now(),
            status=OrderStatus.PLACED,
            broker_order_id="BROKER_127"
        )

        # Should not raise, just log and timeout
        result = order_manager._poll_order_fill(mock_api, order, timeout_seconds=1)

        assert result.status == OrderStatus.PLACED

    def test_fill_confirmation_in_place_order(self, order_manager, mock_api):
        """Test that place_order calls fill confirmation"""
        # Setup paper mode to avoid actual API calls
        order_manager.live_mode = False

        # Mock get_order_status to return filled
        mock_api.get_order_status = Mock(return_value={
            'status': 'FILLED',
            'filled_price': 255.0
        })

        with patch.object(order_manager, '_poll_order_fill') as mock_poll:
            mock_poll.return_value = Order(
                order_id="TEST_006",
                symbol="BANKNIFTY23000CE",
                underlying="BANKNIFTY",
                strike=23000,
                option_type="CE",
                qty=1,
                side="BUY",
                order_time=datetime.now(),
                status=OrderStatus.FILLED,
                broker_order_id="PAPER_123",
                filled_price=255.0
            )

            order = order_manager.place_order(
                api=mock_api,
                symbol="BANKNIFTY23000CE",
                underlying="BANKNIFTY",
                strike=23000,
                option_type="CE",
                qty=1,
                side="BUY"
            )

            # _poll_order_fill should be called for placed orders
            mock_poll.assert_called_once()

    def test_multiple_polls_until_fill(self, order_manager, mock_api):
        """Test that polling retries until order fills"""
        poll_count = {"count": 0}

        def mock_get_order_status(broker_id):
            poll_count["count"] += 1
            if poll_count["count"] < 3:
                # First two polls return pending
                return None
            else:
                # Third poll returns filled
                return {
                    'status': 'FILLED',
                    'filled_price': 260.0
                }

        mock_api.get_order_status = mock_get_order_status

        order = Order(
            order_id="TEST_007",
            symbol="BANKNIFTY23000CE",
            underlying="BANKNIFTY",
            strike=23000,
            option_type="CE",
            qty=1,
            side="BUY",
            order_time=datetime.now(),
            status=OrderStatus.PLACED,
            broker_order_id="BROKER_128"
        )

        result = order_manager._poll_order_fill(mock_api, order, timeout_seconds=5)

        assert result.status == OrderStatus.FILLED
        assert result.filled_price == 260.0
        assert poll_count["count"] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
