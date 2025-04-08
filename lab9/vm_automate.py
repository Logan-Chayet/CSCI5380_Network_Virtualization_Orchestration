import openstack

IMAGE_NAME = "cirros-0.6.3-x86_64-disk"
FLAVOR_NAME = "cirros256"
EXTERNAL_NETWORK = "public"
SERVER_PREFIX = "cirros_auto_"
MAX_SCALE = 4
CPU_THRESHOLD = 10
conn = openstack.connect()

def create_server(server_name, INTERNAL_NETWORK):
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
