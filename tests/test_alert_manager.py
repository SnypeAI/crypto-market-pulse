import pytest
import asyncio
from datetime import datetime
from src.realtime.alert_manager import AlertManager

@pytest.fixture
def alert_manager():
    return AlertManager()

@pytest.fixture
def sample_data():
    return {
        'price': 42000.0,
        'volume': 100.0,
        'timestamp': datetime.now().timestamp()
    }

@pytest.mark.asyncio
async def test_add_handler(alert_manager):
    async def test_handler(alert):
        pass
    
    alert_manager.add_handler(test_handler)
    assert len(alert_manager.handlers) == 1

@pytest.mark.asyncio
async def test_price_spike_alert(alert_manager, sample_data):
    alerts_received = []
    
    async def test_handler(alert):
        alerts_received.append(alert)
    
    alert_manager.add_handler(test_handler)
    
    # Simulate price spike
    base_price = sample_data['price']
    spike_data = sample_data.copy()
    spike_data['price'] = base_price * 1.03  # 3% spike
    
    await alert_manager.check_conditions('BTCUSDT', spike_data)
    
    assert len(alerts_received) == 1
    assert alerts_received[0]['type'] == 'PRICE_SPIKE'

@pytest.mark.asyncio
async def test_volume_spike_alert(alert_manager, sample_data):
    alerts_received = []
    
    async def test_handler(alert):
        alerts_received.append(alert)
    
    alert_manager.add_handler(test_handler)
    
    # Simulate volume spike
    base_volume = sample_data['volume']
    spike_data = sample_data.copy()
    spike_data['volume'] = base_volume * 4  # 4x volume spike
    
    await alert_manager.check_conditions('BTCUSDT', spike_data)
    
    assert len(alerts_received) == 1
    assert alerts_received[0]['type'] == 'VOLUME_SPIKE'

@pytest.mark.asyncio
async def test_multiple_alerts(alert_manager, sample_data):
    alerts_received = []
    
    async def test_handler(alert):
        alerts_received.append(alert)
    
    alert_manager.add_handler(test_handler)
    
    # Simulate both price and volume spikes
    spike_data = sample_data.copy()
    spike_data['price'] = sample_data['price'] * 1.03
    spike_data['volume'] = sample_data['volume'] * 4
    
    await alert_manager.check_conditions('BTCUSDT', spike_data)
    
    assert len(alerts_received) == 2
    alert_types = {alert['type'] for alert in alerts_received}
    assert 'PRICE_SPIKE' in alert_types
    assert 'VOLUME_SPIKE' in alert_types

@pytest.mark.asyncio
async def test_handler_error_handling(alert_manager, sample_data):
    async def failing_handler(alert):
        raise Exception("Test error")
    
    alert_manager.add_handler(failing_handler)
    
    # Should not raise exception
    await alert_manager.check_conditions('BTCUSDT', sample_data)