from f5downloads import *
from f5rest import *
from config import *

downloads = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])

new_geoip_file = downloads.download_geoipdb(16)
if new_geoip_file:
    for device in config['devices']:
        f5rest = F5rest(config['device_credentials']['username'], config['device_credentials']['password'],
                        device, False)
        f5rest.update_geoip_database(new_geoip_file)