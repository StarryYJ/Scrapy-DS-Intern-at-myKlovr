from bs4 import BeautifulSoup
import requests
import pandas as pd

category = ['national-rankings?page=', 'search?public=true&page=', 'national-rankings/magnet-school-rankings?page=',
			'national-rankings/charter-school-rankings?page=', 'national-rankings/stem?page=']
category_col = ['National', 'Traditional', 'Magnet', 'Charter', 'STEM']


Urls = pd.read_csv('intermediate/high_school_url.csv')
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

proxy = "127.0.0.1:8866"


def get_ranks(lin):
	out = []
	for k in range(1, 1500):
		resp = requests.get(lin + str(k), headers=headers)
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


ranking_df = pd.DataFrame(index=Urls['school'])
except_df = pd.DataFrame(columns=['school', 'category', 'rank'])

for m in range(len(category)):
	link = 'https://www.usnews.com/education/best-high-schools/{0}'.format(category[m])
	school_name = get_ranks(link)
	ranking_df[category_col[m]] = 0
	for i in range(len(school_name)):
		if school_name[i] in ranking_df.index:
			ranking_df.loc[school_name[i], category_col[m]] = i
		else:
			except_df = except_df.append([{'school': school_name[i], 'category': category_col[m], 'rank': i}], ignore_index=True)

	ranking_df.to_csv('temp {0}.csv'.format(category_col[m]))


ranking_df.to_csv('high school ranking.csv')
except_df.to_csv('except_df.csv')


school_list = []
school_name = []


for n in range(len(except_df)):
	sn = except_df['school'][n].replace(' ', '%20')
	if except_df['category'][n] == 'Traditional':
		tail = '&public=true'
	else:
		tail = ''
	search_link = 'https://www.usnews.com/education/best-high-schools/search?name={0}{1}'.format(sn, tail)
	html = requests.get(
		search_link, headers=headers).text
	soup = BeautifulSoup(html, 'lxml')
	li = soup.find('li', style='animation-delay:0ms')
	h2 = li.h2
	url = h2.a['href']
	name = h2.a.text

	school_list.append(url)
	school_name.append(name)

data = {
	"school": school_name,
	"url": school_list
}

url_list = pd.DataFrame(data)
print(url_list)
print(url_list.shape)
# url_list.to_csv('intermediate/supplement_url.csv', index=False)

for n in range(len(url_list)):
	Urls = Urls.append([{'school': url_list.iloc[n, 0], 'url': url_list.iloc[n, 1]}], ignore_index=True)
# url_list.to_csv('results/high_school_url.csv', index=False)


for n in range(len(except_df)):
	if except_df.iloc[n, 0] not in ranking_df.index:
		series = pd.Series({'Traditional': 0, 'Magnet': 0, 'Charter': 0, 'STEM': 0, 'National': 0}, name=except_df.iloc[n, 0])
		ranking_df = ranking_df.append(series)
	ranking_df.loc[except_df.iloc[n, 0], except_df.iloc[n, 1]] = except_df.iloc[n, 2]

# ranking_df.to_csv('results/high shool ranking.csv')


# url1 = pd.read_csv('materials/urls.csv')
# url2 = pd.read_csv('intermediate/high_school_url.csv')
# url3 = pd.read_csv('results/high_school_url.csv')
#
# url_test = pd.concat([url2, url3], axis=0, ignore_index=True)
# url_test1 = url_test.drop(axis=1, index=24115)
# url_test1.to_csv('results/high_school_url.csv', index=False)
