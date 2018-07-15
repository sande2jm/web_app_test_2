
from swarm_leader import Swarm_Leader
import boto3
import time
import yaml
import mpu.io
from subprocess import call



direc = "web_app_test"
github_clone = " git clone https://github.com/sande2jm/" + direc + ".git"
rm_repo = 'sudo rm -r ' + direc

with open("ec2_web_app.yaml", 'r') as stream:
	config = yaml.load(stream)

size = 1
swarm_name = config['instance']['name']
leader = Swarm_Leader(size=size,config=config['instance'])
pip_installs = [
"#!/bin/bash", 
"sudo apt-get update",
"sudo apt-get install -y python3-pip",
'pip3 install --upgrade pip',
"pip3 install flask",
"pip3 install flask_bootstrap",
'sudo python3 -m pip install pymysql',
"sudo apt-get install apache2 libapache2-mod-wsgi-py3",
"sudo ln -sT ~/web_app_test /var/www/html/web_app_test",
"sudo a2enmod wsgi"]


leader.init(dependencies=pip_installs)
leader.populate()
leader.describe()
print(leader.locusts)


leader.gather(size = 1,group='web_app')
print(leader.swarm.items())
leader.inject_code(rm_repo)
leader.inject_code(github_clone)
for x,params in leader.swarm.items():
	ssh = "ssh -i ../DLNAkey.pem ubuntu@" + params['public_dns_name']
	call(ssh.split(" "))	
