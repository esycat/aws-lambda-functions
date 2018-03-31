import os, logging
from datetime import date
import boto3
from SnapshotService import SnapshotService

class Diehard:

    def __init__(self, region, policy):
        self.logger = logging.getLogger()
        self.region = region
        self.policy = policy
        self.service = SnapshotService()
        self.ec2 = boto3.resource('ec2', region_name = region)

    def backup(self):
        self.logger.info('Starting backing up volumes')

        volumes = self.ec2.volumes.filter(Filters = [
            {'Name': 'status',         'Values': ['in-use']},
            {'Name': 'tag:AutoBackup', 'Values': ['true']}
        ])

        for volume in volumes:
            retention = self.policy.inferRetention(volume)
            self.service.create(volume, retention)

    def rotate(self):
        self.logger.info('Starting cleaning up snapshots')

        snapshots = self.ec2.snapshots.filter(Filters = [
            {'Name': 'tag:CreatedBy', 'Values': [os.environ['appname']]},
            {'Name': 'status',        'Values': ['completed']},
        ])

        for snapshot in snapshots:
            if (self.policy.isExpired(snapshot)):
                self.service.delete(snapshot)
            else:
                self.logger.info('Preserving snapshot: %s', snapshot.description)
