# Set up logging
import logging

logger = logging.getLogger("Bot")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.StreamHandler()
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
