# Automate F5 downloads
The primary reason for this repository was to update GeoIP databases automatically but it was expanded to make it easy
to download things and keep a local repository of F5 software.

#### Disclaimer
While I've tested this in my own environments I should add that like with all free software you're running this on your
own risk.

#### Not happy about something? 
Leave an [issue](https://github.com/net-utilities/f5-downloads/issues), or better yet, a Pull Request. 
You can also try your luck at our [Discord channel](https://discord.gg/Q2c3UhpJ).

# Configuration

| Option                         | Description                                                                                                                                                              | Optional | Sample value                                |
|--------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|---------------------------------------------|
| f5_downloads.username          | This is the mail address you use at https://downloads.f5.com.                                                                                                            | No       | `myemail@company.com`                       |
| f5_downloads.password          | The password used to login to https://downloads.f5.com.                                                                                                                  | No       | `***********` :)                            |
| device_credentials.username    | The username used to login to the F5 devices. Admin permissions required if updating GeoIP databases.                                                                    | No*     | `john`                                      |
| device_credentials.password    | The password used to login to the F5 devices.                                                                                                                            | No*     | ********** :)                               |
| bigipreport_url                | If you're using [BigIPReport](https://loadbalancing.se/bigipreport-rest/) you can use it as a source for your device list.                                               | Yes      | `https://bigipreport.company.com`           |
| skip_bigipreport_device_groups | If you're using BigIPreport [BigIPReport](https://loadbalancing.se/bigipreport-rest/) you can skip specific device groups by adding their device group name to this list | Yes      | `['LD-LB']`                                 |
| explicit_devices               | Add your devices to this array if you're **not** using BigIPReport or want to explicitly add something that is not in BigIPReport.                                       | No*     | `['my-manual-lb.company.com']`              |
| slackWebHook                   | If you want reports on Slack when the job has finished, just add a Webhook URL here.                                                                                     | Yes      | `https://hooks.slack.com/services/AABBCCDD` |

`* The things mentioned as mandatory configuration is only mandatory if you want to update the GeoIP databases using
main.py`

### A note about the device list

#### If you're using BigIPReport as source
The script will take the device groups in BigIPReport, remove the device groups matching names in `explicit_devices` and
then finally add the devices that is added to `explicit_devices`.

#### If you're not using BigIPReport
Simply leave `bigipreport_url` and `skip_bigipreport_device_groups` as `None` or and empty string and add all your
device IPs/DNSs manually to `explicit_devices`.

# Running the script
When you have configured the script you can run `main.py` to start it. Schedule it according to your liking using a
Cronjob or Scheduled tasks.

## How it works
1. Login downloads.f5.com and download the latest geoip database, if needed
2. Generates a device list according to the logic above and then for each device it gets a token and does the following
   steps
3. Validate that the existing database on the device matches the latest version at downloads.f5.com
4. If it does, the script exists, if it does not it will move on to the next step
5. Validate that the update shell script [./update_geoip.sh](./update_geoip.sh) exists in `/var/tmp/`. Upload it if it does not.
6. Run the update script and update the geoip database
7. Validate that the databases now matches the latest version
8. Send a slack report if there's any updated databases or if there was an issue with a device 

## Using the packages just for downloading things and keeping a local cache of software

1. Copy `rename_to_config.py` to `config.py` and populate it with credentials and optionally your devices
2. Run the script from the root of the cloned repo
3. Example for downloading things
   ```python3
   from f5downloads import F5Downloads
   from config import *

   d = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])

   # Download the latest v16 version
   d.download_latest_version(16)

   # Download the latest GeoIP database
   d.download_geoipdb(16)
   ``` 
   
   Your downloads will be save in a sub directory called downloads and grouped by version.
   
   I'm aware of that these are not version specific but if by any chance
   F5 decides to make it so at least the script is prepared for it.
   
### Hooks
The download functions supports callback functions to trigger ie. Slack reports or uploads of the databases.
To use them you simply need to supply a function as a second parameter.

```python3
def my_func(file_path):
    print(f'Downloaded {file_path}')

d = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])

# Download the latest GeoIP database and run the my_func in case the download was successful
d.download_geoipdb(16, my_func)
```
