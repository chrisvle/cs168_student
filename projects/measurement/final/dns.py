import subprocess
from utils import *
import json
import numpy as np
import matplotlib.pyplot as plt

def run_dig(hostname_filename, output_filename, dns_query_server=None):
    final = []

    with open(hostname_filename, "r") as hosts:
        for h in hosts:
            for _ in range(5):
                if "\n" in h:
                    h = h[:-1]

                each_host = {}
                each_host[NAME_KEY] = h
                each_host[SUCCESS_KEY] = True
                each_host[QUERIES_KEY] = []

                section = {}
                section[ANSWERS_KEY] = []

                types = set()

                if dns_query_server:
                    dns_log = subprocess.Popen(['dig', h, "@" + dns_query_server], stdout=subprocess.PIPE)
                    for line in dns_log.stdout.readlines():
                        s = line.split()
                        if "Query time" in line:
                            section[TIME_KEY] = int(s[3])
                            each_host[QUERIES_KEY].append(section)
                            section = {}
                            section[ANSWERS_KEY] = []
                        elif ";" in line or line == "\n":
                            continue
                        else:
                            info = {}
                            info[QUERIED_NAME_KEY] = s[0]
                            info[TYPE_KEY] = s[3]
                            types.add(s[3])
                            info[ANSWER_DATA_KEY] = s[4]
                            info[TTL_KEY] = int(s[1])
                            section[ANSWERS_KEY].append(info)
                    if "A" in types or "CNAME" in types:
                        final.append(each_host)
                    else:
                        fail = {}
                        fail[NAME_KEY] = h
                        fail[SUCCESS_KEY] = False
                        final.append(fail)

                else:
                    dns_log = subprocess.Popen(['dig', '+trace', '+tries=1', '+nofail', h], stdout=subprocess.PIPE)

                    for line in dns_log.stdout.readlines():
                        s = line.split()
                        if "Received" in line:
                            section[TIME_KEY] = int(s[7])
                            each_host[QUERIES_KEY].append(section)
                            section = {}
                            section[ANSWERS_KEY] = []
                        elif ";" in line or line == "\n":
                            continue
                        else:
                            info = {}
                            info[QUERIED_NAME_KEY] = s[0]
                            info[TYPE_KEY] = s[3]
                            types.add(s[3])
                            info[ANSWER_DATA_KEY] = s[4]
                            info[TTL_KEY] = int(s[1])
                            section[ANSWERS_KEY].append(info)
                    if "A" in types or "CNAME" in types:
                        final.append(each_host)
                    else:
                        fail = {}
                        fail[NAME_KEY] = h
                        fail[SUCCESS_KEY] = False
                        final.append(fail)

        with open(output_filename, "w") as out_json:
            json.dump(final, out_json)

def get_average_ttls(filename):
    with open(filename) as in_json:
        data = json.load(in_json)

    total_root, total_tld, total_name, total_term = 0.0, 0.0, 0.0, 0.0
    count_root, count_tld, count_name, count_term = 0.0, 0.0, 0.0, 0.0
    for host in data:
        section_root, section_tld, section_name, section_term = 0.0, 0.0, 0.0, 0.0
        section_count_root, section_count_tld, section_count_name, section_count_term = 0.0, 0.0, 0.0, 0.0
        if host[SUCCESS_KEY]:
            for q in host[QUERIES_KEY]:
                for a in q[ANSWERS_KEY]:
                    if a[QUERIED_NAME_KEY] == '.':
                        section_count_root += 1.0
                        section_root += int(a[TTL_KEY])
                    elif a[QUERIED_NAME_KEY].count(".") == 1:
                        section_count_tld += 1.0
                        section_tld += int(a[TTL_KEY])
                    elif a[TYPE_KEY] != "A" and a[TYPE_KEY] != "CNAME":
                        section_count_name += 1.0
                        section_name += int(a[TTL_KEY])
                    else:
                        section_count_term += 1.0
                        section_term += int(a[TTL_KEY])
                if section_count_root > 0:
                    count_root += 1.0
                    total_root += section_root / section_count_root
                if section_count_tld > 0:
                    count_tld += 1.0
                    total_tld += section_tld / section_count_tld
                if section_count_name > 0:
                    count_name += 1.0
                    total_name += section_name / section_count_name
                if section_count_term:
                    count_term += 1.0
                    total_term += section_term / section_count_term

                section_root, section_tld, section_name, section_term = 0.0,0.0,0.0,0.0
                section_count_root, section_count_tld, section_count_name, section_count_term = 0.0,0.0,0.0,0.0

    avg_root = total_root / count_root
    avg_tld = total_tld / count_tld
    avg_name = total_name / count_name
    avg_term = total_term / count_term
    return [avg_root, avg_tld, avg_name, avg_term]

def helper(data):
    total_list = []
    term_list = []
    for host in data:
        total_resolve = float(0.0)
        term_resolve = float(0.0)
        if host[SUCCESS_KEY]:
            for q in host[QUERIES_KEY]:
                total_resolve += float(q[TIME_KEY])
                for a in q[ANSWERS_KEY]:
                    if a[TYPE_KEY] == "A" or a[TYPE_KEY] == "CNAME":
                        term_resolve += float(q[TIME_KEY])
                        break
        total_list.append(total_resolve)
        term_list.append(term_resolve)

    return total_list, term_list

def get_average_times(filename):
    with open(filename) as in_json:
        data = json.load(in_json)

    total_list, term_list = helper(data)

    avg_resolve = sum(total_list) / len(total_list)
    avg_term = sum(term_list) / len(total_list)

    return [avg_resolve, avg_term]

def generate_time_cdfs(json_filename, output_filename):
    with open(json_filename) as in_json:
        data = json.load(in_json)

    total_list, term_list = helper(data)

    sorted = np.sort(total_list)
    yvals = np.arange(len(sorted))/(float(len(sorted))-1)
    plt.step(sorted, yvals, label = "total")

    sorted = np.sort(term_list)
    yvals = np.arange(len(sorted))/(float(len(sorted))-1)
    plt.step(sorted, yvals, label = "term")

    plt.xlabel('milliseconds')
    plt.ylabel('Cumulative fraction')
    plt.legend(loc=4, prop={'size':13})
    plt.xscale('log')
    plt.savefig(output_filename)

def count_different_dns_responses(filename1, filename2):
    with open(filename1) as in_json:
        data1 = json.load(in_json)

    with open(filename2) as in_json2:
        data2 = json.load(in_json2)

    total_single = 0
    total_double = 0

    list_single = []
    list_double = []
    curr_host = None

    changed_hosts_single = []
    changed_hosts_double = []

    for i in range(len(data1)):
        host1 = data1[i]
        host2 = data2[i]

        curr_host = host1[NAME_KEY]

        curr_set1 = set()
        curr_set2 = set()
        if host1[SUCCESS_KEY]:
            for q1 in host1[QUERIES_KEY]:
                for a1 in q1[ANSWERS_KEY]:
                    if (a1[TYPE_KEY] == "A" or a1[TYPE_KEY] == "CNAME") and  a1[QUERIED_NAME_KEY] == curr_host+".":
                        curr_set1.add(a1[ANSWER_DATA_KEY])
            list_single.append(curr_set1)
            list_double.append(curr_set1)
            curr_set1 = set()

        if host2[SUCCESS_KEY]:
            for q2 in host2[QUERIES_KEY]:
                for a2 in q2[ANSWERS_KEY]:
                    if (a2[TYPE_KEY] == "A" or a2[TYPE_KEY] == "CNAME") and a2[QUERIED_NAME_KEY] == curr_host+".":
                        curr_set2.add(a2[ANSWER_DATA_KEY])
            list_double.append(curr_set2)
            curr_set2 = set()

        if i % 5 == 4:
            prev_single = None
            prev_double = None
            for e1 in list_single:
                if prev_single:
                    if e1 != prev_single:
                        total_single += 1
                        changed_hosts_single.append(curr_host)
                        break
                prev_single = e1
            for e2 in list_double:
                if prev_double:
                    if e2 != prev_double:
                        total_double += 1
                        changed_hosts_double.append(curr_host)
                        break
                prev_double = e2

            list_single = []
            list_double = []

    return [total_single, total_double]