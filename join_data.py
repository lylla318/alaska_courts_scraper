import os
import csv
import simplejson as json
import time
import urllib3
import requests
import collections




def read_data(output_file, city_bounds, communities, police_data, trooper_posts):

	output_data = collections.defaultdict(dict)
	with open(communities) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',')
		next(reader)
		for row in reader:
			output_data[row["NAME"].lower()] = row

	with open(police_data) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',')
		next(reader)
		for row in reader:
			if(row["\xef\xbb\xbfCOMMUNITY"].lower() in output_data.keys()):
				output_data[row["\xef\xbb\xbfCOMMUNITY"].lower()]["POLICE"] = row["POLICE"]

	
	with open(trooper_posts) as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',')
		next(reader)
		for row in reader:
			if(row["\xef\xbb\xbfPOST "].lower() in output_data.keys()):
				output_data[row["\xef\xbb\xbfPOST "].lower()]["TROOPER"] = 1

	with open(output_file, 'w') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter=',')
		csvwriter.writerow(["NAME", "CLASS", "INCORPDATE", "POLICE", "TROOPER", "POP", "X", "Y"])
		for key in output_data.keys():
			row = output_data[key]
			csvwriter.writerow([row["NAME"], row["CLASS"], row["INCORPDATE"], row["POLICE"], row["TROOPER"], row["POP"], row["X"], row["Y"]])



if __name__ == '__main__':

	output_file = "/Users/lyllayounes/Documents/lrn_github/ak_daily_scraping/output_data/joined_ak_community_data_F.csv"
	city_bounds = "/Users/lyllayounes/Documents/lrn_github/ak_daily_scraping/input_data/ak_city_boundaries.csv"
	communities = "/Users/lyllayounes/Documents/lrn_github/ak_daily_scraping/input_data/ak_communities_geom.csv"
	police_data = "/Users/lyllayounes/Documents/lrn_github/ak_daily_scraping/input_data/ak_comunity_police_presence_data.csv"
	trooper_loc = "/Users/lyllayounes/Documents/lrn_github/ak_daily_scraping/input_data/ak_trooper_posts.csv"
	read_data(output_file, city_bounds, communities, police_data, trooper_loc)







