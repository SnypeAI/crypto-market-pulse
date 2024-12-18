class AlertNotifier:
    def __init__(self):
        self.channels = ['telegram', 'discord', 'email']

    def send_alerts(self, alerts):
        for alert in alerts:
            for channel in self.channels:
                self.send_to_channel(channel, alert)

    def send_to_channel(self, channel, alert):
        # Implement channel-specific sending
        pass