import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import re
from collections import Counter

# read in data and some pre settings
zip_codes = pd.read_csv('material/zip_code_database.csv')
zip_codes = zip_codes.drop(zip_codes[zip_codes['country'] != 'US'].index)
url = 'https://nces.ed.gov/globallocator/'
options = Options()
options.add_argument("--disable-notifications")

# mimic tool
browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
browser.get(url)

# prepare data frame to store and data to use
high_school_result = pd.DataFrame(columns=['state', 'city', 'zip code', 'nature', 'school name', 'address',
										   'contact', 'grades', 'link'])

mat = zip_codes.iloc[:, [0, 2, 5]]
mat = mat.drop_duplicates()
mat.iloc[:, 0] = [str(i) for i in mat.iloc[:, 0]]
for i in range(len(mat)):
	n = 5 - len(mat.iloc[i, 0])
	if n > 0:
		mat.iloc[i, 0] = '0' * n + mat.iloc[i, 0]
mat['public'] = 'To be filled'
mat['private'] = 'To be filled'

# CSS selector
state_path = '#state'  # '//*[@id="state"]'  select
city_path = '#city'  # '//*[@id="city"]'  input
zip_path = '#zipcode'  # '//*[@id="zipcode"]'  input
button = 'body > div:nth-child(7) > div.MainContent > div > div > form > table:nth-child(2) > tbody > tr:nth-child(2) > ' \
		 'td > table > tbody > tr:nth-child(2) > td > table > tbody > tr > td:nth-child(4)'

# check data
fail_states = []
for s in set(mat['state']):
	try:
		state = Select(browser.find_element_by_css_selector(state_path))
		state.select_by_value(s)
	except:
		fail_states.append(s)
print(fail_states)
mat = mat.drop(mat[(mat['state'] == 'AE') | (mat['state'] == 'AP') | (mat['state'] == 'AA')].index)

# fill out the form and submit
k = 0
for i in range(len(mat)):
	state = Select(browser.find_element_by_css_selector(state_path))  # state
	state.select_by_value(mat.iloc[i, 2])
	city = browser.find_element_by_css_selector(city_path)  # primary_city
	city.clear()
	city.send_keys(mat.iloc[i, 1])
	zip_code = browser.find_element_by_css_selector(zip_path)  # zip
	zip_code.clear()
	zip_code.send_keys(mat.iloc[i, 0])
	browser.find_element_by_css_selector(button).click()  # submit

	# scrape data and store
	public_path = '#hiddenitems_school > table:nth-child(1) > tbody'
	private_path = '#hiddenitems_privschool > table > tbody'
	try:
		table = browser.find_element_by_css_selector(public_path)
		public_res = table.text
	except:
		public_res = 'N/A'
	try:
		table = browser.find_element_by_css_selector(private_path)
		private_res = table.text
	except:
		private_res = 'N/A'

	mat['public'][i] = public_res
	mat['private'][i] = private_res

	# format and store to result table
	soup = BeautifulSoup(browser.page_source, "html.parser")

	public_list = public_res.split('\n')
	n_pub = int(len(public_list) / 3)
	if n_pub > 0:
		link_list = []
		b = soup.select(public_path)
		tables = list(b)[0].find_all('tr')
		for t in list(tables):
			link = list(t.find_all('a'))[0]
			link_list.append(link.get('href'))
		for j in range(n_pub):
			high_school_result = high_school_result.append({'state': 'N/A'}, ignore_index=True)
			high_school_result.iloc[k, 0:3] = list(mat.iloc[i, [2, 1, 0]])
			high_school_result['nature'][k] = 'public'
			high_school_result['school name'][k] = public_list[j * 3].strip()
			high_school_result['address'][k] = public_list[j * 3 + 1].strip()
			spot = [m.start() for m in re.finditer('grade', public_list[j * 3 + 2])][0]
			high_school_result['contact'][k] = public_list[j * 3 + 2][:spot].strip()
			high_school_result['grades'][k] = public_list[j * 3 + 2][spot:]
			high_school_result['link'][k] = link_list[j]
			k += 1

	private_list = private_res.split('\n')
	n_pri = int(len(private_list) / 4)
	if n_pri > 0:
		link_list = []
		b = soup.select(private_path)
		tables = list(b)[0].find_all('tr')
		for t in list(tables):
			link = list(t.find_all('a'))[0]
			link_list.append(link.get('href'))
		for j in range(n_pri):
			high_school_result = high_school_result.append({'state': 'N/A'}, ignore_index=True)
			high_school_result.iloc[k, 0:3] = list(mat.iloc[i, [2, 1, 0]])
			high_school_result['nature'][k] = 'private'
			high_school_result['school name'][k] = private_list[j * 4].strip()
			high_school_result['address'][k] = private_list[j * 4 + 1].strip()
			high_school_result['contact'][k] = private_list[j * 4 + 2].strip()
			high_school_result['grades'][k] = private_list[j * 4 + 3].strip()
			high_school_result['link'][k] = link_list[j]
			k += 1

# mat.to_csv('results/raw data.csv')
# high_school_result.to_csv('results/high school info.csv')


# Counter(high_school_result['grades'])
high_school_result = pd.read_csv('results/high school info.csv', index_col=0)
grades_dic = list(set(high_school_result['grades']))

grades_set = pd.DataFrame(columns=['describe', 'start', 'end'])
grades_set['describe'] = ['N/A'] * len(grades_dic)

for i in range(len(grades_dic)):
	grades_set['describe'][i] = grades_dic[i][8:]
	s = grades_set['describe'][i].split(' - ')
	grades_set['start'][i] = s[0]
	if len(s) > 1:
		grades_set['end'][i] = s[1]

weird_set1 = high_school_result[high_school_result['grades'] == 'grades: -6']

# select high schools
grades_dic = list(high_school_result['grades'])
grades_set = pd.DataFrame(columns=['describe', 'start', 'end'])
grades_set['describe'] = ['N/A'] * len(grades_dic)

for i in range(len(grades_dic)):
	grades_set['describe'][i] = grades_dic[i][8:]
	s = grades_set['describe'][i].split(' - ')
	grades_set['start'][i] = s[0]
	if len(s) > 1:
		grades_set['end'][i] = s[1]

hs = []
for i in range(len(grades_set)):
	if grades_set['start'][i].isdigit():
		if int(grades_set['start'][i]) > 9:
			hs.append(i)

	try:
		if grades_set['end'][i].isdigit():
			if int(grades_set['end'][i]) >= 10:
				hs.append(i)
	except:
		pass

high_schools = high_school_result.iloc[list(set(hs)), :]
# high_schools.to_csv('results/high schools.csv', index=False)


# check the result
set(grades_set['describe'][list(set(hs))])
print(set(high_school_result['zip code']) > set(high_schools['zip code']))
zip_a = list(set(high_schools['zip code']))
zip_b = list(set(high_school_result['zip code']))
zip_diff = list(set(high_school_result['zip code']) - set(high_schools['zip code']))

state_a = list(set(high_schools['state']))
state_b = list(set(high_school_result['state']))
state_diff = list(set(high_school_result['state']) - set(high_schools['state']))

city_a = list(set(high_schools['city']))
city_b = list(set(high_school_result['city']))
city_diff = list(set(high_school_result['city']) - set(high_schools['city']))

# high_school_result[high_school_result['city'] == 'Sun City']
