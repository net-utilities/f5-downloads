# Automate F5 downloads
The primary reason for this repository was to update GeoIP databases automatically but it was expanded to make it easy
to download things and keep a local repository of F5 software.

## Usage

1. Copy `rename_to_config.py` to `config.py` and populate it with credentials and optionally your devices
(if you want to) update the geoip databases too.
2. Example for downloading things
   ```python3
   d = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])
   
   # Download the latest v16 version
   d.download_latest_version(16)
   
   # Download the latest GeoIP database
   d.download_geoipdb(16)
   ``` 
   
   Your downloads will be save in a sub directory called downloads and grouped by version.
   
   I'm aware of that these are not version specific but if by any chance
   F5 decides to make it so at least the script is prepared for it.
   
## Hooks
The download functions supports callback functions to trigger ie. Slack reports or uploads of the databases.
To use them you simply need to supply a function as a second parameter.

```python3
def my_func(file_path):
    print(f'Downloaded {file_path}')

d = F5Downloads(config['f5_downloads']['username'], config['f5_downloads']['password'])

# Download the latest GeoIP database and run the my_func in case the download was successful
d.download_geoipdb(16, my_func)
```

## Full example
Check out `main.py` for a full example that both downloads and updates the geoip database on all devices.

### How it works
1. Login downloads.f5.com and download the latest geoip database, if needed
2. For each device it gets a token
3. Validate that the existing database on the device matches the latest version at downloads.f5.com
4. If it does, the script exists, if it does not it will move on to the next step
5. Validate that the update shell script [./update_geoip.sh](./update_geoip.sh) exists in `/var/tmp/`. Upload it if it does not.
6. Run the update script and update the geoip database
7. Validate that the databases now matches the latest version
8. Send a slack report with what was done to the configured webhook