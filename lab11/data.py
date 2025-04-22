import csv
import datetime
from pysnmp.hlapi import *
import sys
#from pysnmp.entity.rfc3413.oneliner import *

# Devices and OIDs
routers = ['192.168.122.2']
oids = {
    'cpu': '1.3.6.1.4.1.9.2.1.57.0',          # CPU 5 sec usage
    'in_errors': '1.3.6.1.2.1.2.2.1.14.1',    # ifInErrors for ifIndex 1
    'out_errors': '1.3.6.1.2.1.2.2.1.20.1'    # ifOutErrors for ifIndex 1
}

def new_snmp_query(ip, oid):
    snmp_ro_comm = 'ai'

    auth = cmdGen.CommunityData(snmp_ro_comm)

    cmdGen = cmdGen.CommandGenerator()

    errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
        auth,
        cmdGen.UdpTransportTarget((ip, 161)),
        cmdGen.MibVariable(oid),
        lookupMib=False,
    )

    if errorIndication:
        sys.exit()

    for oid, val in varBinds:
        print(oid.prettyPrint(), val.prettyPrint())
#new_snmp_query("192.168.122.2", "1.3.6.1.4.1.9.2.1.57.0")
def snmp_query(ip, oid):
    result = None
    for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
        SnmpEngine(),
        CommunityData('ai', mpModel=1),  # Change 'public' if needed
        UdpTransportTarget((ip, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    ):
        if errorIndication or errorStatus:
            return None
        else:
            result = float(varBinds[0][1])
    return result

# Collect and save SNMP data
def collect_data():
    data_rows = []
    now = datetime.datetime.now().isoformat()

    for ip in routers:
        row = [now, ip]
        for metric, oid in oids.items():
            val = snmp_query(ip, oid)
            row.append(val)
        row.append("")  # Placeholder for health label
        data_rows.append(row)
    
    return data_rows
snmp_query("192.168.122.2", "1.3.6.1.4.1.9.2.1.57.0")
# CSV writer
csv_file = "cisco_snmp_health.csv"
header = ['timestamp', 'ip', 'cpu', 'in_errors', 'out_errors', 'label']

def write_to_csv(rows):
    try:
        with open(csv_file, 'x') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass

    with open(csv_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

# Run
#data = collect_data()
#write_to_csv(data)

