import boto3
from subprocess import call
import sys
import time
import paramiko

class Swarm_Leader(object):
	def __init__(self,size=1, config=None):

		self.ec2 = boto3.resource('ec2', 'us-east-1')
		self.size = size
		self.config = config
		self.locusts = []
		self.existing = 0
		self.swarm = {}

	def init(self,dependencies=None):
		"""Python bare minimum pre-config enviornment"""

		cmds = "".join(list(map(lambda x: str(x) + "\n", dependencies)))
		self.config['init'] = cmds

	def head_count(self):
		"""Count number of already available locusts."""	
		filters = [{'Name': 'tag:Name', 'Values': [self.config['name']]}]
		for x in self.ec2.instances.filter(Filters=filters):
			if x and x.state['Name'] == 'running':
				self.existing += 1


	def describe(self):
		print("Swarm Created")
		print('size: ',self.size)
		print('name: ', self.config['name'])
		print('type: ', self.config['type'])
		print(self.size - self.existing, "new locusts created")
		print()
				

	def populate(self):
		"""Spawn the required number of locusts in the image of config"""
		self.head_count()
		if self.existing < self.size:
			self.locusts = self.ec2.create_instances(
				TagSpecifications=
				[{'ResourceType': 'instance','Tags': [{'Key': 'Name','Value': self.config['name']},]},],
				Placement={'AvailabilityZone': self.config['region'],},
				ImageId=self.config['ami'],
				InstanceType=self.config['type'],
				MinCount=1,
				MaxCount=self.size - self.existing,
				Monitoring={'Enabled': True},
				KeyName=self.config['key'],
				SecurityGroupIds=self.config['securityId'],
				SecurityGroups=self.config['securityGroup'],
				UserData=self.config['init'],
				IamInstanceProfile={
			    'Arn': self.config['role']}
			    )
	def gather(self,size=0, group=None): 
		while len(self.swarm) < size:
			l = []
			filters = [{'Name': 'tag:Name', 'Values': [group]}]

			for x in self.ec2.instances.filter(Filters=filters):
				if not x: pass
				if x.state['Name'] == 'running':
					self.swarm[x.id] = {'public_dns_name': x.public_dns_name}
					if len(self.swarm) == size: break
			if size < 16: print(list(self.swarm))
			else: print(len(self.swarm))
			time.sleep(.5)
	def inject_code(self, cmd):
		"""Control version of github repository on each x"""
		
		repeat = True
		while repeat:
			repeat = False	
			for x,params in self.swarm.items():
				print(x, cmd)
				if not self.connect_ssh(params['public_dns_name'],cmd):
					repeat = True
				time.sleep(.2)
	def connect_ssh(self,public_dns, cmd):
		try:
			key = paramiko.RSAKey.from_private_key_file("../DLNAkey.pem")
			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.connect(hostname=public_dns, username="ubuntu", pkey=key)
			stdin, stdout, stderr = client.exec_command(cmd)
			print("Available ")
			ret = True
		except Exception as e:
			print('Unavailable, ', e)
			ret = False
		return ret



