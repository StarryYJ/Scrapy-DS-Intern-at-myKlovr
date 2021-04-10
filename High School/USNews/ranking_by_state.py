import selenium
from bs4 import BeautifulSoup
import requests
import pandas as pd

headers = {
	"Host": "www.usnews.com",
	"Connection": "keep-alive",
	"Cache-Control": "max-age=0",
	"Upgrade-Insecure-Requests": "1",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "zh-CN,zh;q=0.9",
	"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}
url = "https://www.usnews.com/education/best-high-schools/search"
proxy = "127.0.0.1:8866"
response = requests.get(url, headers=headers)
data = response.text
soup = BeautifulSoup(data, 'html.parser')
sel = soup.find_all("select", attrs={"name": 'state-urlname'})
states = list(sel)[0].find_all("option")
states_name = [i.text for i in states][1:]
states_value = [i.get('value') for i in states][1:]


def get_ranks(lin):
	out = []
	for k in range(1, 1000):
		resp = requests.get(lin + '?page=' + str(k), headers=headers)
		if resp.status_code == 404:
			break

		s = BeautifulSoup(resp.text, 'lxml')
		for j in range(0, 30):
			l_i = s.find('li', style='animation-delay:%sms' % (j*100))
			if j == 0 and not l_i:
				return out
			if not l_i:
				break
			if not l_i.h2:
				continue
			print(l_i.h2.a.text)
			out.append(l_i.h2.a.text)
	return out


Urls = pd.read_csv('results/high_school_url.csv')
ranking_df = pd.DataFrame(index=Urls['school'])
ranking_df['state'] = 0
except_df = pd.DataFrame(columns=['school', 'category', 'rank'])

for m in range(len(states_name)):
	print(states_name[m])
	print('\n')
	link = 'https://www.usnews.com/education/best-high-schools/{0}/rankings'.format(states_value[m])
	school_name = get_ranks(link)
	for i in range(len(school_name)):
		if school_name[i] in ranking_df.index:
			ranking_df.loc[school_name[i], 'state'] = i
		else:
			except_df = except_df.append([{'school': school_name[i], 'category': states_name[m], 'rank': i}], ignore_index=True)

ranking_df.to_csv('results/high school ranking - states.csv')




