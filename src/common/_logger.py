import loguru

from loguru import logger

from ..constants import LOGS_DIR


class Filters:

    @staticmethod
    def level(level: str):
        def _wrap(record: 'loguru.Record'):
            return record['level'].name == level and not record['extra'].get('logger_name')

        return _wrap


format_ = "{time:MMMM D, YYYY > HH:mm:ss} | {level} | {message}"


logger.add(LOGS_DIR / 'success.log', format=format_, filter=Filters.level("SUCCESS"))
logger.add(LOGS_DIR / 'errors.log', format=format_, filter=Filters.level("ERROR"))
logger.add(LOGS_DIR / "exceptions.log", format=format_, filter=Filters.level("EXCEPTION"))
logger.add(LOGS_DIR / 'info.log', format=format_, filter=Filters.level("INFO"))
logger.add(LOGS_DIR / 'debug.log', format=format_, filter=Filters.level("DEBUG"))
