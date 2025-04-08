import virtual_network_automate
import vm_automate
import security_automate
import frr_automate
import ryu_automate

def menu():
    print("=== NVO Automation Framework ===")
    print("1. Create Virtual Network")
    print("2. Add VM Sinlge or Multi Tenant")
    print("3. Add Security Group and Rules")
    print("4. Add FRR BGP Docker Container")
    print("5. Add RYU BGP Docker Container")
    print("6. Exit")
    print("================================")

def main():
    while(1):
        
        menu()
        choice = input("Enter your choice: ")
        print()
        if choice == "1":
            network_name = input("Enter network name: ")
            subnet_name  = input("Enter subnet name: ")
            router_name  = input("Enter router name: ")
            CIDR         = input("Enter CIDR: ")
            gateway      = input("Enter gateway IP: ") 
            virtual_network_automate.create_virtual_network(network_name, subnet_name, router_name, CIDR, gateway)
        elif choice == "2":
            server_name =       input("Enter server name: ")
            INTERNAL_NETWORK =  input("Enter internal network name: ")

            vm_automate.create_server(server_name, INTERNAL_NETWORK)

        elif choice == "3":
            group_name = input("Enter security group: ")
            server_name = input("Enter server name: ")
            sec_group = security_automate.create_security_group(group_name)
            security_automate.remove_security_group_from_server(server_name, "default")
            print()
            while(1):
                print("=== Security Group Services ===")
                print("1. ICMP")
                print("2. SSH")
                print("3. TCP")
                print("4. UDP")
                print("5. Exit")
                print("================================")
                choice = input("Enter your choice: ")
                print()

                if choice == "1": security_automate.allow_icmp(sec_group, server_name)
                elif choice == "2": security_automate.allow_ssh(sec_group, server_name)
                elif choice == "3": security_automate.allow_tcp(sec_group, server_name)
                elif choice == "4": security_automate.allow_udp(sec_group, server_name)
                elif choice == "5": break

        elif choice == "4":
            
            frr_automate.create_network()

            FRR_CONTAINER_NAME = input("Enter container name: ")
            FRR_IP = input("Enter FRR IP: ")
            NEIGHBOR_IP = input("Enter Neighbor IP: ")
            FRR_AS = input("Enter Local AS: ")
            REMOTE_AS = input("Enter Remote AS: ")
            FRR_ROUTER_ID = input("Enter Router ID: ")


            frr_automate.generate_frr_conf(FRR_IP, NEIGHBOR_IP, REMOTE_AS, FRR_AS, FRR_ROUTER_ID)
            frr_automate.run_frr(FRR_CONTAINER_NAME, FRR_IP)
        
        elif choice == "5":


            RYU_CONTAINER_NAME = input("Enter container name: ")
            RYU_IP = input("Enter RYU IP: ")
            NEIGHBOR_IP = input("Enter Neighbor IP: ")
            RYU_AS = input("Enter Local AS: ")
            NEIGHBOR_AS = input("Enter Remote AS: ")
            RYU_ROUTER_ID = input("Enter Router ID: ")


            ryu_automate.generate_ryu_bgp_script(RYU_AS, RYU_IP, NEIGHBOR_AS, NEIGHBOR_IP, RYU_ROUTER_ID)
            ryu_automate.run_ryu_bgp(RYU_CONTAINER_NAME, RYU_IP)

        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid Choice, try again.")
        print()

if __name__ == "__main__":
    main()
