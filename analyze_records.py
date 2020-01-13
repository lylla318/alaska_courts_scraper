import os
import csv
import simplejson as json
import time
import urllib3
import requests
import collections


class Analyzer:

	def __init__(self, input_file, output_file):

		self.case_data = self.read_data(input_file)
		self.dispositions = collections.defaultdict(lambda: collections.defaultdict(int))
		self.indicted_charges = collections.defaultdict(int)
		self.clean_data()
		# self.get_dispositions()
		# chrg = "AS1141410A1 AS11.41.410(a)(1): Sex Assault 1- Penetrate w/o Consent (Unclassified Felony)"
		# self.get_charge_tree(chrg)
		self.get_felony_tree()


	def read_data(self, input_file):

		with open(input_file) as json_file:
			data = json.load(json_file)
			return data

	def clean_data(self):

		# Remove cases without information.
		for key in self.case_data.keys():	
			if(len(self.case_data[key].keys()) == 0):
				self.case_data.pop(key, None)


		# Split full names into first, middle and last.
		
		for key in self.case_data.keys():
			party0 = self.case_data[key]["party0"]
			if(party0["ptyType"] == "Defendant"):
				full_name   = (party0["ptyName"]).split(",")
				last_name   = (full_name[0]).strip()
				first_name  = (full_name[1].split(" ")[0]).strip()
				middle_name = (full_name[1].split(" ")[1]).strip()
			self.case_data[key]["party0"]["firstName"]  = first_name
			self.case_data[key]["party0"]["middleName"] = middle_name
			self.case_data[key]["party0"]["lastName"]   = last_name


	def get_felony_tree(self):

		heirarchy      = {'Unclassified Felony': 1 , 'Murder Unclassified Felony': 2, 'Class A Felony':3, 'Class B Felony':4,  'Class C Felony':5, 'Class A Misdemeanor': 6 , 'Class B Misdemeanor': 7, 'Misdemeanor - Not Classified': 8, 'Probation/Parole Violation': 9, 'Violation (Non-Criminal)': 10}
		inv_heirarchy  = {v: k for k, v in heirarchy.iteritems()}

		# charge_tree = collections.defaultdict(lambda: defaultdict())
		cases = []
		charge_tree = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
		for case_number in self.case_data.keys():
			case = self.case_data[case_number]
			disps = []
			for charge in case["charges"]:
				charge_text = charge["chgDescription"]
				disposition = charge["dispText"]
				disps.append((charge_text,disposition))
			if(disps != []):
				cases.append(disps)

		for case in cases:
			rankings = []
			for tup in case:
				rankings.append(heirarchy[chrg_type])
			rannkings = rankings.sort()
			highest_charge = inv_heirarchy[rankings[0]]
			if("Guilty" not in case[highest_charge]):
				for i in range(1, len(rankings)):
					ranking = rankings[i]
					charge_tree[highest_charge][ranking][case[inv_heirarchy[ranking]]] += 1

		csvrows = []
		for k in charge_tree.keys():
			csvrows.append(["HIGHEST CHARGE: " + k])
			for j in charge_tree[k].keys():
				csvrows.append(["NEXT CHARGE: " + inv_heirarchy[j]])
				sorted_list = sorted(charge_tree[k][j].iteritems(), reverse=True, key=lambda (k,v): (v,k))
				for i in sorted_list:
					csvrows.append([i[0],i[1]])
				csvrows.append(["*********"])

		with open("output_data/felony_tree_2.csv", mode='w') as outfile:
			writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for row in csvrows:
				writer.writerow(row)


	def get_felony_tree_old(self):

		heirarchy      = {'Unclassified Felony': 1 , 'Murder Unclassified Felony': 2, 'Class A Felony':3, 'Class B Felony':4,  'Class C Felony':5, 'Class A Misdemeanor': 6 , 'Class B Misdemeanor': 7, 'Misdemeanor - Not Classified': 8, 'Probation/Parole Violation': 9, 'Violation (Non-Criminal)': 10}
		inv_heirarchy  = {v: k for k, v in heirarchy.iteritems()}

		# charge_tree = collections.defaultdict(lambda: defaultdict())
		cases = []
		charge_tree = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
		for case_number in self.case_data.keys():
			case = self.case_data[case_number]
			disps = {}
			for charge in case["charges"]:
				charge_text = charge["chgDescription"]
				disposition = charge["dispText"]
				disps[charge_text] = disposition
				if(disps != {}):
					cases.append(disps)

		for case in cases:
			rankings = []
			for chrg_type in case.keys():
				rankings.append(heirarchy[chrg_type])
			rannkings = rankings.sort()
			highest_charge = inv_heirarchy[rankings[0]]
			if("Guilty" not in case[highest_charge]):
				for i in range(1, len(rankings)):
					ranking = rankings[i]
					charge_tree[highest_charge][ranking][case[inv_heirarchy[ranking]]] += 1

		csvrows = []
		for k in charge_tree.keys():
			csvrows.append(["HIGHEST CHARGE: " + k])
			for j in charge_tree[k].keys():
				csvrows.append(["NEXT CHARGE: " + inv_heirarchy[j]])
				sorted_list = sorted(charge_tree[k][j].iteritems(), reverse=True, key=lambda (k,v): (v,k))
				for i in sorted_list:
					csvrows.append([i[0],i[1]])
				csvrows.append(["*********"])

		with open("output_data/felony_tree_2.csv", mode='w') as outfile:
			writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for row in csvrows:
				writer.writerow(row)




	def get_felony_tree_detailed(self):

		heirarchy      = {"Unclassified Felony": 1, "Murder Unclassified Felony":2, "Class A Felony": 3, "Class B Felony": 4, "Class C Felony":5, "Class A Misdemeanor": 6}
		inv_heirarchy  = {v: k for k, v in heirarchy.iteritems()}

		cases = []
		sequences = collections.defaultdict(int)

		charge_degrees = set()

		for case_number in self.case_data.keys():
			case = self.case_data[case_number]
			
			seq  = case["caseNum"]
			for charge in case["charges"]:
				indicted_charge = charge["chgDescription"]
				disposition = charge["dispText"]

				charge_degrees.add(charge["chgDegree"])



		print(charge_degrees)


	def get_felony_tree_detailed_old(self):

		inv_heirarchy  = {v: k for k, v in heirarchy.iteritems()}

		cases = []
		missing_disps = set()
		felony_tree = collections.defaultdict(lambda: collections.defaultdict(int))
		for case_number in self.case_data.keys():
			case = self.case_data[case_number]
			disps = {}
			for charge in case["charges"]:
				indicted_charge = charge["indictedCharge"]
				disposition = charge["dispText"]
				if "missing" in disposition:
					missing_disps.add(case["caseNum"])
				tmp = indicted_charge.split(":")
				if(len(tmp) > 1):
					tmp = (tmp[1].split("("))
					tmp = tmp[1].replace(")","")
					disps[tmp] = disposition
			if(disps != {} and "missing" not in disposition):
				cases.append(disps)

		for case in cases:

			rankings = []
			for chrg_type in case.keys():
				rankings.append(heirarchy[chrg_type])
			rannkings = rankings.sort()
			buff = ""
			highest_charge = inv_heirarchy[rankings[0]]
			for ranking in rankings:
				chrg = inv_heirarchy[ranking]

				if("Guilty" not in case[chrg]):
					buff += (" " + chrg)
				else:
					buff += (" " + chrg + " " + case[chrg])
			
			felony_tree[highest_charge][buff] += 1

		# with open("output_data/missing_dispositions_1.csv", mode='w') as outfile:
		# 	missing_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		# 	for case_num in missing_disps:
		# 		missing_writer.writerow([case_num])

		# csvrows = []
		# for chrg_type in felony_tree.keys():
		# 	print("CHARGE TYPE: ", chrg_type)
		# 	csvrows.append(["CHARGE TYPE: ", chrg_type])
		# 	sorted_list = sorted(felony_tree[chrg_type].iteritems(), reverse=True, key=lambda (k,v): (v,k))
		# 	for seq in sorted_list:
		# 		print(seq)
		# 		csvrows.append([seq[0],seq[1]])
		# 	print("*************************************")
		# 	csvrows.append("*************************************")

		# with open("output_data/felony_sequences_2.csv", mode='w') as outfile:
		# 	csv_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		# 	for row in csvrows:
		# 		csv_writer.writerow(row)

	def get_charge_tree(self, chrg):
		
		charge_dict = collections.defaultdict()
		disposition_dict = collections.defaultdict(lambda: collections.defaultdict(int))
		case_nums = collections.defaultdict(int)
		for case_number in self.case_data.keys():
			case = self.case_data[case_number]
			for charge in case["charges"]:
				if(charge["indictedCharge"] == chrg):
					case_nums[case_number] = 0

		for case_number in case_nums:
			case = self.case_data[case_number]
			for charge in case["charges"]:
				indicted_charge = charge["indictedCharge"]
				disposition = charge["dispText"]
				disposition_dict[indicted_charge][disposition] += 1

		with open("tmp.txt", "w") as outfile:
			json.dump(disposition_dict, outfile)


	def get_dispositions(self):

		for case_number in self.case_data.keys():
			case = self.case_data[case_number]
			for charge in case["charges"]:
				indicted_charge = charge["indictedCharge"]
				self.indicted_charges[indicted_charge] += 1
				disposition = charge["dispText"]
				self.dispositions[indicted_charge][disposition] += 1

		print("Most common charges: ")
		csvrows = []
		sorted_list = sorted(self.indicted_charges.iteritems(), reverse=True, key=lambda (k,v): (v,k))
		for i in range(0,20):
			tmp = "%s: %s" % (sorted_list[i][0], sorted_list[i][1])
			print(tmp)
			csvrows.append([tmp])
			dispositions = self.dispositions[sorted_list[i][0]]
			for key, value in sorted(dispositions.iteritems(), reverse=True, key=lambda (k,v): (v,k)):
				print "-----------------------" + "%s: %s" % (key,value)
				row = "%s: %s" % (key,value)
				csvrows.append([row])

		with open("output_data/disposition_info.csv", mode='w') as outfile:
			writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for row in csvrows:
				writer.writerow(row)

	
	def write_missing_data(self, output_file):

		not_found = []
		for key in data.keys():
			if(data[key] == {}):
				not_found.append(key)

		write_missing_data(not_found, output_file)

		with open(output_file, mode='w') as outfile:
			csv_writer = csv.writer(outfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			for case in not_found:
				csv_writer.writerow([case])


if __name__ == '__main__':

	input_file = "output_data/court_cases_w_dispositions.json"
	output_file = "output_data/missing_case_numbers.csv"
	Analyzer(input_file, output_file)


