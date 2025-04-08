import openstack


conn = openstack.connect()

def create_virtual_network(network_name, subnet_name, router_name, CIDR, gateway):
    #Create Network
    network = conn.network.create_network(name=network_name)
    print(f"Created network: {network.name}")
    
    #Create Subnet
    subnet = conn.network.create_subnet(
    name=subnet_name,
    network_id=network.id,
    ip_version=4,
    cidr=CIDR,
    gateway_ip=gateway,
    dns_nameservers=["8.8.8.8", "8.8.4.4"],
    enable_dhcp=True
    )
    print(f"Created subnet: {subnet.name}")

    #Create Router
    router = conn.network.find_router(router_name)
    if router:
        print(f"Using existing router: {router.name}")
    else:
        router = conn.network.create_router(name=router_name)
        print(f"Created router: {router.name}")

    #Router gateway to public netowrk
    public_net = conn.network.find_network("public")
    conn.network.update_router(router, external_gateway_info={"network_id": public_net.id})
    print("Router gateway set to public network")

    conn.network.add_interface_to_router(router, subnet_id=subnet.id)
    print("Attached subnet to router")
