#Objective 5.3 Fetching Cloudwatch metrics using Boto3
import boto3
from datetime import datetime, timedelta

# Create a CloudWatch client
cloudwatch = boto3.client('cloudwatch')

def get_instance_data(instance_id):
    # Calculate the time range (last 30 minutes)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=30)

    # Fetch the metrics for the given instance
    metrics = [
        'StatusCheckFailed',
        'CPUUtilization',
        'NetworkIn',
        'NetworkOut'
    ]

    # Loop through the list of metrics
    for metric_name in metrics:
        # Get the metric statistics for the given metric
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[
                {
                    'Name': 'InstanceId',
                    'Value': instance_id
                }
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=1800,
            Statistics=['Average'], 
        )
        if 'Datapoints' in response and response['Datapoints']:
            for datapoint in response['Datapoints']:
                value = datapoint['Average']
                print(f"{metric_name}: {value}")
        else:
            print(f"No data found for {metric_name} in the last 30 minutes.")

def get_cpu_util(instance_id):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=30)
    # Get the metric statistics for the given metric
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=60,
        Statistics=['Average'], 
    )
    if 'Datapoints' in response and response['Datapoints']:
        for datapoint in response['Datapoints']:
            value = datapoint['Average']
            #print(f"CPU Utilization: {value}")
            return value

#instance_id = 'i-0716f9b9f0a9fbc46'
#print(get_cpu_util(instance_id))