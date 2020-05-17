import logging
import sys
import re
import time
import datetime
from settings.settings import Settings
from src.openwebif.openwebif import OpenWebIf

logger = logging.getLogger(__name__)


class PurgeRecordings:

    def __init__(self):
        self.settings = Settings()
        self.config = self.settings.load_config()
        self.settings.init_logging('purge_recordings', prefix_date=True, stdout=True)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get_locations(self, open_web_if):
        locations_list = []
        locations = open_web_if.get_locations()
        for key, value in locations.items():
            for key2, value2 in value.items():
                locations_list.append(value2)
        return locations_list

    def days_old(self, dt, now):
        delta = now - dt
        return delta.days

    def main(self):
        logger.info("Starting a new run")

        news_re = re.compile('Nine News')
        now = datetime.datetime.now()
        purge_older_than_days = int(self.config.get('BEYONWIZ', 'purge_older_than_days'))
        logger.info("Purging recordings older than {} days".format(purge_older_than_days))

        open_web_if = OpenWebIf(self.config.get('BEYONWIZ', 'host'), 80)
        locations = self.get_locations(open_web_if)
        for location in locations:
            movies = open_web_if.get_movies(location)
            e2movies = movies['e2movielist']['e2movie']
            for movie in e2movies:
                if news_re.search(movie['e2title']):
                    dt = datetime.datetime.fromtimestamp(int(movie['e2time']))
                    days_old = self.days_old(dt, now)
                    logger.info("{} - {}, {} days old".format(movie['e2title'], dt.strftime("%d/%m/%Y %H:%M"), days_old))
                    if days_old > purge_older_than_days:
                        logger.info("Purging {} - {}".format(movie['e2title'], dt.strftime("%d/%m/%Y %H:%M")))
                        result = open_web_if.delete_movie(movie['e2servicereference'])
                        if 'e2simplexmlresult' in result:
                            if 'e2state' in result['e2simplexmlresult']:
                                if result['e2simplexmlresult']['e2state']:
                                    logger.info("Deleted: {} - {}".format(movie['e2title'], dt.strftime("%d/%m/%Y %H:%M")))
                                else:
                                    logger.error("Failed deleting: {} - {} => {}".format(
                                        movie['e2title'],
                                        dt.strftime("%d/%m/%Y %H:%M"),
                                        result['e2simplexmlresult']['e2statetext']
                                    ))
                            else:
                                logger.error(result)
                        else:
                            logger.error(result)


if __name__ == "__main__":
    purge_recordings = PurgeRecordings()
    purge_recordings.main()
    sys.exit(0)
