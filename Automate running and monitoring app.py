'''
The script create ec2 instance , install docker and run nginx container on the instance and open the 
required ports in the security group to allow public access to our nginx app.
In the background it will monitor the running nginx container and in case there is no response
for 5 attempts, it will automatically send an email notification and restart the container. 
''' 

import boto3
import requests
import paramiko
import os
import schedule
import smtplib

# Before starting to program make sure your aws credentials are set with access key ,secret key and credentials!
# Could be using the .aws folder or use env variables. Also open port 22 in the default vpc that created, so you can
# ssh into the server and set permission 400 to the pem file.
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
image_id = 'ami-031eb8d942193d84f'  # Replace with the desired AMI ID
ssh_path = 'C:\Users\Yasharzada\Downloads\boto3-server-key.pem'
key_name = 'boto3-server-key'
ssh_user = 'ec2-user'
instance_type = 't2-small' # Replace with the desired type
ec2_ip = ''
msg = "Subject: Website is down \n Please take action"
fail_count = 0

ec2_instance = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')

try:
    response = ec2_instance.run_instances(
        ImageId=image_id,  
        InstanceType=instance_type,  
        MinCount=1,
        MaxCount=1,
        KeyName=key_name,
        # Remove comments if you don't want a default SG or Subnet
        # SecurityGroupIds=['sg-xxxxxxxx'],  # You can replace to your SG ID
        # SubnetId='subnet-xxxxxxxx'  # You can replace to your Subnet ID
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"Created EC2 instance with ID: {instance_id}")

    # Wait until the EC2 instance is running
    ec2_instance.wait_until_running(InstanceIds=[instance_id])
    print("EC2 instance is now fully initialized and running.")

except Exception as e:
    print(f'An error occurred:{str(e)}')

response = ec2_instance.describe_instances(
    Filters=[
        {
            'Name': 'tag:Name',
            'Values': [
                'boto3-server',
            ]
        },
    ]
)
instance = response["Reservations"][0]["Instances"][0]
ec2_ip = instance["PublicIpAddress"]

commands_to_execute = [
    'sudo yum update -y && sudo yum install -y docker',
    'sudo systemctl start docker',
    'sudo usermod -aG docker ec2-user',
    'docker run -d -p 8080:80 --name nginx nginx'
]

print("Connecting to the server")
print(f"Public ip: {ec2_ip}")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=ec2_ip, username=ssh_user, key_filename=ssh_path)

# install docker & start nginx
for command in commands_to_execute:
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.readlines())

ssh.close()

# Open port 8080 on nginx server, if not already open
sg_list = ec2_instance.describe_security_groups(
    GroupNames=['default']
)


def open_nginx_ports():
    port_open = False
    for permission in sg_list['SecurityGroups'][0]['IpPermissions']:
        print(permission)
        # some permissions don't have FromPort set
        if 'FromPort' in permission and permission['FromPort'] == 8080:
            port_open = True

    if not port_open:
        ec2_instance.authorize_security_group_ingress(
            FromPort=8080,
            ToPort=8080,
            GroupName='default',
            CidrIp='0.0.0.0/0',
            IpProtocol='tcp'
        )


def restart_container():
    global fail_count
    print('Restarting the application...')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ec2_ip, username=ssh_user, key_filename=ssh_path)
    stdin, stdout, stderr = ssh.exec_command('docker start nginx')
    print(stdout.readlines())
    ssh.close()
    # reset the count
    fail_count = 0
    print(fail_count)


def send_email(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)


def monitor_application():
    global fail_count
    try:
        response = requests.get(f"http://{ec2_ip}:8080")
        if response.status_code == 200:
            print('Application is running successfully!')
        else:
            print('Application Down. Fix it!')
            fail_count += 1
            if fail_count == 5:
                restart_container()
    except Exception as ex:
        # send_email() Possible to send an email via the function
        print(f'Connection error happened: {ex}')
        print('Application not accessible at all')
        fail_count += 1
        if fail_count == 5:
            restart_container()
        return "test"


schedule.every(1).hour.do(monitor_application)

while True:
    schedule.run_pending()
