import requests
import smtplib
import os
import paramiko
import linode_api4
import time
import schedule

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')
SERVER_IP = os.environ.get('SERVER_IP')
WEB_URL = os.environ.get('WEB_URL')
message = "Subject: Website is down \n Please take action"


def restart_server_and_app():
    print('Rebooting the server...')
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    nginx_server = client.load(linode_api4.Instance, 'Linode ID')
    nginx_server.reboot()
    while True:
        nginx_server = client.load(linode_api4.Instance, 'Linode ID')
        if nginx_server.status == 'running':
            time.sleep(10)
            restart_container()
            break


def send_email(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, message)


def restart_container():
    print('Restarting the app')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(hostname=SERVER_IP, username='root', key_filename='/Users/Yasharzada/.ssh/id_rsa')
    stdin, stout, stderr = ssh.exec_command("docker ps -a | grep nginx | awk '{ print $1 }'")
    container_id = stout.readline()
    ssh.exec_command('docker restart' + container_id[0])
    ssh.close()
    print('App restarted')


def monitor_app():
    try:
        response = requests.get(WEB_URL)
        if response.status_code == 200:
            print('App is running successfully')
        else:
            print('App down , fix it.')
            msg = f"Subject: SITE DOWN\n App returned {response.status_code}."
            send_email(msg)
            restart_container()

    except Exception as e:
        print(f'Connection error happened : {e}')
        msg = f"Subject: SITE DOWN\n App not accessible at all."
        send_email(msg)
        restart_server_and_app()


schedule.every(1).hour.do(monitor_app)

while True:
    schedule.run_pending()
