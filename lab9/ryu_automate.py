import os
import docker
import time

RYU_CONTAINER_NAME = "ryu-bgp"
RYU_AS = 65020
RYU_ROUTER_ID = "3.3.3.3"
RYU_IP = "192.168.50.5"
NEIGHBOR_IP = "192.168.50.3"
NEIGHBOR_AS = 65001
NETWORK_NAME = "bgp-net"

client = docker.from_env()

def generate_ryu_bgp_script(RYU_AS, RYU_IP, NEIGHBOR_AS, NEIGHBOR_IP, RYU_ROUTER_ID):
    os.makedirs("/tmp/ryu-bgp", exist_ok=True)
    script = f"""#!/usr/bin/env python3

from ryu.base import app_manager
from ryu.services.protocols.bgp.bgpspeaker import BGPSpeaker

def bgp_best_path_change_handler(event):
    print("Best path changed:", event)

class RyuBGPDemo(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(RyuBGPDemo, self).__init__(*args, **kwargs)
        speaker = BGPSpeaker(as_number={RYU_AS},
                             router_id='{RYU_ROUTER_ID}',
                             best_path_change_handler=bgp_best_path_change_handler)

        speaker.neighbor_add('{NEIGHBOR_IP}', {NEIGHBOR_AS})
"""
    with open("/tmp/ryu-bgp/ryu_bgp_app.py", "w") as f:
        f.write(script)
    print("Generated Ryu BGP app")

def run_ryu_bgp(RYU_CONTAINER_NAME, RYU_IP):
    try:
        client.containers.get(RYU_CONTAINER_NAME).remove(force=True)
    except docker.errors.NotFound:
        pass

    container = client.containers.run(
        "osrg/ryu",
        name=RYU_CONTAINER_NAME,
        command="ryu-manager /ryu-bgp/ryu_bgp_app.py",
        volumes={"/tmp/ryu-bgp": {"bind": "/ryu-bgp", "mode": "rw"}},
        detach=True,
        tty=True,
        stdin_open=True
    )
    network = client.networks.get(NETWORK_NAME)
    network.connect(container, ipv4_address=RYU_IP)
    print("Started Ryu BGP container")
    return container
