import os, logging
import aws
from Diehard import Diehard
from policies.gfs import GFS

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.debug('Event: %s', event)

    regions = event['regions'] if 'regions' in event else aws.getRegions()
    policy = GFS()

    for region in regions:
        logger.info('Processing `%s` region', region)

        diehard = Diehard(region, policy)
        diehard.backup()
        diehard.rotate()

        logger.info('All done, good job!')
