import logging
import os
from dotenv import load_dotenv

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger("config")
logger.info('Retrieving environment variables')

try:
    load_dotenv()

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    logger.info('Successfully retrieved environment variables')

except Exception as e:
    logger.info(f'Error while retrieving environment variables: {e}')
