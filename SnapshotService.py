import os, logging
from datetime import date
from Retention import Retention
from aws import getNameOf

class SnapshotService():

    def __init__(self):
        self.logger = logging.getLogger()

    def create(self, volume, retention):
        name = self.composeName(volume)

        tags = [
            {'Key': 'Name',      'Value': name},
            {'Key': 'CreatedBy', 'Value': os.environ['appname']},
            {'Key': 'retention', 'Value': retention.value},
        ]

        self.logger.info('Creating a snapshot for volume `%s` (%s) with `%s` retention policy', getNameOf(volume), volume.id, retention.value)
        snapshot = volume.create_snapshot(Description = self.composeDescription(volume))
        snapshot.create_tags(Tags = tags)
        self.logger.info('Snapshot `%s` has been started…' % name)

        return snapshot

    def delete(self, snapshot):
        self.logger.info('Deleting snapshot: %s', snapshot.description)
        snapshot.delete()

    def composeName(self, volume):
        return '%s.%s' % (getNameOf(volume), date.today())

    def composeDescription(self, volume):
        return 'Backup for %s from %s' % (getNameOf(volume), date.today())
