from f5downloads import F5Downloads, F5rest
import requests
from Slack.Webhook import SlackReport
from config import *

if config['slackWebHook']:
    slack = SlackReport(config['slackWebHook'])
else:
    slack = None

downloads = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])
new_geoip_file = downloads.download_geoipdb(16)

devices = []

# If you're running bigipreport (https://loadbalancing.se/bigipreport-rest/)
# you can source your devices from bigipreport
# Else just leave that option empty and it'll skill this section
if config['bigipreport_url']:
    device_groups = requests.get(f'{config["bigipreport_url"]}/json/devicegroups.json').json()
    for device_group in [ dg for dg in device_groups if dg['name'] not in config['skip_bigipreport_device_groups'] ]:
        devices.extend(device_group['ips'])

devices.extend(config['explicit_devices'])

if new_geoip_file:
    for device in devices:
        try:
            f5rest = F5rest(config['device_credentials']['username'], config['device_credentials']['password'],
                            device, False)
            if f5rest.update_geoip_db(new_geoip_file):
                if slack: slack.updated.append(device)
            else:
                if slack: slack.up_to_date.append(device)
        except Exception as e:
            if slack:
                slack.failed.append(f'{device} - {e}')
            else:
                print(f'{device} - {e}')

if slack and len(slack.failed) or len(slack.updated):
    slack.send_webhook()
