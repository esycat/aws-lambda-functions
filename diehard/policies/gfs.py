import os
from datetime import date, timedelta
from aws import getTagValue
from Retention import Retention

class GFS:

    def __init__(self):
        self.policy = self.fromEnv()

    def fromEnv(self):
        policy = {}

        for retention in Retention:
            name = 'retention_' + retention.value
            if name in os.environ:
                policy[retention.value] = int(os.environ[name])

        return policy

    def isExpired(self, snapshot):
        today = date.today()

        createdAt = snapshot.start_time.date()
        retention = Retention(getTagValue(snapshot, 'retention'))

        return (
            (retention == Retention.MONTHLY and createdAt < today - timedelta(days  = self.policy.get(Retention.MONTHLY.value) * 31)) or
            (retention == Retention.WEEKLY  and createdAt < today - timedelta(weeks = self.policy.get(Retention.WEEKLY.value))) or
            (retention == Retention.DAILY   and createdAt < today - timedelta(days  = self.policy.get(Retention.DAILY.value)))
        )

    def inferRetention(self, volume):
        timestamp = date.today()

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
