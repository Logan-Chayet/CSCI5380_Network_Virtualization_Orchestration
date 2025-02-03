import paramiko
import re
import time
import requests
from novaclient import client
import os
from keystoneauth1.identity import v3
from keystoneauth1 import loading
from keystoneauth1 import session

# Define SSH connection details
host = "172.24.4.12"
#port = 22
username = "cirros"
password = "gocubsgo"  # Consider using key-based authentication

def get_cpu_times(client):
    """Fetch CPU times from /proc/stat and parse the values."""
    stdin, stdout, stderr = client.exec_command("cat /proc/stat | grep '^cpu '")
    output = stdout.read().decode().strip()
    # Parse the first line of /proc/stat
    parts = output.split()
    user, nice, system, idle, iowait, irq, softirq, steal = map(int, parts[1:9])

    total_idle = idle + iowait
    total_usage = user + nice + system + irq + softirq + steal
    total = total_usage + total_idle

    return total, total_usage
def get_usage(): 
    # Create SSH client
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote machine
        client.connect(hostname=host, username=username, password=password)

        # Get first CPU sample
        total1, usage1 = get_cpu_times(client)
        time.sleep(0.5)  # Wait for a short interval
        total2, usage2 = get_cpu_times(client)
        # Compute CPU usage percentage
        total_diff = total2 - total1
        usage_diff = usage2 - usage1
        cpu_usage = (usage_diff / total_diff) * 100 if total_diff else 0

        print(f"CPU Usage: {cpu_usage:.2f}%")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()

get_usage()

auth_url = "http://198.11.21.103/identity/v3/auth/tokens"
username = os.environ['OS_USERNAME']
password = os.environ['OS_PASSWORD']
project_name = os.environ['OS_PROJECT_NAME']
domain_name = os.environ['OS_USER_DOMAIN_NAME']
project_id = "fa69c86f0eda40e8a33178aea05ed042"

# Nova API Endpoint
nova_url = "http://198.11.21.103/compute/v2/fa69c86f0eda40e8a33178aea05ed042"

# Image, Flavor, and Network Details
image_name = "cirros"
flavor_name = "m1.small"
network_id = "your-network-id"

def get_token():
    auth_payload = {
    "auth": {
        "identity": {
            "methods": [
                "password"
            ],
            "password": {
                "user": {
                    "name": username,
                    "domain": {
                        "name": domain_name
                    },
                    "password": password
                }
            }
        }
    }

}

    response = requests.post(auth_url, json=auth_payload)
    response.raise_for_status()
   
    return response.headers["X-Subject-Token"]  # Keystone token

#auth = v3.Token(auth_url=auth_url, token=get_token())

#sess = session.Session(auth=auth)



#nova = client.Client("2.1", session=sess)

#nova = client.Client("2", username, password, project_id, nova_url)

loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url=nova_url,
                                username=username,
                                password=password,
                                project_id=project_id)
sess = session.Session(auth=auth)
#nova = client.Client("2.1", session=sess)




#servers = nova.servers.list()
#for server in servers:
#    print(server.name)


def get_resource_id(endpoint, name, headers):
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    resources = response.json()
    print(resources) 
    for resource in resources['images' if 'images' in resources else 'flavors']:
        if resource["name"] == name:
            return resource["id"]
    
    return None

token = get_token()
headers = {"X-Auth-Token": token, "Content-Type": "application/json"}

x = get_resource_id(f"http://198.11.21.103/compute/v2.1/flavors", image_name, headers)
print(x)
