import openstack

conn = openstack.connect()

def create_security_group(group_name):
    sec_group = conn.network.find_security_group(group_name)
    if sec_group:
        print(f"Using existing security group: {group_name}")
        return sec_group
    sec_group = conn.network.create_security_group(name=group_name, description="Allow intra- and inter-VN traffic")
    print(f"Created security group: {group_name}")
    return sec_group

def remove_security_group_from_server(server_name, sec_group_name):
    server = conn.compute.find_server(server_name)
    if not server:
        print(f"Server '{server_name}' not found.")
        return

    server = conn.compute.get_server(server.id)  # Get full server object
    current_sgs = server.security_groups
    attached_sg_names = [sg['name'] for sg in current_sgs]

    #print(f"Current security groups on {server_name}: {attached_sg_names}")

    if sec_group_name not in attached_sg_names:
        print(f"Security group '{sec_group_name}' not attached to server '{server_name}', skipping removal.")
        return

    # Use session + endpoint from the connection
    session = conn.session
    endpoint = conn.compute.get_endpoint()
    url = f"{endpoint}/servers/{server.id}/action"
    body = {
        "removeSecurityGroup": {
            "name": sec_group_name
        }
    }

    print(f"Sending request to remove SG '{sec_group_name}' from server '{server_name}'...")

    response = session.post(url, json=body)
    if response.status_code == 202:
        print(f"Successfully removed security group '{sec_group_name}' from server '{server_name}'")
    else:
        print(f"Failed to remove security group: {response.status_code}, {response.text}")

def remove_security_group_from_server2(server_name, sec_group_name):
    # Find the server by name
    server = conn.compute.find_server(server_name)
    if not server:
        print(f"Server '{server_name}' not found.")
        return

    server_id = server.id

    # Use session from connection directly
    session = conn.session
    endpoint = conn.compute.get_endpoint()

    # Prepare REST API call
    url = f"{endpoint}/servers/{server_id}/action"
    body = {
        "removeSecurityGroup": {
            "name": sec_group_name
        }
    }

    # Send POST request to remove the security group
    response = session.post(url, json=body)
    if response.status_code == 202:
        print(f"Removed security group '{sec_group_name}' from server '{server_name}'")
    else:
        print(f"Failed to remove security group: {response.status_code}, {response.text}")


def allow_icmp(sec_group, server_name):
    conn.network.create_security_group_rule(
        security_group_id=sec_group.id,
        direction="ingress",
        protocol="icmp",
        ethertype="IPv4"
    )
    server = conn.compute.find_server(server_name)
    conn.compute.add_security_group_to_server(server, sec_group.name)
    print(f"Added ICMP rule to security group: {sec_group.name}")

def allow_ssh(sec_group, server_name):
    conn.network.create_security_group_rule(
        security_group_id=sec_group.id,
        direction="ingress",
        protocol="tcp",
        port_range_min=22,
        port_range_max=22,
        ethertype="IPv4"
    )
    server = conn.compute.find_server(server_name)
    conn.compute.add_security_group_to_server(server, sec_group.name)
    print(f"Added SSH rule to security group: {sec_group.name}")

def allow_tcp(sec_group, server_name):
    conn.network.create_security_group_rule(
        security_group_id=sec_group.id,
        direction="ingress",
        protocol="tcp",
        port_range_min=1,
        port_range_max=65535,
        remote_ip_prefix="0.0.0.0/0",  # Allow all — can restrict by subnet if needed
        ethertype="IPv4"
    )
    server = conn.compute.find_server(server_name)
    conn.compute.add_security_group_to_server(server, sec_group.name)
    print(f"Added TCP rule to security group: {sec_group.name}")

def allow_udp(sec_group, server_name):
    conn.network.create_security_group_rule(
        security_group_id=sec_group.id,
        direction="ingress",
        protocol="udp",
        port_range_min=1,
        port_range_max=65535,
        remote_ip_prefix="0.0.0.0/0",  # Allow all — can restrict by subnet if needed
        ethertype="IPv4"
    )
    server = conn.compute.find_server(server_name)
    conn.compute.add_security_group_to_server(server, sec_group.name)
    print(f"Added UDP rule to security group: {sec_group.name}")


    
