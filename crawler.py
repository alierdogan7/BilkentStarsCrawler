# -*- coding: utf-8 -*-
import requests
from pyquery import PyQuery as pq
import pprint
import json

def main():
	cookies = auth('BilkentID', 'Password')
	grades = parse_online(cookies)
	#parse_plain()
	json_file = json.dumps(grades)
	print json_file

def auth(id, pwd):
	args = {
		'ID': id,
		'PWD': pwd,
	}
	
	auth = requests.post("https://stars.bilkent.edu.tr/srs/ajax/login.php",
						data=args)
	
	if auth.text == 'HOME':
		return auth.cookies
		
def parse_plain():
	"""with open('plain_grades.html', 'r') as f:
		plain_html = f.read()"""
	d = pq(filename='plain_grades.html')
	return parse_grades(d)

def parse_online(cookies):
	r = requests.get('https://stars.bilkent.edu.tr/srs/ajax/gradeAndAttend/grade.php', cookies=cookies)
	html = convert_turkish_chars(r.text)
	return parse_grades(html)

def convert_turkish_chars(text):
	mappings = { u"ı": u"i", u"ö": u"o", u"ç": u"c", 
				u"ş": u"s", u"ğ": u"g", u"ü": u"u"}
	for tr, ascii in mappings.iteritems():
		text = text.replace(tr, ascii)
	
	return text

def parse_grades(html):
	d = pq(html)
	grades = {}

	for course in d(".gradeDiv").items():
		code = (course("h4").text()).replace(
					"Grade Records for ", "")
		grades[code] = {}
		headers = []
		#headers row of table
		for header in course("table").find("tr").eq(0).find("th").items():
			headers.append(header.text())

		all_rows = course("table").find("tr")
		first_pass = True
		for row in all_rows.items():
			if first_pass:
				first_pass = False
				continue

			cols = row("td") #all td's in a row
			if len(cols) == 1: #row for grade type with single col. 
				# add an empty object for Midterm, Homework vs
				grades[code][cols.eq(0).text()] = []
			else:
				#find the type of grade via 'Type' column
				# and insert to corresponding Grade Type object

				#map each grade row according to table headers
				grade = {}
				for i in xrange(len(cols)):
					grade[headers[i]] = cols.eq(i).text()

				#insert grade entry corresponding grade type's array
				grades[code][grade["Type"]].append(grade)


	#pprint.pprint(grades)
	return grades

main()