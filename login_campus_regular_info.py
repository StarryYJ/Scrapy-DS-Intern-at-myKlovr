from requests_html import HTMLSession
import pandas as pd
from bs4 import BeautifulSoup

Urls = pd.read_csv('material/urls.csv', names=['University', 'URL'])
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
						 ' Chrome/84.0.4147.105 Safari/537.36',
		   'username': 'your username',
		   'password': 'your password',
		   # you may need to change cookie here:
		   # log in on your browser, find it in the 'Network' section, 'Request Headers' block, with developer tool
		   "cookie": 'get with developer tool'}
regular_info = pd.DataFrame(index=Urls['University'])

for i in range(len(Urls)):
	url = ('https://www.usnews.com' + Urls.iloc[i, 1] + '/campus-info').replace(' ', '')
	print(url)

	session = HTMLSession()
	page = session.get(url, headers=headers, timeout=5)
	soup = BeautifulSoup(page.content, 'html.parser')

	body = soup.find_all('div', class_='Display__BellowStyled-h3gn08-6 gdKeTK')

	# get main sections title:
	ID = []
	for section in body:
		ID.append(section['id'])

	# map main sections and get info inside
	for j in range(len(ID)):
		k = 1
		while True:
			test = soup.select('#{0} > div > div > div:nth-child({1})'.format(ID[j], k))
			if len(test) == 0:  # which means there's no next block in this section
				break  # therefore come to the next section
			test_children = list(test[0].children)
			aa = test[0].find_all('div', recursive=False)

			for x in aa:
				temp = []
				for y in x.strings:
					temp.append(y)
				if 'Jump To Section:' not in temp:
					col_name = ' - '.join([ID[j], temp[0]])
					if col_name not in regular_info.columns:  # create a new column if the category doesn't exist
						regular_info[col_name] = 'N/A'
					if len(temp) == 2:
						regular_info[col_name][i] = temp[1]
					else:
						regular_info[col_name][i] = ', '.join(temp[1:])
					k += 1
				else:  # if it's a button div which doesn't include any useful info, we skip
					k += 1
					break

# regular_info.to_csv('campus/login_info_1.csv')

