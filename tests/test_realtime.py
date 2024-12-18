import pytest
import asyncio
from datetime import datetime
from src.realtime.data_processor import DataProcessor
from src.realtime.market_monitor import MarketMonitor

@pytest.fixture
def sample_trade_data():
    return {
        'e': 'trade',
        's': 'BTCUSDT',
        'p': '42000.50',
        'q': '0.5',
        'T': 1639925607123
    }

@pytest.fixture
def sample_orderbook_data():
    return {
        'bids': [
            ['42000.50', '1.5'],
            ['41999.50', '2.3']
        ],
        'asks': [
            ['42001.50', '1.2'],
            ['42002.50', '3.4']
        ]
    }

def test_data_processor_initialization():
    processor = DataProcessor(max_data_points=100)
    assert processor.max_data_points == 100
    assert len(processor.price_data) == 0
    assert len(processor.order_book) == 0

def test_process_trade(sample_trade_data):
    processor = DataProcessor()
    symbol = 'BTCUSDT'
    
    processor.process_trade(symbol, sample_trade_data)
    
    assert symbol in processor.price_data
    latest_price = processor.get_latest_price(symbol)
    assert latest_price == float(sample_trade_data['p'])

def test_process_orderbook(sample_orderbook_data):
    processor = DataProcessor()
    symbol = 'BTCUSDT'
    
    processor.process_order_book(symbol, sample_orderbook_data)
    
    order_book = processor.get_order_book(symbol)
    assert 'bids' in order_book
    assert 'asks' in order_book
    assert len(order_book['bids']) == 2
    assert len(order_book['asks']) == 2

@pytest.mark.asyncio
async def test_market_monitor_initialization():
    symbols = ['BTCUSDT', 'ETHUSDT']
    monitor = MarketMonitor(symbols)
    
    assert monitor.symbols == symbols
    assert isinstance(monitor.processor, DataProcessor)
    assert len(monitor.alerts) == 0

@pytest.mark.asyncio
async def test_handle_message(sample_trade_data):
    symbols = ['BTCUSDT']
    monitor = MarketMonitor(symbols)
    
    await monitor.handle_message(sample_trade_data)
    
    price = monitor.processor.get_latest_price('BTCUSDT')
    assert price == float(sample_trade_data['p'])

@pytest.mark.asyncio
async def test_alert_generation():
    symbols = ['BTCUSDT']
    monitor = MarketMonitor(symbols)
    
    # Simulate price spike
    base_price = 42000.0
    for i in range(5):
        await monitor.handle_message({
            'e': 'trade',
            's': 'BTCUSDT',
            'p': str(base_price + (i * 100)),
            'q': '1.0',
            'T': int(datetime.now().timestamp() * 1000)
        })
    
    # Trigger alert with 3% spike
    await monitor.handle_message({
        'e': 'trade',
        's': 'BTCUSDT',
        'p': str(base_price * 1.03),
        'q': '1.0',
        'T': int(datetime.now().timestamp() * 1000)
    })
    
    assert len(monitor.alerts) > 0
    assert monitor.alerts[-1]['type'] == 'PRICE_SPIKE'