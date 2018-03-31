from enum import Enum, unique

@unique
class Retention(Enum):
    YEARLY  = 'yearly'
    MONTHLY = 'monthly'
    WEEKLY  = 'weekly'
    DAILY   = 'daily'
