import subprocess
import csv
import datetime
import time
# SNMP config
community = "ai"
routers = ["192.168.122.2"]

# OIDs
oids = {
    "cpu": "1.3.6.1.4.1.9.2.1.58.0",           # CPU 5-second usage
    "in_errors": "1.3.6.1.2.1.2.2.1.14.1",     # ifInErrors (interface index 1)
    "out_errors": "1.3.6.1.2.1.2.2.1.20.1"     # ifOutErrors (interface index 1)
}

def determine_health(cpu, in_err, out_err):
    # Default to failure
    label = "failure"

    if cpu is None or in_err is None or out_err is None:
        return "unknown"

    # Failure condition
    if cpu > 80 or in_err > 50 or out_err > 50:
        label = "failure"
    # Warning condition
    elif cpu > 50 or in_err > 10 or out_err > 10:
        label = "warning"
    # Otherwise, healthy
    else:
        label = "healthy"

    return label

def snmpwalk(ip, oid):
    try:
        result = subprocess.check_output(
            ["snmpwalk", "-v2c", "-c", community, ip, oid],
            stderr=subprocess.STDOUT
        ).decode("utf-8")
        
        # Extract value from output like:
        #   SNMPv2-SMI::enterprises.9.2.1.58.0 = Gauge32: 8
        value = result.strip().split(":")[-1].strip()
        return float(value)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] SNMP failed for {ip} OID {oid}: {e.output.decode()}")
        return None
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return None

# Collect SNMP data
def collect_data():
    now = datetime.datetime.now().isoformat()
    data_rows = []

    for ip in routers:
        row = [now, ip]
        metrics = []

        for label, oid in oids.items():
            val = snmpwalk(ip, oid)
            metrics.append(val)
            row.append(val)

        # Get label
        health = determine_health(*metrics)
        row.append(health)

        data_rows.append(row)

    return data_rows
# CSV setup
csv_file = "cisco_snmp_health.csv"
header = ["timestamp", "ip", "cpu", "in_errors", "out_errors", "label"]

def write_to_csv(rows):
    try:
        with open(csv_file, "x") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass

    with open(csv_file, "a") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

# Run the script
if __name__ == "__main__":
    while(1):
        time.sleep(1)
        data = collect_data()
        write_to_csv(data)
        print("[✓] SNMP data collected and written.")

