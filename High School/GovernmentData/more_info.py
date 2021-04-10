import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession


# read in data and some pre settings
school_list = pd.read_csv('results/high schools.csv')
schools = school_list['school name']
url = 'https://nces.ed.gov/globallocator/'
options = Options()
options.add_argument("--disable-notifications")

high_school_more = pd.DataFrame(index=school_list['school name'],
								columns=['ID', 'Directory Information year', 'District Name', 'Physical Address', 'Status',
										 'Charter', 'Supervisory Union', 'Details year', 'Details', 'Enrollment Info year',
										 'Enrollment more info'])

# mimic tool
browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)


fail_list = []
for i in range(len(school_list)):
	# extract ID
	high_school_more['ID'][i] = [m.group() for m in re.finditer(r"\d+", school_list['link'][i])][0]
	link = 'https://nces.ed.gov/ccd/schoolsearch/school_detail.asp?Search=1&SchoolID={0}&ID={0}'.\
		format(high_school_more['ID'][i], high_school_more['ID'][i])

	if HTMLSession().get(link).status_code != 200:
		fail_list.append(i)
		continue

	browser.get(link)

	# School Directory Information
	School_Directory_Information_school_year = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > '
																					'tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > '
																					'td:nth-child(1) > font')
	high_school_more['Directory Information year'][i] = School_Directory_Information_school_year.text.split('\n')[1]


	district = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(4) > '
													'td > table > tbody > tr:nth-child(3) > td:nth-child(1) > font:nth-child(3)')
	high_school_more['District Name'][i] = district.text


	address = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(4) > '
												   'td > table > tbody > tr:nth-child(5) > td:nth-child(3) > font')
	high_school_more['Physical Address'][i] = address.text


	status = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(4) > '
												  'td > table > tbody > tr:nth-child(7) > td:nth-child(2) > font:nth-child(2)')
	high_school_more['Status'][i] = status.text


	charter = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(4) > '
												   'td > table > tbody > tr:nth-child(7) > td:nth-child(3) > font')
	high_school_more['Charter'][i] = charter.text


	SU = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(4) > '
											  'td > table > tbody > tr:nth-child(9) > td:nth-child(1) > font')
	high_school_more['Supervisory Union'][i] = SU.text


	# School Details
	School_Details_school_year = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(6) > td > font')
	high_school_more['Details year'][i] = School_Details_school_year.text


	details = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(8) > '
												   'td > table > tbody > tr:nth-child(2) > td:nth-child(1)')
	high_school_more['Details'][i] = details.text


	details_2 = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(8) > '
													 'td > table > tbody > tr:nth-child(2) > td:nth-child(2) > table > tbody')
	temp = [j.split(': ') for j in details_2.text.split('\n')]
	details_2_text = []
	for j in temp:
		for k in j:
			details_2_text.append(k)
	for j in range(int(len(details_2_text)/2)):
		if details_2_text[2*j] not in high_school_more.columns:
			high_school_more[details_2_text[2*j]] = 'N/A'
		high_school_more[details_2_text[2*j]][i] = details_2_text[2*j+1]


	# enrollment characteristics
	Enrollment_Characteristics_school_year = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(10) > td > font')
	high_school_more['Enrollment Info year'][i] = Enrollment_Characteristics_school_year.text

	for m in range(1, 4):
		by_grade = browser.find_element_by_css_selector(
			'body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(12) > td > table > tbody > tr:nth-child(' + str(m) + ') > td')
		if by_grade.text != '':
			if by_grade.text.split(':')[0] not in high_school_more.columns:
				high_school_more[by_grade.text.split(':')[0]] = 'N/A'
			high_school_more[by_grade.text.split(':')[0]][i] = by_grade.text.split(':')[1]


	enrollment_more = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(14) > td > table > tbody > tr > td:nth-child(2) > table > tbody > tr')
	high_school_more['Enrollment more info'][i] = enrollment_more.text


fail_df = pd.DataFrame(fail_list)
fail_df.to_csv('results/fails 2.csv')
high_school_more.to_csv('results/high school more info 3.csv')



