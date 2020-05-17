import xmltodict
import requests
import urllib.parse
from requests.exceptions import HTTPError
import logging

logger = logging.getLogger(__name__)


"""

https://dream.reichholf.net/wiki/Enigma2:WebInterface
https://dream.reichholf.net/e2web/

"""


class OpenWebIf:
    # HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
    HEADERS = {"Content-Type": "application/xml", "Accept": "application/xml"}
    API_PATH = "/web"
    API_MOVIES = "/movielist"
    API_MOVIE_DELETE = "/moviedelete"
    DEFAULT_DIRECTORY = "/media/hdd/movie"

    def __init__(self, host=None, port=80, username=None, password=None, is_https=False):
        self.host = host
        self.username = username
        self.password = password
        protocol = 'http' if not is_https else 'https'
        self.base_url = '{}://{}:{}'.format(protocol, host, port)
        self.session = requests.Session()
        if username is not None:
            self.session.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.session.headers = OpenWebIf.HEADERS

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def json(self, path):
        try:
            response = self.session.get(url=self.base_url + OpenWebIf.API_PATH + path)
            response.raise_for_status()
            result = xmltodict.parse(response.content)
            return result
        except HTTPError as e:
            logger.warning(e.message)
            raise e

    def json_put(self, path, dict):
        try:
            response = self.session.put(url=self.base_url + OpenWebIf.API_PATH + path, data=xmltodict.unparse(dict))
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.warning(e.message)
            raise e

    def json_patch(self, path, dict):
        try:
            response = self.session.patch(url=self.base_url + OpenWebIf.API_PATH + path, data=xmltodict.unparse(dict))
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.warning(e.message)
            raise e

    def json_post(self, path, dict):
        try:
            response = self.session.post(url=self.base_url + OpenWebIf.API_PATH + path, data=xmltodict.unparse(dict))
            response.raise_for_status()
            return response.json()
        except HTTPError as e:
            logger.warning(e.message)
            raise e

    def get_movies(self, directory=None):
        request_url = OpenWebIf.API_MOVIES
        if directory:
            request_url += '?' + directory
        result = self.json(request_url)
        return result

    def get_locations(self):
        return self.json('/getlocations')

    def delete_movie(self, movie):
        request_url = OpenWebIf.API_MOVIE_DELETE + '?sRef=' + urllib.parse.quote(movie)
        result = self.json(request_url)
        return result

