import requests, os, re

class F5rest:
    def __init__(self, username, password, device, verify_ssl=True):
        self.device = device
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self._token = None

    @property
    def token(self):
        if not self._token:
            body = {
                'username': self.username,
                'password': self.password,
                'loginProviderName': 'tmos'
            }

            token_response = requests.post(
                f'https://{self.device}/mgmt/shared/authn/login',
                verify=self.verify_ssl,
                auth=(self.username, self.password),json=body)\
                .json()

            self._token = token_response['token']['token']
        return self._token

    def upload_file(self, file_path):

        headers = {
            'Content-Type': 'application/octet-stream',
            'X-F5-Auth-Token': self.token
        }

        chunk_size=512*1024
        file_obj = open(file_path, 'rb')
        file_name = os.path.basename(file_path)
        size = os.path.getsize(file_path)
        end_point = 'https://' + self.device + '/mgmt/shared/file-transfer/uploads/' + file_name

        start = 0

        while True:
            file_slice = file_obj.read(chunk_size)
            if not file_slice:
                break

            current_bytes = len(file_slice)
            if current_bytes < chunk_size:
                end = size
            else:
                end = start + current_bytes

            content_range = f'{start}-{end-1}/{size}'
            headers['Content-Range'] = content_range
            response = requests.post(end_point,
                          data=file_slice,
                          headers=headers,
                          verify=self.verify_ssl)
            start += current_bytes

    def run_bash_command(self, command):

        headers = {
            'X-F5-Auth-Token': self.token
        }

        payload = {
            'command': 'run',
            'utilCmdArgs': f"-c '{command}'"
        }

        response = requests.post('https://' + self.device + '/mgmt/tm/util/bash', json=payload, verify=self.verify_ssl, headers=headers).json()
        if 'commandResult' in response:
            print(response['commandResult'])
            return re.sub('\n$', '', response['commandResult'])
        else:
            return None

    def test_file(self, file_path):
        return self.run_bash_command(f'[ -f "{file_path}" ] && echo 1 || echo 0') == '1';

    def update_geoip_database(self, file_path):
        if True or not self.test_file('/var/tmp/update_geoipdb.sh'):
            self.upload_file('./update_geoipdb.sh')
            self.run_bash_command('mv /var/config/rest/downloads/update_geoipdb.sh /var/tmp/')

        self.upload_file(file_path)
        self.upload_file(f'{file_path}.md5')
        file_name = os.path.basename(file_path)
        self.run_bash_command(f'bash /var/tmp/update_geoipdb.sh {file_name}')
