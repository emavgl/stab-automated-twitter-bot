from core.bot import Bot
from helper.config import read_configuration_from_file

# Set up logging
import logging

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = logging.StreamHandler()
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

if __name__ == "__main__":
    logger.info("Creating bot...")
    config = read_configuration_from_file('config.json')
    bot = Bot(config)
    bot.run()
