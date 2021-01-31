from requests_html import HTMLSession
import re, logging, os
import pathlib
import hashlib


logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

logger.addHandler(ch)

class F5Downloads:
    def __init__(self, username, password, default_location='IRELAND'):
        self.username = username
        self.password = password
        self.default_location = default_location
        self._session = None
        self._version_pages = None
        self.new_files = []

    @property
    def session(self):
        if not self._session:
            self._session = HTMLSession()
            self._session.post('https://api-u.f5.com/auth/pub/sso/login/user',
                               headers={'Content-Type': 'application/x-www-form-urlencoded'},
                               data={
                                   'userid': self.username,
                                   'passwd': self.password,
                               }
                               )
        return self._session

    def find_links(self, page, pattern):
        return [
            (l.text, next(iter(l.absolute_links))) for l in page.html.find('a')
            if l.text and l.absolute_links and re.match(pattern, l.text)
        ]

    def follow_specific_link(self, **kwargs):
        page = kwargs['page']
        pattern= kwargs['pattern']

        matching_links = self.find_links(page, pattern)

        # To proceed in the chain we need exactly one match
        if len(matching_links) != 1:
            logging.error('Found {len(matching_links)} matches for url {url} and pattern {pattern}, unable to proceed')
            logging.error('Files found:')
            logging.error(matching_links)
            raise Exception(f'')

        name, url = matching_links[0]
        logger.debug(f'Following {name} with {url}')
        return self.get_page(url)

    def pick_latest_version(self, **kwargs):
        page = kwargs['page']
        pattern= kwargs['pattern']

        matching_links = self.find_links(page, pattern)

        if not len(matching_links):
            raise Exception(f'No versions matching {pattern} found on page {page}')

        versionDict = {}

        # This is an ugly one. Threat the versions as a decimal number and increase the worth
        # of each version number by a factor of 10, then return the sum
        for version, url in matching_links:
            number = version.replace('.', '')
            versionDict[number] = (version, url)

        # Pick the highest number
        version, url = versionDict[max(versionDict, key=int)]
        logger.debug(f'Picking {version} as latest version')

        return self.get_page(url)

    def follow_path(self, page, steps):

        step = steps.pop(0)
        f = step['f']
        args = step['args'] | { 'page': page }

        result = f(**args)

        if not len(steps):
            return result
        elif result:
            return self.follow_path(result, steps)

    # Detect if the EULA exists and circle around it
    def get_page(self, url):
        page = self.session.get(url)
        if len(page.html.find('input#accept-eula')):
            logger.debug('EULA encountered, accepting it')
            page = self.session.get(
                url.replace('https://downloads.f5.com/esd/ecc.sv', 'https://downloads.f5.com/esd/eula.sv'))
        return page

    def download_files(self, **kwargs):
        page = kwargs['page']
        pattern = kwargs['pattern']
        download_folder = kwargs['download_folder']
        cb = kwargs['cb']

        # Create folders if needed
        pathlib.Path(download_folder).mkdir(parents=True, exist_ok=True)

        matching_links = self.find_links(page, pattern)

        for name, url in matching_links:
            md5_name, md5_url = next(iter(self.find_links(page, rf'^{name}.md5$')), (None, None))

            # Only download if there's a matching md5 file
            if not md5_name:
                raise Exception(f'No matching md5 file found for {name}')

            file_path = f'{download_folder}{name}'
            md5_path = f'{download_folder}{md5_name}'
            self.download_file(md5_path, md5_url)

            if self.md5_sum_ok(md5_path, file_path):
                logger.info('The newest file already exists on disk')
                return file_path
            else:
                self.download_file(file_path, url)
                logger.info(f'Validating {name} against the supplied    md5')
                if self.md5_sum_ok(md5_path, f'{download_folder}{name}'):
                    logger.info('Downloaded file successfully')
                    if cb:
                        cb(file_path)
                    return(file_path)
                else:
                    raise Exception(f'Failed to download file {name}')

    def md5_sum_ok(self, md5_file, file):
        if not os.path.exists(md5_file):
            raise Exception(f'{md5_file} does not exist')
        if not os.path.exists(file):
            logger.info(f'{file} does not exist')
            return False
        with open(md5_file, 'r') as f:
            md5sum = re.sub(r' .+\n$', '', f.read())
        file_sum = self.md5(file)

        return md5sum == file_sum

    def md5(self, file_name):
        hash_md5 = hashlib.md5()
        with open(file_name, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def download_file(self, file_path, url):
        if os.path.exists(file_path):
            os.remove(file_path)
        page = self.get_page(url)
        name, download_url = next(iter(self.find_links(page, rf'{self.default_location}')), (None, None))
        if(download_url):
            logger.debug(f'Saving file as ./{file_path}')
            with self.session.get(download_url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)


    def download_geoipdb(self, version, cb=None):
        return self.follow_path(
            self.get_page('https://downloads.f5.com/esd/productlines.jsp'),
            [
                {
                    'f': self.follow_specific_link,
                    'args': { 'pattern': rf'BIG-IP v{version}.x.+' },
                }, {
                    'f': self.follow_specific_link,
                    'args': { 'pattern': r'GeoLocationUpdates', }
                },
                {
                    'f': self.download_files,
                    'args': { 'pattern': rf'^ip-geolocation-.+\.zip$', 'download_folder': f'./downloads/GeoIP/v{version}/', 'cb': cb}
                }
            ]
        )

    def download_latest_version(self, version, cb=None ):
        return self.follow_path(
            self.get_page('https://downloads.f5.com/esd/productlines.jsp'),
            [
                {
                    'f': self.follow_specific_link,
                    'args': { 'pattern': rf'BIG-IP v{version}.x.+' },
                }, {
                    'f': self.pick_latest_version,
                    'args': { 'pattern': rf'^{version}[\.0-9]+$', }
                },
                {
                    'f': self.download_files,
                    'args': {'pattern': rf'^BIGIP-{version}[\.0-9]+.+iso$', 'download_folder': f'./downloads/BIG-IP/v{version}/', 'cb': cb}
                }
            ]
        )
