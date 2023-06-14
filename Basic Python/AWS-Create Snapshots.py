import boto3
import schedule

ec2_client = boto3.client('ec2', region_name="eu-central-1")


def snapshot_volumes():
    volumes = ec2_client.describe_volumes(
        Filter=[
            {
                'Name': 'tag:Name',
                'Value': ['production']

            }
        ]
    )
    for volume in volumes['Volumes']:
        ec2_client.create_snapshot(
            VolumeId=volume['VolumeId']
        )


schedule.every().day.at("12:00").do(snapshot_volumes)
while True:
    schedule.run_pending()
