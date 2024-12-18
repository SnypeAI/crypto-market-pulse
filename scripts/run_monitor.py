import asyncio
import os
from src.realtime.market_monitor import MarketMonitor
from discord_webhook import DiscordWebhook
from telegram import Bot

async def send_alert(alert):
    # Discord notification
    if webhook_url := os.getenv('DISCORD_WEBHOOK'):
        webhook = DiscordWebhook(
            url=webhook_url,
            content=f"🚨 Alert: {alert['type']} for {alert['symbol']} at {alert['price']}"
        )
        webhook.execute()
    
    # Telegram notification
    if (token := os.getenv('TELEGRAM_TOKEN')) and (chat_id := os.getenv('TELEGRAM_CHAT_ID')):
        bot = Bot(token=token)
        await bot.send_message(
            chat_id=chat_id,
            text=f"🚨 Alert: {alert['type']} for {alert['symbol']} at {alert['price']}"
        )

async def main():
    # Initialize market monitor with top cryptocurrencies
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']
    monitor = MarketMonitor(symbols)
    
    try:
        # Start monitoring
        print(f"Starting market monitor for {', '.join(symbols)}")
        
        # Add alert handler
        async def alert_handler(alert):
            print(f"Alert triggered: {alert}")
            await send_alert(alert)
        
        monitor.on_alert = alert_handler
        
        # Run for specified duration or until interrupted
        await monitor.start_monitoring()
        
    except KeyboardInterrupt:
        print("Stopping market monitor...")
        await monitor.stop_monitoring()
    except Exception as e:
        print(f"Error in market monitor: {str(e)}")
        raise

if __name__ == '__main__':
    asyncio.run(main())