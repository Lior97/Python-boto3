import boto3
from operator import itemgetter

ec2_client = boto3.client('ec2', region_name="eu-central-1")
ec2_resource = boto3.resource('ec2', region_name="eu-central-1")

instance_id = "Id of the instance from aws"

ec2_client.describe_volumes(
    Filters=[
        {
            'Name': 'attachment.instance_id',
            'Values': [instance_id]
        }
    ]
)

instance_volume = volume['Volumes'][0]

snapshots = ec2_client.describe_snapshots(
    OwnerIds=['self'],
    Filter=[
        {
            'Name': 'volume-id',
            'Value': [instance_volume['VolumeId']]

        }
    ]
)

latest_snapshots = sorted(snapshots['Snapshots'], key=itemgetter('StartTime'), reverse=True)[0]
new_volume = ec2_client.create_volume(
    SnapshotId=latest_snapshots['SnapshotId'],
    AvaileabilityZone="az of your instance",
    TagSpecifications=[
        {
            'ResourceType': 'volume',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'production'
                }
            ]
        }
    ]
)

while True:
    vol = ec2_resource.Volume(new_volume['VolumeId'])
    if vol.state == 'available':
        ec2_resource.Instance(instance_id).attach_volume(
            VolumeId=new_volume['VolumeId'],
            Device='/dev/xvdb'
        )
    break
