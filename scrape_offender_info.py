import os
import csv
import simplejson as json
import time
import lxml
import urllib3
import requests
import collections
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 
from selenium.common.exceptions import TimeoutException


class Scraper:

	def __init__(self):

		self.search()



	# Search for the page corresponding to a given case number.
	def search(self):

		# Set up the driver.
		chrome_path = os.path.realpath('chromedriver')
		chrome_options = Options()
		chrome_options.add_experimental_option("detach", True)
		driver = webdriver.Chrome(executable_path='/Users/lyllayounes/Documents/lrn_github/ak_daily_scraping/chromedriver', chrome_options=chrome_options)
		page = driver.get( 'https://dps.alaska.gov/SORWeb/Registry/Search' )
		
		time.sleep(3)

		# Query with nothing selected to view all entries.
		button = driver.find_element_by_xpath('//*[@id="main_content"]/div/form/div/div[2]/div[7]/input[2]')
		button.click()

		# Wait for page load.
		try:
			driver.find_element_by_id('SearchResults_wrapper')
		except:
			time.sleep(1)
		
		# Display all results	
		el = driver.find_element_by_xpath('//*[@id="SearchResults_length"]/label/select')
		el.click()
		for option in el.find_elements_by_tag_name('option'):
		    if (option.text == "All"):
		    	option.click()

		# Grab all the profile urls
		profile_urls = []
		links = driver.find_elements_by_xpath('//*[@id="SearchResults"]/tbody/tr[*]/td[*]/a')
		for link in links:
			profile_urls.append(link.get_attribute("href"))

		# Set up data object to populate.
		entries = {}

		# FOR TESTING ONLY 
		# testurl      = "https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=187137639149352769"
		# profile_urls = [u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793366663127834796', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793356667327424794', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=646117133670656602', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793376664127024792', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793306663827784799', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793356663927524795', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793386663627104792', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=646158138570636606', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793301667427314794', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=793336661727354798', u'https://dps.alaska.gov/SORWeb/registry/Detail?SexOffenderId=646177130270176607']

		ctr = 0
		for prof_url in profile_urls:

			if (ctr % 20 == 0):
				print("Processed " + str(ctr) + " of " + str(len(profile_urls)) + " entries...")

			entry = {}

			try:

				profile_html = requests.get(prof_url)
				profile      = BeautifulSoup(profile_html.text, "lxml")
				
				row = profile.findAll("div", {"class" : "row"})[1]

				# Find name
				name = row.find("h2").text
				entry["name"] = name

				# Find charge
				charge = row.find("h3").text
				entry["charge"] = charge

				# Find the aliases
				row = row.findAll("div")
				aliases = [] 
				for div in row:
					aliases.append(div.text.replace('\n',''))
				entry["aliases"] = aliases

				# Find the current status
				status = profile.findAll("p")[0].text.strip() + " " + profile.findAll("p")[1].text.strip()
				entry["status"] = status

				# Get bottom panel information
				panels = profile.findAll("div", {"class", "panel-default"})

				# Find info for each panel
				for i in range(0,3):
					personal_information = panels[i]#.find("div", {"class", "panel-body"})
					for row_div in personal_information.findAll("div", {"class", "row"}):
						for div in row_div.findAll("div"):
							if(len(div.text.split(":")) > 1):
								entry[div.text.split(":")[0].strip()] = div.text.split(":")[1].strip()

			except:

				entry["profile_url"] = prof_url
				entry["error"]       = 1

		
			entries[prof_url] = entry
			# print(entries)
			ctr += 1

		with open("offender_information.txt", "w") as jsonfile:
			json.dump(entries, jsonfile)

		# driver.close()

		# return fields


	# Convert data to string and clean whitespace
	def form_str(self, data):
		return str(data).strip()


	# Read case numbers from CSV.
	def read_case_numbers(self):

		case_nums = []
		with open(self.input_file) as csvfile:
			reader = csv.reader(csvfile)
			for row in reader:
				x = row[0].replace("\xef\xbb\xbf","")
				case_nums.append(x.replace("\xc2\xa0",""))

		return case_nums

	# Write output.
	def write_data(self):
		with open(self.output_file, "w") as outfile:
			json.dump(self.case_data, outfile)
		


if __name__ == '__main__':

	instance = Scraper()

