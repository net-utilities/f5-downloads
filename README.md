# Automate F5 downloads
Make it easy to download things and keep a local repository of F5 software.

## Usage

1. Copy `rename_to_config.py` to `config.py` and populate it with credentials.
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