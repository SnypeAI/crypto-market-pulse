from datetime import datetime

import pytest


@pytest.fixture
def sample_market_data():
    return {
        "BTC": {
            "prices": [40000, 41000, 40500, 42000],
            "volume": 1000000,
            "sentiment": 0.65,
        },
        "ETH": {
            "prices": [2800, 2850, 2900, 3000],
            "volume": 500000,
            "sentiment": 0.72,
        },
    }


@pytest.fixture
def mock_api_response():
    return {
        "status": "success",
        "data": sample_market_data(),
        "timestamp": datetime.now().isoformat(),
    }
