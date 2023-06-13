import boto3

ec2 = boto3.client('ec2')
subnets = ec2.describe_subnets()
for subnet in subnets["Subnets"]:
    if subnet["DefaultForAz"]:
        print(subnet["SubnetId"])
