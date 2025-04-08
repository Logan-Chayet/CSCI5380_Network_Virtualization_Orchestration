import os
import docker
import time

# Configuration values
#FRR_CONTAINER_NAME = "frr-bgp"
NETWORK_NAME = "bgp-net"
SUBNET = "192.168.50.0/24"
GATEWAY = "192.168.50.1"
#FRR_IP = "192.168.50.3"
#NEIGHBOR_IP = ""
#REMOTE_AS = ""
#FRR_AS = 65001
#FRR_ROUTER_ID = "1.1.1.1"

client = docker.from_env()

def create_network():
    try:
        client.networks.get(NETWORK_NAME)
        print(f"Network {NETWORK_NAME} already exists.")
    except docker.errors.NotFound:
        client.networks.create(
            name=NETWORK_NAME,
            driver="bridge",
            ipam=docker.types.IPAMConfig(
                pool_configs=[
                    docker.types.IPAMPool(
                        subnet=SUBNET,
                        gateway=GATEWAY
                    )
                ]
            )
        )
        print(f"Created network {NETWORK_NAME}.")

# Generate FRR1 config
def generate_frr_conf(FRR_IP, NEIGHBOR_IP, REMOTE_AS, FRR_AS, FRR_ROUTER_ID):
    os.makedirs("/tmp/frr", exist_ok=True)
    daemons_content = """
zebra=yes
bgpd=yes
ospfd=no
ripd=no
isisd=no
ldpd=no
"""
    with open("/tmp/frr/daemons", "w") as daemons_file:
        daemons_file.write(daemons_content)

    config = f"""
frr defaults traditional
hostname frr-bgp
no ipv6 forwarding
!
router bgp {FRR_AS}
 bgp router-id {FRR_ROUTER_ID}
 neighbor {NEIGHBOR_IP} remote-as {REMOTE_AS}
 network {FRR_ROUTER_ID}/32
!
log stdout
"""
    with open("/tmp/frr/frr.conf", "w") as f:
        f.write(config)
    print("Generated frr.conf for frr-bgp")

# Run FRR1 container
def run_frr(FRR_CONTAINER_NAME, FRR_IP):
    try:
        client.containers.get(FRR_CONTAINER_NAME).remove(force=True)
    except docker.errors.NotFound:
        pass

    container = client.containers.run(
        "frrouting/frr:latest",
        name=FRR_CONTAINER_NAME,
        detach=True,
        tty=True,
        stdin_open=True,
        privileged=True,
        volumes={"/tmp/frr": {"bind": "/etc/frr", "mode": "rw"}},
        hostname="frr-bgp"
    )
    network = client.networks.get(NETWORK_NAME)
    network.connect(container, ipv4_address=FRR_IP)
    print("Started frr-bgp container")
    return container
