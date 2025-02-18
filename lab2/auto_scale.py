import paramiko
import re
import csv
import openstack
import time

# Constant variables for server setup:
IMAGE_NAME = "cirros-0.6.3-x86_64-disk"
FLAVOR_NAME = "cirros256"
INTERNAL_NETWORK = "lab1"
EXTERNAL_NETWORK = "public"
SERVER_PREFIX = "cirros_auto_"
MAX_SCALE = 4
CPU_THRESHOLD = 10
conn = openstack.connect()
csv_file = "ssh_info.csv"

def get_cpu_usage(host, username, password):
    try:
        # Create SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the device
        client.connect(host, "22", username, password)

        # Run command to get CPU usage
        stdin, stdout, stderr = client.exec_command("top -bn1 | grep CPU | head -n1")
        output = stdout.read().decode()
        stdin.close()
        # Close connection
        client.close()
        
        # Extract CPU usage using regex
        match = re.search(r"(\d+\%) idle", output)

        if match:
            idle = float(match.group(1)[:-1])
            cpu_usage = 100 - idle
            return cpu_usage
        else:
            return "Failed to parse CPU usage"

    except Exception as e:
        return f"Error: {str(e)}"

def sshInfo():
    """ Gets the data for all instances """
    data = {}

    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            router_name = row["hostname"]
            router_data = {
                "ip": row["ip"],
                "username": row["username"],
                "password": row["password"] 
            }
            data[router_name] = router_data

    return data 

def add_sshInfo(hostname, ip, username, password):
    """Appends a new SSH entry to the CSV file."""
    with open(csv_file, "a", newline="") as file:
        fieldnames = ["hostname", "ip", "username", "password"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # Add a new row with SSH credentials
        writer.writerow({"hostname": hostname, "ip": ip, "username": username, "password": password})

# Create server and wait for it to start up
def create_server(conn, server_name):
    print("Create Server:")

    image = conn.image.find_image(IMAGE_NAME)
    flavor = conn.compute.find_flavor(FLAVOR_NAME)
    private_network = conn.network.find_network(INTERNAL_NETWORK)
    public_network = conn.network.find_network(EXTERNAL_NETWORK)


    server = conn.compute.create_server(
        name=server_name,
        image_id=image.id,
        flavor_id=flavor.id,
        networks=[{"uuid": private_network.id}],
    )

    server = conn.compute.wait_for_server(server)

    print(f"Created and configured instance: {server.name}")

    print(f"Now creating/assigning floating IP...")
    floating_ip = create_floating_ip(server, public_network.id)

    return server, floating_ip.floating_ip_address

def create_floating_ip(server, public_network):
    # Check first if we can allocate any floating IPs
    floating_ips = list(conn.network.ips(status="DOWN"))

    if floating_ips:
        floating_ip = floating_ips[0]  # Use the first available IP
        print(f"Floating IP: {floating_ip.floating_ip_address} assigned to: {server.name}")
    else:
        # Allocate a new floating IP
        floating_ip = conn.network.create_ip(floating_network_id=public_network)
        print(f"Floating IP: {floating_ip.floating_ip_address} created for: {server.name}")

    # Attach the floating IP
    ports = list(conn.network.ports(device_id=server.id))
    conn.network.update_ip(floating_ip, port_id=ports[0].id)
    print(f"Attached Floating IP {floating_ip.floating_ip_address} to {server.name}")

    return floating_ip

def scale_instances():
    SCALE = 0
    usage=0
    start_time = time.time()

    while SCALE < MAX_SCALE:
        data = sshInfo()

        for i in data:
            cpu = get_cpu_usage(data[i]['ip'], data[i]['username'], data[i]['password'])
            if cpu > CPU_THRESHOLD:
                usage+=1
                print(f"IP: {data[i]['ip']}, CPU Usage: {cpu}%  <--- THRESHOLD EXCEEDED!")
            elif cpu <= CPU_THRESHOLD:
                print(f"IP: {data[i]['ip']}, CPU Usage: {cpu}%")
                if SCALE >= MAX_SCALE:
                    print("Max instances reached, stopping.")
                    break
        if time.time() - start_time > 40 and usage >= 1:
            print("Threshold exceeded in 40 sec time period! Creating a new instance...")
            server, floating_ip = create_server(conn, SERVER_PREFIX+str(SCALE+1))
            add_sshInfo(server.name, floating_ip, "cirros", "gocubsgo")
            SCALE+=1
            start_time = time.time()
            usage=0
        elif time.time() - start_time > 40 and usage == 0:
            print("Threshold NOT exceeded in 40 sec time period! Continuing to monitor all instances...")
            start_time = time.time()
            usage=0

    time.sleep(40)

if __name__ == "__main__":
    scale_instances()