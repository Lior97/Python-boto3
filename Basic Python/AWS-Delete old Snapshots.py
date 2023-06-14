import boto3
import schedule
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name="eu-central-1")

volumes = ec2_client.describe_volumes(
    Filter=[
        {
            'Name': 'tag:Name',
            'Value': ['production']

        }
    ]
)


def delete_snapshots():
    for volume in volumes['Volumes']:
        snapshots = ec2_client.describe_snapshot(
            OwnerIds=['self'],
            Filter=[
                {
                    'Name': 'volume-id',
                    'Value': [volume['VolumeId']]

                }
            ]
        )
    sorted_by_date = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)

    for snap in sorted_by_date[2:]:
        ec2_client.delete_snapshots(
            SnapshotId=snap['Snapshots']
        )


schedule.every().day.at("12:00").do(delete_snapshots)
while True:
    schedule.run_pending()
