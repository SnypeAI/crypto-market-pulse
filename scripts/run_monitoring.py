import os
import json
from datetime import datetime
from pathlib import Path
from src.monitoring.metrics_collector import MetricsCollector
from src.monitoring.alert_system import ModelAlertSystem
from discord_webhook import DiscordWebhook
from telegram import Bot

async def send_alert(alert):
    # Discord notification
    if webhook_url := os.getenv('DISCORD_WEBHOOK'):
        webhook = DiscordWebhook(
            url=webhook_url,
            content=f"🚨 Model Alert: {alert['type']} for {alert['symbol']}\n{alert['message']}"
        )
        webhook.execute()
    
    # Telegram notification
    if (token := os.getenv('TELEGRAM_TOKEN')) and (chat_id := os.getenv('TELEGRAM_CHAT_ID')):
        bot = Bot(token=token)
        await bot.send_message(
            chat_id=chat_id,
            text=f"🚨 Model Alert: {alert['type']} for {alert['symbol']}\n{alert['message']}"
        )

def load_recent_predictions(symbol):
    predictions_dir = Path('data/predictions')
    files = sorted(predictions_dir.glob(f'{symbol}_*.json'))[-10:]  # Last 10 files
    
    predictions = []
    for file in files:
        with open(file, 'r') as f:
            predictions.extend(json.load(f))
    
    return predictions

def main():
    metrics = MetricsCollector()
    alerts = ModelAlertSystem()
    symbols = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP']
    
    for symbol in symbols:
        print(f'Monitoring {symbol} model performance...')
        
        # Load recent predictions
        predictions = load_recent_predictions(symbol)
        
        # Check model drift
        if metrics.check_model_drift(symbol, predictions):
            drift_data = metrics.metrics['model_drift'][symbol]
            alerts.check_drift(symbol, drift_data['average_error'])
        
        # Check accuracy
        performance = metrics.get_model_performance(symbol)
        if 'current_accuracy' in performance:
            alerts.check_accuracy(symbol, performance['current_accuracy'])
        
        # Save metrics
        metrics.save_metrics()
    
    # Handle alerts
    active_alerts = alerts.get_active_alerts()
    if active_alerts:
        print(f'Found {len(active_alerts)} active alerts')
        for alert in active_alerts:
            await send_alert(alert)
    
    alerts.save_alerts()

if __name__ == '__main__':
    main()