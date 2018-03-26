import os, logging
from datetime import date, timedelta
import boto3
from Retention import Retention

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getRetentionPolicy():
    policy = {}

    for retention in Retention:
        name = 'retention_' + retention.value
        if name in os.environ:
            policy[retention.value] = int(os.environ[name])

    return policy

def inferRetention(timestamp):
    # Annual backup on the New Year Day
    if timestamp.month == 1 and timestamp.day == 1:
        retention = Retention.YEARLY
    # Monthly backup in the middle of the month
    elif timestamp.day == 15:
        retention = Retention.MONTHLY
    # Weekly backup on Saturdays
    elif timestamp.isoweekday() == 6:
        retention = Retention.WEEKLY
    # Daily backup for everything else
    else:
        retention = Retention.DAILY
        
    return retention

def composeSnapshotDescription(volume):
    return 'Backup for %s from %s' % (getNameTag(volume), date.today())

def getTagValue(item, tagName):
    return [tag['Value'] for tag in item.tags if tag['Key'] == tagName][0]

def getNameTag(item):
    return getTagValue(item, 'Name')

def createSnapshot(volume):
    volumeName = getNameTag(volume)
    description = composeSnapshotDescription(volume)
    retention = inferRetention(date.today())

    tags = [
        {'Key': 'CreatedBy', 'Value': os.environ['appname']},
        {'Key': 'retention', 'Value': retention.value},
    ]

    logger.info('Creating a snapshot for volume `%s` (%s) with `%s` retention policy', volumeName, volume.id, retention.value)
    snapshot = volume.create_snapshot(Description = description)
    snapshot.create_tags(Tags = tags)
    logger.info('%s snapshot has been started' % description)

    return snapshot

def deleteSnapshot(snapshot):
    logger.info('Deleting snapshot: %s', snapshot.description)
    snapshot.delete()

def backup(ec2):
    logger.info('Starting backing up volumes')

    volumes = ec2.volumes.filter(Filters = [
        {'Name': 'status',         'Values': ['in-use']},
        {'Name': 'tag:AutoBackup', 'Values': ['true']}
    ])

    for volume in volumes:
        createSnapshot(volume)

def isExpired(snapshot):
    today = date.today()

    createdAt = snapshot.start_time.date()
    retention = Retention(getTagValue(snapshot, 'retention'))
    policy    = getRetentionPolicy()

    return (
        (retention == Retention.MONTHLY and createdAt < today - timedelta(days  = policy.get(Retention.MONTHLY.value) * 31)) or
        (retention == Retention.WEEKLY  and createdAt < today - timedelta(weeks = policy.get(Retention.WEEKLY.value))) or
        (retention == Retention.DAILY   and createdAt < today - timedelta(days  = policy.get(Retention.DAILY.value)))
    )

def rotate(ec2):
    logger.info('Starting cleaning up snapshots')

    snapshots = ec2.snapshots.filter(Filters = [
        {'Name': 'tag:CreatedBy', 'Values': [os.environ['appname']]},
        {'Name': 'status',        'Values': ['completed']},
    ])

    for snapshot in snapshots:
        if (isExpired(snapshot)):
            deleteSnapshot(snapshot)
        else:
            logger.info('Preserving snapshot: %s', snapshot.description)

def handler(event, context):
    logger.debug('Event: %s', event)

    regions = [event['region']]

    for region in regions:
        logger.info('Processing `%s` region', region)
        ec2 = boto3.resource('ec2', region_name = region)

        backup(ec2)
        rotate(ec2)
