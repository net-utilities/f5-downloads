import requests
class SlackReport:
    def __init__(self, webhook):
        self.webhook = webhook
        self.updated = []
        self.failed = []
        self.up_to_date = []

    def send_webhook(self):

        payload = {
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
                }
            ]
        }

        if len(self.updated):
            updated = '\n'.join(self.updated)

            payload['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:white_check_mark: Updated devices*\n\n {updated}"
                }
            })

        if len(self.up_to_date):
            up_to_date = '\n'.join(self.up_to_date)

            payload['blocks'].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*:ballot_box_with_check: Devices already running the latest version*\n\n {up_to_date}"
                    }
                })

        if len(self.failed):
            failed = '\n'.join(self.failed)
            payload['blocks'].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*:warning: Failed devices*\n\n {failed}"
                }
            })

        requests.post(self.webhook, json=payload)
