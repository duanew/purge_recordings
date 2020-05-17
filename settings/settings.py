import logging
import configparser
import os
import sys
import errno
import datetime
import socket

logger = logging.getLogger(__name__)


class Settings:

    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        self.SETTINGS_DIR = os.path.join(self.BASE_DIR, 'settings', 'config.conf')
        self.LOG_ROOT = os.path.join(self.BASE_DIR, 'logs')
        self.LOG_PATH = ""

        if not(os.path.isfile(self.SETTINGS_DIR)):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), self.SETTINGS_DIR)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read(self.SETTINGS_DIR)
        return config

    def create_logs_subfolder(self, folder):
        self.LOG_ROOT = os.path.join(self.LOG_ROOT, folder)
        if not os.path.join(self.LOG_ROOT, folder):
            try:
                os.makedirs(self.LOG_ROOT)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

    def init_logging(self, log_name, prefix_date=False, stdout=False):
        settings = self.load_config()

        if '.log' in log_name:
            log_name = log_name.replace('.log', '')

        if prefix_date:
            time = datetime.datetime.now().strftime('%Y%m%d')
            log_name = log_name + '_' + str(time) + '.log'
        else:
            log_name = log_name + '.log'

        self.LOG_PATH = os.path.join(self.LOG_ROOT, log_name)

        hostname = socket.gethostname()

        logging.basicConfig(
            filename=self.LOG_PATH,
            level=logging.getLevelName(settings.get('LOGGING', 'level')),
            format='%(asctime)s severity=%(levelname)s [%(module)s:%(name)s:%(lineno)s]: %(message)s'
        )

        if stdout:
            logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        return logging
