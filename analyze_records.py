import os
import csv
import simplejson as json
import time
import urllib3
import requests
import collections


def read_data(input_file, output_file):
	data = None

	with open(input_file) as json_file:
		data = json.load(json_file)

	not_found = []
	print(len(data.keys()))
	for key in data.keys():
		if(data[key] == {}):
			not_found.append(key)

	write_missing_data(not_found, output_file)


def write_missing_data(not_found, output_file):

	with open(output_file, mode='w') as outfile:
		csv_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for case in not_found:
			csv_writer.writerow([case])


if __name__ == '__main__':

	input_file = "output_data/case_information_alaska_detailed.json"
	output_file = "output_data/missing_case_numbers.csv"
	read_data(input_file, output_file)

