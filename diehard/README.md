# Diehard

A simple Lambda function to automate EC2 EBS backups.

## Workflow

## Environment Variables
* `appname` — name of the application, used for `CreatedBy` tags assigned to created snapshots, e.g. `diehard@lambda`
* `retention_monthly` — number of months to retain monthly snapshots (note: one month is counted as 31 day)
* `retention_weekly` — number of weeks to retain weekly snapshots
* `retention_daily` — number of days to retain daily snapshots

## Example Event Payload
```json
{
    "regions": [
        "ca-central-1",
        "eu-central-1",
        "ap-southeast-2"
    ]
}
```

## IAM Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CopySnapshot",
                "ec2:DescribeRegions",
                "ec2:DescribeInstances",
                "ec2:DeleteSnapshot",
                "ec2:ModifySnapshotAttribute",
                "ec2:DescribeTags",
                "ec2:DescribeSnapshotAttribute",
                "ec2:DescribeInstanceAttribute",
                "ec2:DescribeVolumes",
                "ec2:CreateSnapshot",
                "ec2:DescribeSnapshots",
                "ec2:DescribeVolumeAttribute"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": "ec2:CreateTags",
            "Resource": "arn:aws:ec2:*::snapshot/*"
        }
    ]
}
```