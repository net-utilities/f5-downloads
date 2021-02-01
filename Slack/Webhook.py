import requests
class SlackReport:
    def __init__(self, webhook):
        self.webhook = webhook
        self.updated = []
        self.failed = []
        self.up_to_date = []

    def send_webhook(self):
        updated = '\n'.join(self.updated)
        failed = '\n'.join(self.failed)
        up_to_date = '\n'.join(self.up_to_date)

        requests.post(self.webhook, json={
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "A report from the GeoIP database update script"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*:white_check_mark: Updated devices*\n\n {updated}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*:ballot_box_with_check: Devices already running the latest version*\n\n {up_to_date}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*:warning: Failed devices*\n\n {failed}"
                    }
                }
            ]
        })
