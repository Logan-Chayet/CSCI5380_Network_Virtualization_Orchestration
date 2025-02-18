#Objective 5.4 Spinning new instances based on CPU utilization
import boto3
from get_cw_metrics import get_cpu_util

ec2 = boto3.resource('ec2')
instances = ["i-099002599828ad626", "i-0716f9b9f0a9fbc46"]
sns = boto3.client('sns')
sns_topic_arn = 'arn:aws:sns:us-west-2:495599756527:cpu-utilization-alerts'


def send_email(message):
    sns.publish(
        TopicArn=sns_topic_arn,
        Message=message,
        Subject="CPU Utilization Alert",
    )
x = True
while x:
    for instance in instances:
        cpu = get_cpu_util(instance)
        print(f"Instance: {instance}, CPU%: {cpu}")
        if cpu > 5:
            ec2.instances.filter(InstanceIds=instances).stop()
            print("===============================")
            print(f"CPU LIMITED DETECTED, stopping instances: {instances}")
            print("===============================")
            #Creating Instances
            instances = ec2.create_instances(ImageId='ami-00c257e12d6828491', MinCount=2, MaxCount=2, InstanceType='t2.micro')

            #Listing and stopping 2nd instance
            for instance in instances:
                print(f"Instance created with ID: {instance.id}")

            message = "CPU Utilization exceeded for 2 instances, stopped and created two identical instances!"
            send_email(message)
            x = False
            break
    
            
                    

 


    
