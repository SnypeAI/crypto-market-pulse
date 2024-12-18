import pytest
from datetime import datetime
from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.alert_system import ModelAlertSystem

@pytest.fixture
def metrics_collector():
    return MetricsCollector()

@pytest.fixture
def alert_system():
    return ModelAlertSystem()

@pytest.fixture
def sample_prediction():
    return {
        'price': 42000.0,
        'confidence': 0.85,
        'model_version': '1.0.0'
    }

@pytest.fixture
def sample_predictions():
    return [
        {'actual': 42000, 'predicted': 41000},
        {'actual': 42500, 'predicted': 42000},
        {'actual': 43000, 'predicted': 43500}
    ]

def test_record_prediction(metrics_collector, sample_prediction):
    metrics_collector.record_prediction('BTC', sample_prediction)
    
    assert len(metrics_collector.metrics['predictions']) == 1
    recorded = metrics_collector.metrics['predictions'][0]
    assert recorded['symbol'] == 'BTC'
    assert recorded['predicted'] == sample_prediction['price']
    assert recorded['confidence'] == sample_prediction['confidence']

def test_update_accuracy(metrics_collector):
    metrics_collector.update_accuracy('BTC', actual=42000, predicted=41000)
    
    assert 'BTC' in metrics_collector.metrics['accuracy']
    assert len(metrics_collector.metrics['accuracy']['BTC']) == 1
    
    accuracy = metrics_collector.metrics['accuracy']['BTC'][0]
    assert 'error' in accuracy
    assert 'actual' in accuracy
    assert 'predicted' in accuracy

def test_check_model_drift(metrics_collector, sample_predictions):
    drift_detected = metrics_collector.check_model_drift('BTC', sample_predictions)
    
    assert isinstance(drift_detected, bool)
    assert 'BTC' in metrics_collector.metrics['model_drift']
    drift_data = metrics_collector.metrics['model_drift']['BTC']
    assert 'average_error' in drift_data
    assert 'drift_detected' in drift_data

def test_get_model_performance(metrics_collector):
    # Add some test data
    metrics_collector.update_accuracy('BTC', actual=42000, predicted=41000)
    metrics_collector.update_accuracy('BTC', actual=42500, predicted=42000)
    
    performance = metrics_collector.get_model_performance('BTC')
    
    assert 'current_accuracy' in performance
    assert 'error_std' in performance
    assert 'min_error' in performance
    assert 'max_error' in performance
    assert 'predictions_count' in performance

def test_alert_system_accuracy(alert_system):
    alert_fired = alert_system.check_accuracy('BTC', accuracy=0.94)
    assert alert_fired == True
    
    alert_fired = alert_system.check_accuracy('BTC', accuracy=0.96)
    assert alert_fired == False

def test_alert_system_drift(alert_system):
    alert_fired = alert_system.check_drift('BTC', drift=0.06)
    assert alert_fired == True
    
    alert_fired = alert_system.check_drift('BTC', drift=0.04)
    assert alert_fired == False

def test_alert_system_confidence(alert_system, sample_prediction):
    # Test low confidence
    low_confidence = sample_prediction.copy()
    low_confidence['confidence'] = 0.7
    alert_fired = alert_system.check_confidence('BTC', low_confidence)
    assert alert_fired == True
    
    # Test acceptable confidence
    alert_fired = alert_system.check_confidence('BTC', sample_prediction)
    assert alert_fired == False

def test_get_active_alerts(alert_system):
    # Create some test alerts
    alert_system.create_alert('BTC', 'ACCURACY', 'Test alert 1')
    alert_system.create_alert('ETH', 'DRIFT', 'Test alert 2')
    
    active_alerts = alert_system.get_active_alerts()
    
    assert len(active_alerts) == 2
    assert active_alerts[0]['type'] == 'ACCURACY'
    assert active_alerts[1]['type'] == 'DRIFT'