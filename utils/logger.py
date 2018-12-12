import logging
from settings.config import settings

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename=settings['logging']['file_name'], encoding='utf-8', mode='a+')
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(name)s: %(message)s',
                                       datefmt='%d/%m/%Y %H:%M:%S'))
logger.addHandler(handler)
