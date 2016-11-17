import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
	raw_ping_output_dict = {}
	agg_ping_output_dict = {}

	for host in hostnames:
		temp_rtt = [float(-1.0)] * (num_packets - 1)

		ping_log = subprocess.Popen(['ping', '-c', str(num_packets), host], stdout=subprocess.PIPE, stderr = subprocess.PIPE)
		for line in ping_log.stdout.readlines():

			if "time=" in line:
				temp_rtt_index = int(line.split("icmp_seq=")[1].split(" ")[0])
				time_value_with_ms = line.split("time=")[1]
				time_value = float(time_value_with_ms.split(" ms")[0])

				if temp_rtt_index < num_packets-1:
					temp_rtt[temp_rtt_index] = time_value

		raw_ping_output_dict[host] = temp_rtt

		# Drop rate
		drop_count = 0
		for rtt in temp_rtt:
			if rtt == float(-1.0):
				drop_count += 1

		agg_ping_output_dict[host] = {}
		agg_ping_output_dict[host]["drop_rate"] = float(100) * (1-float(num_packets-1-drop_count)/(num_packets-1))

		# Dropped ALL packets
		if float(max(temp_rtt)) == float(-1.0):
			agg_ping_output_dict[host]["max_rtt"] = float(max(temp_rtt))
			agg_ping_output_dict[host]["median_rtt"] = float(np.median(np.array(temp_rtt)))

		# Dropped SOME or NONE packets
		else:
			no_drop_rtt = [value for value in temp_rtt if value != float(-1.0)]
			agg_ping_output_dict[host]["max_rtt"] = float(max(no_drop_rtt))
			agg_ping_output_dict[host]["median_rtt"] = float(np.median(np.array(no_drop_rtt)))

		ping_log.stdout.close()

	with open(raw_ping_output_filename, 'w') as fp:
		json.dump(raw_ping_output_dict, fp)

	with open(aggregated_ping_output_filename, 'w') as fp:
		json.dump(agg_ping_output_dict, fp)

def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename):
	with open(raw_ping_results_filename) as data_file:
		data = json.load(data_file)

	host_ping_dict = {}

	ping_list = []

	for host in data:
		with_drop_ping_list = data[host]

		ping_list = [value for value in with_drop_ping_list if value != float(-1.0)]
		host_ping_dict[host] = np.sort(ping_list)

	for k,v in host_ping_dict.iteritems():
		yvals = np.arange(len(v))/(float(len(v))-1)
		a = plt.step(v, yvals, label = k)

	plt.legend(loc=4, prop={'size':13})
	plt.xlabel('milliseconds')
	plt.ylabel('Cumulative fraction')
	plt.savefig(output_cdf_filename)

def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename):
	with open(agg_ping_results_filename) as data_file:
		data = json.load(data_file)

	med_rtt_list = []

	for host in data:
		med_rtt = float(round(data[host]["median_rtt"],3))
		if med_rtt != float(-1.0):
			med_rtt_list.append(med_rtt)

	med_rtt_list.sort()

	sorted = np.sort(med_rtt_list)
	yvals = np.arange(len(sorted))/(float(len(sorted))-1)
	plt.step(sorted, yvals, label = "median rtt")
	plt.legend(loc=4, prop={'size':13})
	plt.xlabel('milliseconds')
	plt.ylabel('Cumulative fraction')
	plt.savefig(output_cdf_filename)

def check_for_drop(raw_ping_results_filename):
	with open(raw_ping_results_filename) as data_file:
		data = json.load(data_file)

	drop_count = 0

	for host in data:
		if float(-1.0) in data[host]:
			drop_count+=1
			print host

	print drop_count