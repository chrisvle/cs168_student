import subprocess
import time
import json
import re

def main():
    hostnames = ["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"]
    num_packets = 5
    output_filename = "tr_a.txt"
    run_traceroute(hostnames, num_packets, output_filename)

def run_traceroute(hostnames, num_packets, output_filename):
    first = True
    for h in hostnames:
        with open(output_filename, "a") as out_txt:
            if first:
                out_txt.write("timestamp " + str(time.time()) + "\n")
                first = False
            out_txt.write("hostname " + h + "\n")
            process = subprocess.Popen(['traceroute', '-a', '-q', str(num_packets), h], stdout=subprocess.PIPE)
            for line in process.stdout.readlines():
                out_txt.write(line)
            out_txt.write("\n")
            process.stdout.close()

    with open(output_filename, "a") as out_txt:
        out_txt.write("done")

def parse_traceroute(raw_traceroute_filename, output_filename):
    from_public = False
    AS_start = 3
    if from_public:
        AS_start = 4

    with open(raw_traceroute_filename) as in_file:
        full = {}
        current_host = None
        current_info = []

        for line in in_file:
            s = line.split()

            if line == "\n":
                continue

            elif s[0] == "done":
                if current_info:
                    full[current_host].append(current_info)
                    current_info = []

                with open(output_filename, 'a') as out_json:
                    json.dump(full, out_json)
                    out_json.write("\n")

                full = {}
                current_host = None
                current_info = []

            else:
                timestamp = re.search('timestamp.*', line)
                if timestamp:
                    timestamp = timestamp.group()[10:]
                    full["timestamp"] = timestamp
                    continue

                hostname = re.search('hostname.*', line)
                if hostname:
                    if current_info:
                        full[current_host].append(current_info)
                        current_info = []
                    hostname = hostname.group()[9:]
                    current_host = hostname
                    full[hostname] = []
                    continue

                if not from_public:
                    name = re.search('\](.*?)\(', line)
                    if name:
                        name = name.group()[2:-2]
                    else:
                        name = "None"
                else:
                    name = re.search('[\d]{1} (.*?) [\[, \(]', line)
                    if name:
                        name = name.group()[2:-2]
                        if len(name) < 7:
                            name = "None"
                    else:
                        name = s[0]
                        if len(name) < 7:
                            name = s[1]
                            if len(name) < 7:
                                name = "None"

                ip = re.search('\((.*?)\)', line)
                if ip:
                    ip = ip.group()[1:-1]
                    try:
                        int(s[0])

                        if current_info:
                            full[current_host].append(current_info)
                            current_info = []
                    except ValueError:
                        if check_dup(ip, current_info):
                            continue
                else:
                    if name.count(".") == 3:
                        ip = name
                    else:
                        ip = "None"

                asn = re.search('\[AS(.*?)\]', line)
                if asn:
                    asn = asn.group()[AS_start:-1]
                    if asn == "0":
                        asn = "None"
                else:
                    asn = "None"

                try:
                    int(s[0])

                    if current_info:
                        full[current_host].append(current_info)
                        current_info = []
                except ValueError:
                    pass

                info = {}
                info["ip"] = ip
                info["name"] = name
                info["ASN"] = asn
                current_info.append(info)

def check_dup(ip, current_info):
    for l in current_info:
        if l['ip'] == ip:
            return True
    return False

def get_ips(raw_traceroute_filename):
    with open(raw_traceroute_filename) as in_file:
        for line in in_file:
            if "hostname" in line:
                print "\n"+line[:-1]
                continue
            if "timestamp" in line or line=="\n":
                continue
            ip = re.search('\((.*?)\)', line)
            if ip:
                ip = ip.group()[1:-1]
            else:
                ip = "None"
            print ip


def run():
    for i in range(5):
        main()
        if i < 4:
            time.sleep(3660)
    parse_traceroute("tr_a.txt", "tr_a.json")