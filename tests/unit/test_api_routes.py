"""Tests for API routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.main import app


class TestHealthRoutes:
    """Tests for health check routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "online"

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestPredictionRoutes:
    """Tests for prediction routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_get_prediction_valid_us_symbol(self, client):
        """Test prediction with valid US stock symbol."""
        response = client.get("/api/v1/predictions/AAPL")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "current_price" in data
        assert "predicted_price" in data
        assert "confidence" in data
        assert "timestamp" in data

    def test_get_prediction_valid_vn_symbol(self, client):
        """Test prediction with valid Vietnamese stock symbol."""
        response = client.get("/api/v1/predictions/VCB.VN")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "VCB.VN"

    def test_get_prediction_lowercase_symbol(self, client):
        """Test prediction with lowercase symbol (should be converted)."""
        response = client.get("/api/v1/predictions/aapl")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"

    def test_get_prediction_invalid_symbol_format(self, client):
        """Test prediction with invalid symbol format."""
        response = client.get("/api/v1/predictions/INVALID123")

        assert response.status_code == 400
        data = response.json()
        assert "Invalid symbol format" in data["detail"]

    def test_get_prediction_too_long_symbol(self, client):
        """Test prediction with too long symbol."""
        response = client.get("/api/v1/predictions/TOOLONG")

        assert response.status_code == 400

    def test_get_prediction_empty_symbol(self, client):
        """Test prediction with empty symbol."""
        response = client.get("/api/v1/predictions/")

        # Should return 404 (no route match) or 400
        assert response.status_code in [404, 400]

    def test_get_signal_valid_symbol(self, client):
        """Test signal generation with valid symbol."""
        response = client.get("/api/v1/signals/AAPL")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "signal" in data
        assert "strength" in data
        assert "target_price" in data
        assert "stop_loss" in data
        assert "take_profit" in data

    def test_get_signal_vietnamese_symbol(self, client):
        """Test signal generation with Vietnamese symbol."""
        response = client.get("/api/v1/signals/FPT.VN")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "FPT.VN"

    def test_get_signal_invalid_symbol(self, client):
        """Test signal generation with invalid symbol."""
        response = client.get("/api/v1/signals/INVALID@")

        assert response.status_code == 400


class TestTrainingRoutes:
    """Tests for training routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @patch("src.api.routes.training.retraining_service")
    def test_train_model_success(self, mock_service, client):
        """Test successful model training."""
        # Mock successful training response
        mock_service.retrain_model.return_value = {
            "status": "success",
            "symbol": "AAPL",
            "trigger": "manual",
            "models_trained": ["lstm", "gru"],
            "data_points": 1000,
            "error": None,
            "timestamp": "2024-01-01T00:00:00"
        }

        response = client.post("/api/v1/training/train", json={
            "symbol": "AAPL",
            "models": "all",
            "fetch_new_data": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["symbol"] == "AAPL"
        assert data["trigger"] == "manual"

    @patch("src.api.routes.training.retraining_service")
    def test_train_model_specific_models(self, mock_service, client):
        """Test training specific models."""
        mock_service.retrain_model.return_value = {
            "status": "success",
            "symbol": "AAPL",
            "trigger": "manual",
            "models_trained": ["lstm"],
            "data_points": 1000,
            "error": None,
            "timestamp": "2024-01-01T00:00:00"
        }

        response = client.post("/api/v1/training/train", json={
            "symbol": "AAPL",
            "models": "lstm",
            "fetch_new_data": False
        })

        assert response.status_code == 200

    @patch("src.api.routes.training.retraining_service")
    def test_batch_train_models(self, mock_service, client):
        """Test batch training multiple symbols."""
        mock_service.retrain_multiple.return_value = [
            {"status": "success", "symbol": "AAPL"},
            {"status": "success", "symbol": "MSFT"},
        ]

        response = client.post("/api/v1/training/batch-train", json={
            "symbols": ["AAPL", "MSFT"],
            "models": "all",
            "fetch_new_data": True
        })

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert data["successful"] == 2
        assert data["failed"] == 0

    @patch("src.api.routes.training.retraining_service")
    def test_get_training_history(self, mock_service, client):
        """Test getting training history."""
        mock_service.get_training_history.return_value = [
            {"timestamp": "2024-01-01", "status": "success"},
            {"timestamp": "2024-01-02", "status": "success"},
        ]

        response = client.get("/api/v1/training/history/AAPL?limit=50")

        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "AAPL"
        assert "history" in data
        assert data["total"] == 2

    @patch("src.api.routes.training.retraining_service")
    def test_get_training_stats(self, mock_service, client):
        """Test getting training statistics."""
        mock_service.get_training_stats.return_value = {
            "total_trainings": 10,
            "successful": 9,
            "failed": 1
        }

        response = client.get("/api/v1/training/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_trainings" in data


class TestMonitoringRoutes:
    """Tests for monitoring routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_monitoring_health(self, client):
        """Test monitoring health endpoint."""
        response = client.get("/api/v1/monitoring/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "models_loaded" in data
        assert "data_updated" in data

    @patch("src.api.routes.monitoring.market_monitor")
    def test_check_market_us(self, mock_monitor, client):
        """Test market check for US market."""
        mock_monitor.check_market_drop_event.return_value = {
            "event_detected": False,
            "market": "us",
            "drop_percentage": 0.0,
            "threshold": 5.0,
            "should_retrain": False,
            "market_data": {}
        }

        response = client.get("/api/v1/market/check/us?threshold=5.0&lookback_days=5")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "us"
        assert "event_detected" in data

    @patch("src.api.routes.monitoring.market_monitor")
    def test_check_market_vietnam(self, mock_monitor, client):
        """Test market check for Vietnamese market."""
        mock_monitor.check_market_drop_event.return_value = {
            "event_detected": True,
            "market": "vietnam",
            "drop_percentage": 6.5,
            "threshold": 5.0,
            "should_retrain": True,
            "market_data": {}
        }

        response = client.get("/api/v1/market/check/vietnam")

        assert response.status_code == 200
        data = response.json()
        assert data["market"] == "vietnam"
        assert data["event_detected"] is True

    @patch("src.api.routes.monitoring.market_monitor")
    def test_get_market_events(self, mock_monitor, client):
        """Test getting market events."""
        mock_monitor.get_market_events.return_value = [
            {"timestamp": "2024-01-01", "market": "us", "drop": 5.5},
            {"timestamp": "2024-01-02", "market": "vietnam", "drop": 6.0},
        ]

        response = client.get("/api/v1/market/events?limit=50")

        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert data["total"] == 2

    @patch("src.api.routes.monitoring.market_monitor")
    def test_get_market_events_filtered(self, mock_monitor, client):
        """Test getting market events filtered by market."""
        mock_monitor.get_market_events.return_value = [
            {"timestamp": "2024-01-01", "market": "us", "drop": 5.5},
        ]

        response = client.get("/api/v1/market/events?market=us&limit=50")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1


class TestSchedulerRoutes:
    """Tests for scheduler routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @patch("src.api.routes.scheduler.scheduler_service")
    def test_get_scheduler_status(self, mock_scheduler, client):
        """Test getting scheduler status."""
        mock_scheduler.get_status.return_value = {
            "running": True,
            "jobs": [],
            "next_run_time": "2024-01-01T00:00:00"
        }

        response = client.get("/api/v1/scheduler/status")

        assert response.status_code == 200
        data = response.json()
        assert "running" in data

    def test_get_scheduler_status_not_initialized(self, client):
        """Test scheduler status when not initialized."""
        # This tests the actual app where scheduler might not be initialized
        response = client.get("/api/v1/scheduler/status")

        assert response.status_code == 200
        data = response.json()
        # Should return status even if not initialized
        assert "running" in data or "message" in data

    @patch("src.api.routes.scheduler.scheduler_service")
    def test_start_scheduler(self, mock_scheduler, client):
        """Test starting scheduler."""
        mock_scheduler.start.return_value = None

        response = client.post("/api/v1/scheduler/start")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch("src.api.routes.scheduler.scheduler_service")
    def test_stop_scheduler(self, mock_scheduler, client):
        """Test stopping scheduler."""
        mock_scheduler.stop.return_value = None

        response = client.post("/api/v1/scheduler/stop")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch("src.api.routes.scheduler.scheduler_service")
    def test_trigger_retraining(self, mock_scheduler, client):
        """Test triggering scheduled retraining."""
        mock_scheduler.trigger_scheduled_retraining_now.return_value = None

        response = client.post("/api/v1/scheduler/trigger-retraining")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @patch("src.api.routes.scheduler.scheduler_service")
    def test_trigger_market_check(self, mock_scheduler, client):
        """Test triggering market check."""
        mock_scheduler.trigger_market_check_now.return_value = None

        response = client.post("/api/v1/scheduler/trigger-market-check")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestSymbolValidation:
    """Tests for symbol validation function."""

    def test_valid_us_symbols(self):
        """Test validation of valid US symbols."""
        from src.api.routes.predictions import validate_symbol

        assert validate_symbol("AAPL") == "AAPL"
        assert validate_symbol("aapl") == "AAPL"
        assert validate_symbol("MSFT") == "MSFT"
        assert validate_symbol("GOOGL") == "GOOGL"
        assert validate_symbol("A") == "A"

    def test_valid_vietnamese_symbols(self):
        """Test validation of valid Vietnamese symbols."""
        from src.api.routes.predictions import validate_symbol

        assert validate_symbol("VCB.VN") == "VCB.VN"
        assert validate_symbol("vcb.vn") == "VCB.VN"
        assert validate_symbol("FPT.VN") == "FPT.VN"

    def test_invalid_symbols(self):
        """Test validation of invalid symbols."""
        from src.api.routes.predictions import validate_symbol

        with pytest.raises(ValueError, match="Invalid symbol format"):
            validate_symbol("TOOLONG")  # 7 letters

        with pytest.raises(ValueError, match="Invalid symbol format"):
            validate_symbol("ABC123")  # Contains numbers

        with pytest.raises(ValueError, match="Invalid symbol format"):
            validate_symbol("ABC@")  # Contains special char

        with pytest.raises(ValueError, match="Invalid symbol format"):
            validate_symbol("")  # Empty

    def test_symbol_whitespace_handling(self):
        """Test that validation handles whitespace."""
        from src.api.routes.predictions import validate_symbol

        assert validate_symbol(" AAPL ") == "AAPL"
        assert validate_symbol("  MSFT  ") == "MSFT"
