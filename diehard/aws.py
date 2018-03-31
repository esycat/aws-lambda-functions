import boto3

def getTagValue(item, tagName):
    values = [tag['Value'] for tag in item.tags if tag['Key'] == tagName]
    if len(values) is 0:
        return None
    else:
        return values[0]

def getNameOf(item):
    return getTagValue(item, 'Name')

def getRegions():
    ec2 = boto3.client('ec2')
    return [region['RegionName'] for region in ec2.describe_regions()['Regions']]
