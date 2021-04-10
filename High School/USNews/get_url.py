from bs4 import BeautifulSoup
import requests
import pandas as pd


school_list = []
school_name = []

rge = range(0, 30)
d = {i: i for i in rge}
df = pd.DataFrame(columns=['url'])
for j in range(1, 1500):
	html = requests.get(
		'https://www.usnews.com/education/best-high-schools/search?page={}'.format(j), headers={
			"Host": "www.usnews.com",
			"Connection": "keep-alive",
			"Cache-Control": "max-age=0",
			"Upgrade-Insecure-Requests": "1",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "zh-CN,zh;q=0.9",
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
		}).text
	soup = BeautifulSoup(html, 'lxml')
	print('Get page ' + str(j))

	for i in d:
		print(i)
		li = soup.find('li', style='animation-delay:%sms' % (i*100))

		if not li:
			break
		if not li.h2:
			continue
		h2 = li.h2
		url = h2.a['href']
		name = h2.a.text
		print(name)
		print(url)

		school_list.append(url)
		school_name.append(name)

data = {
	"school": school_name,
	"url": school_list
}

url_list = pd.DataFrame(data)
print(url_list.iloc[:100, :])
print(url_list.shape)

url_list.to_csv('high_school_url.csv', index=False)


