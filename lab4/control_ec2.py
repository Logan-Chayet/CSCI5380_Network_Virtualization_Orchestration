#Objective 5.2 Controlling EC2 using Boto3 
import boto3
import time

ec2 = boto3.resource('ec2')

#Creating Instances
instances = ec2.create_instances(ImageId='ami-00c257e12d6828491', MinCount=2, MaxCount=2, InstanceType='t2.micro')

#Listing and stopping 2nd instance
insts = []
for instance in instances:
    print(f"Instance ID: {instance.id}")
    insts.append(instance.id)
print(f"\n")
print(f"Now stopping Instance: {instance.id}")
time.sleep(5)
ec2.instances.filter(InstanceIds=[insts[1]]).stop()

#Listing info for Instances
data = {}

instances2 = ec2.instances.filter(
    Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
for instance in instances2:
    data[instance.id] = [instance.instance_type]

instances = ec2.instances.all()  # This will fetch all instances
# Loop through the reservations and instances
for instance in ec2.instances.all():
    # Get Instance ID, Type, Private IP, and State
    if instance.id in data.keys():
        instance_id = instance.id
        instance_type = instance.instance_type
        private_ip = instance.private_ip_address if instance.private_ip_address else 'N/A'
        state = instance.state['Name']  # Running, Stopped, etc.

        # Print the result in the desired format
        print(f"{instance_id}\t{instance_type}\t{private_ip}\t{state}")