# This is a sample configuration
# Look here for an explanation
# https://github.com/net-utilities/f5-downloads

config = {
    'f5_downloads': {
        'username': 'user@domain.com',
        'password': 'password',
    },
    'device_credentials': {
        'username': 'user',
        'password': 'password',
    },
    'bigipreport_url': 'https://bigipreport.company.com',
    'skip_bigipreport_device_groups': [
        'LD-LB',
    ],
    'explicit_devices': [
        'my-manual-lb.company.com'
    ],
    'slackWebHook': 'https://hooks.slack.com/services/...'
}