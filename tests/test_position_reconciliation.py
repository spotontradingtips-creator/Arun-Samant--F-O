"""Tests for position reconciliation and sync"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta, timezone
from src.position_sync import sync_positions_from_broker
from src.trading_models import TradeType, ExitReason

# IST timezone offset
IST = timezone(timedelta(hours=5, minutes=30))


class TestPositionReconciliation:
    """Test position reconciliation with broker"""

    @pytest.fixture
    def mock_api(self):
        """Create mock API"""
        api = Mock()
        api.get_positions = Mock(return_value={})
        api.get_net_positions = Mock(return_value=[])
        api.get_quote = Mock(return_value={"last_price": 25000})
        return api

    @pytest.fixture
    def mock_bot(self):
        """Create mock trading bot"""
        bot = Mock()
        bot.positions = {}
        bot.enter_trade = Mock()
        bot.exit_trade = Mock()
        bot.sync_daily_pnl = Mock()
        return bot

    def test_sync_empty_positions(self, mock_bot, mock_api):
        """Test syncing when there are no positions"""
        result = sync_positions_from_broker(mock_bot, mock_api)

        assert result == 0
        mock_bot.enter_trade.assert_not_called()
        mock_bot.exit_trade.assert_not_called()

    def test_sync_detects_broker_api_error(self, mock_bot, mock_api):
        """Test graceful handling of broker API errors"""
        # API returns None (error)
        mock_api.get_positions = Mock(return_value=None)
        mock_api.get_net_positions = Mock(return_value=None)

        # Bot has no local memory
        mock_bot.positions = {}

        result = sync_positions_from_broker(mock_bot, mock_api)

        assert result == 0  # Fresh state, no positions

    def test_sync_uses_local_memory_on_api_error(self, mock_bot, mock_api):
        """Test that local memory is used when broker API fails"""
        # API returns None (error)
        mock_api.get_positions = Mock(return_value=None)
        mock_api.get_net_positions = Mock(return_value=None)

        # Bot has existing positions in memory
        mock_position = Mock()
        mock_position.entry_time = datetime.now(IST)
        mock_bot.positions = {"NIFTY50": mock_position}

        result = sync_positions_from_broker(mock_bot, mock_api)

        # Should use local memory (1 position)
        assert result == 1

    def test_sync_imports_new_position_from_broker(self, mock_bot, mock_api):
        """Test importing a new position from broker"""
        # Broker has a position
        broker_positions = {
            ("NIFTY26FEB25000CE", "NFO"): {
                "qty": 1,
                "price": 250.0,
                "ltp": 255.0
            }
        }
        mock_api.get_positions = Mock(return_value=broker_positions)
        mock_api.get_net_positions = Mock(return_value=[])

        # Mock SymbolMaster (imported dynamically in function)
        with patch("src.symbol_master.SymbolMaster") as MockSymbolMaster:
            mock_sm = Mock()
            mock_sm.get_symbol = Mock(return_value="NIFTY26FEB25000CE")
            MockSymbolMaster.return_value = mock_sm

            result = sync_positions_from_broker(mock_bot, mock_api)

            # Should import 1 new position
            assert result == 1
            mock_bot.enter_trade.assert_called_once()

    def test_sync_detects_closed_positions(self, mock_bot, mock_api):
        """Test detection of closed positions (zombie detection)"""
        # Bot has a position
        mock_position = Mock()
        mock_position.entry_time = datetime.now(IST) - timedelta(hours=1)
        mock_position.entry_price = 250.0
        mock_position.entry_underlying_price = 25000
        mock_position.option_symbol = "NIFTY26FEB25000CE"
        mock_bot.positions = {"NIFTY50": mock_position}

        # Broker has no positions
        mock_api.get_positions = Mock(return_value={})
        mock_api.get_net_positions = Mock(return_value=[])

        result = sync_positions_from_broker(mock_bot, mock_api)

        # Should call exit_trade for closed position
        mock_bot.exit_trade.assert_called_once()

    def test_sync_respects_grace_period(self, mock_bot, mock_api):
        """Test that grace period prevents removing recently opened positions"""
        # Bot has a position opened 30 seconds ago (within 120s grace period)
        mock_position = Mock()
        mock_position.entry_time = datetime.now(IST) - timedelta(seconds=30)
        mock_position.entry_price = 250.0
        mock_position.entry_underlying_price = 25000
        mock_position.option_symbol = "NIFTY26FEB25000CE"
        mock_bot.positions = {"NIFTY50": mock_position}

        # Broker has no positions yet
        mock_api.get_positions = Mock(return_value={})
        mock_api.get_net_positions = Mock(return_value=[])

        result = sync_positions_from_broker(mock_bot, mock_api)

        # Should NOT call exit_trade (grace period protection)
        mock_bot.exit_trade.assert_not_called()
        # Position should still exist
        assert "NIFTY50" in mock_bot.positions

    def test_sync_updates_existing_position(self, mock_bot, mock_api):
        """Test updating quantities for existing positions"""
        # Bot already tracking NIFTY50
        mock_position = Mock()
        mock_position.lot_size = 1
        mock_position.option_symbol = "NIFTY26FEB25000CE"
        mock_position.strike_price = 25000
        mock_bot.positions = {"NIFTY50": mock_position}

        # Broker has the same position
        broker_positions = {
            ("NIFTY26FEB25000CE", "NFO"): {
                "qty": 2,  # Different quantity
                "price": 250.0,
                "ltp": 255.0
            }
        }
        mock_api.get_positions = Mock(return_value=broker_positions)
        mock_api.get_net_positions = Mock(return_value=[])

        with patch("src.symbol_master.SymbolMaster") as MockSymbolMaster:
            mock_sm = Mock()
            mock_sm.get_symbol = Mock(return_value="NIFTY26FEB25000CE")
            MockSymbolMaster.return_value = mock_sm

            result = sync_positions_from_broker(mock_bot, mock_api)

            # Should update quantity
            assert mock_position.lot_size == 2
            # Should not call enter_trade (position already exists)
            mock_bot.enter_trade.assert_not_called()

    def test_sync_handles_symbol_parsing_failure(self, mock_bot, mock_api):
        """Test handling of symbol parsing failures"""
        # Broker has a position with invalid symbol
        broker_positions = {
            ("INVALID_SYMBOL", "NFO"): {
                "qty": 1,
                "price": 250.0,
                "ltp": 255.0
            }
        }
        mock_api.get_positions = Mock(return_value=broker_positions)
        mock_api.get_net_positions = Mock(return_value=[])

        result = sync_positions_from_broker(mock_bot, mock_api)

        # Should skip invalid symbol
        assert result == 0
        mock_bot.enter_trade.assert_not_called()

    def test_sync_calls_daily_pnl_sync(self, mock_bot, mock_api):
        """Test that daily P&L is synced after position reconciliation"""
        mock_api.get_positions = Mock(return_value={})
        mock_api.get_net_positions = Mock(return_value=[])

        sync_positions_from_broker(mock_bot, mock_api)

        # Should call sync_daily_pnl
        mock_bot.sync_daily_pnl.assert_called_once_with(mock_api)

    def test_sync_handles_multiple_positions(self, mock_bot, mock_api):
        """Test syncing multiple positions from broker"""
        broker_positions = {
            ("NIFTY26FEB25000CE", "NFO"): {"qty": 1, "price": 250.0},
            ("BANKNIFTY26FEB45000PE", "NFO"): {"qty": 2, "price": 150.0},
        }
        mock_api.get_positions = Mock(return_value=broker_positions)
        mock_api.get_net_positions = Mock(return_value=[])

        with patch("src.symbol_master.SymbolMaster") as MockSymbolMaster:
            mock_sm = Mock()
            mock_sm.get_symbol = Mock(side_effect=[
                "NIFTY26FEB25000CE",
                "BANKNIFTY26FEB45000PE"
            ])
            MockSymbolMaster.return_value = mock_sm

            result = sync_positions_from_broker(mock_bot, mock_api)

            # Should import 2 positions
            assert result == 2
            assert mock_bot.enter_trade.call_count == 2

    def test_sync_exit_with_zero_premium_fallback(self, mock_bot, mock_api):
        """Test that exit uses entry price if LTP is zero"""
        # Bot has a position
        mock_position = Mock()
        mock_position.entry_time = datetime.now(IST) - timedelta(hours=1)
        mock_position.entry_price = 250.0
        mock_position.entry_underlying_price = 25000
        mock_position.option_symbol = "NIFTY26FEB25000CE"
        mock_bot.positions = {"NIFTY50": mock_position}

        # Broker has no positions
        mock_api.get_positions = Mock(return_value={})
        mock_api.get_net_positions = Mock(return_value=[])

        # Quote returns zero price
        mock_api.get_quote = Mock(return_value={"last_price": 0})

        sync_positions_from_broker(mock_bot, mock_api)

        # Should use entry price as fallback
        mock_bot.exit_trade.assert_called_once()
        call_args = mock_bot.exit_trade.call_args
        assert call_args[1]["exit_price"] == 250.0  # entry_price fallback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
