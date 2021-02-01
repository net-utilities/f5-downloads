from f5downloads import F5Downloads, F5rest

from Slack.Webhook import SlackReport
from config import *

slack = SlackReport(config['slackWebHook'])
downloads = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])
new_geoip_file = downloads.download_geoipdb(16)

if new_geoip_file:
    for device in config['devices']:
        try:
            f5rest = F5rest(config['device_credentials']['username'], config['device_credentials']['password'],
                            device, False)
            if f5rest.update_geoip_db(new_geoip_file):
                slack.updated.append(device)
            else:
                slack.up_to_date.append(device)
        except Exception as e:
            slack.failed.append(f'{device} - {e}')

slack.send_webhook()
