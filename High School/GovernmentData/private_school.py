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

fail_list = pd.read_csv('results/fails 2.csv', index_col=0).iloc[:, 0]
high_school_more = pd.DataFrame(index=school_list['school name'][fail_list],
								columns=['ID', 'Physical Address', 'Total Students', 'Non-Prekindergarten',
										 'Other Characteristics'])


# mimic tool
browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)


fail_new = []
for i in range(len(fail_list)):
	# extract ID
	high_school_more['ID'][i] = [m.group() for m in re.finditer(r"ID=\w+\d+", school_list['link'][fail_list[i]])][0][3:]
	link = 'https://nces.ed.gov/surveys/pss/privateschoolsearch/school_detail.asp?Search=1&SchoolID={0}&ID={0}'.\
		format(high_school_more['ID'][i], high_school_more['ID'][i])

	if HTMLSession().get(link).status_code != 200:
		fail_new.append(i)
		continue

	browser.get(link)


	address = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(7) >'
												   ' td > table > tbody > tr > td:nth-child(1) > font')
	high_school_more['Physical Address'][i] = address.text


	total_students = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(11) > '
												  'td > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(4) > td > table:nth-child(1) > tbody > tr:nth-child(1) > td:nth-child(3)')
	high_school_more['Total Students'][i] = total_students.text


	non_prekindergarten = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(11) > '
												   'td > table > tbody > tr > td:nth-child(1) > table > tbody > tr:nth-child(4) > td > table:nth-child(2) > tbody')
	high_school_more['Non-Prekindergarten'][i] = non_prekindergarten.text


	other_characteristics = browser.find_element_by_css_selector('body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(11) > '
											  'td > table > tbody > tr > td:nth-child(3) > table > tbody')
	high_school_more['Other Characteristics'][i] = other_characteristics.text


	for m in range(1, 3):
		by_grade = browser.find_element_by_css_selector(
			'body > div:nth-child(7) > div.sfsContent > table > tbody > tr:nth-child(15) > td > table > tbody > tr:nth-child(' + str(m) + ') > td')
		if by_grade.text != '':
			if by_grade.text.split(':')[0] not in high_school_more.columns:
				high_school_more[by_grade.text.split(':')[0]] = 'N/A'
			high_school_more[by_grade.text.split(':')[0]][i] = by_grade.text.split(':')[1]


fail_df = pd.DataFrame(fail_new)
fail_df.to_csv('results/fails new.csv')
high_school_more.to_csv('results/private schools.csv')




























