from bs4 import BeautifulSoup
import requests
import pandas as pd

url = pd.read_csv('results/high_school_url.csv')
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

info_df = pd.DataFrame(index=url['school'])
info_df['Student Diversity'] = 'N/A'
info_df['Overall Student Performance - Percentile'] = 'N/A'
info_df['Overall Student Performance - Expectation'] = 'N/A'
info_df['Underserved Student Performance'] = 'N/A'

max_count = 0

for i in range(20917, len(info_df)):
	# soup.find_all('section')
	print(url['school'][i])
	link = url['url'][i]
	resp = requests.get(link, headers=headers)
	soup = BeautifulSoup(resp.text, 'lxml')

	count = 0
	print('section a')
	a = soup.find_all('section', id='students_teachers_section')[0].find_all('div',
																			 class_='Box-w0dun1-0 DataRow__Row-sc-1udybh3-0 dJBYVI lhoQNa RowSection__Row-kw6jgz-4 eFvuZG')
	if len(a) > 0:
		for j in range(len(a)):
			p_list = a[j].find_all('p')
			if p_list[0].text not in info_df.columns:
				info_df[p_list[0].text] = 'N/A'
			info_df[p_list[0].text][i] = p_list[1].text
			count += 1

	print('section b')
	b_sec = soup.find_all('section', id='test_scores_section')
	b, b_extra = [], []
	for k in range(len(b_sec)):
		b_temp = b_sec[k].find_all('div',
								   class_='Box-w0dun1-0 DataRow__Row-sc-1udybh3-0 dJBYVI lhoQNa RowSection__Row-kw6jgz-4 eFvuZG')
		if len(b_temp) > 0:
			[b.append(b_single) for b_single in b_temp]
	sections = b_sec[0].find_all('section')
	for k in range(len(sections)):
			b_temp = sections[k].find_all('div',
										  class_='Box-w0dun1-0 DataRow__Row-sc-1udybh3-0 dJBYVI kFooTZ RowSection__Row-kw6jgz-4 eFvuZG')
			if len(b_temp) > 0:
				[b.append(b_single) for b_single in b_temp if b_single not in b]

	if len(b) > 0:
		for j in range(len(b)):
			p_list = b[j].find_all('p')
			if 'Percentile Score' in p_list[0].text:
				info_df['Overall Student Performance - Percentile'][i] = p_list[1].text
				count += 1
			elif 'Expectations' in p_list[0].text:
				info_df['Overall Student Performance - Expectation'][i] = p_list[1].text
				count += 1
			elif 'Underserved Students' in p_list[0].text:
				if info_df['Underserved Student Performance'][i] == 'N/A':
					info_df['Underserved Student Performance'][i] = p_list[0].text + ': ' + p_list[1].text
				else:
					info_df['Underserved Student Performance'][i] = info_df['Underserved Student Performance'][
																		i] + '; ' + \
																	p_list[0].text + ': ' + p_list[1].text
			else:
				if p_list[0].text not in info_df.columns:
					info_df[p_list[0].text] = 'N/A'
				info_df[p_list[0].text][i] = p_list[1].text
				count += 1

	c = soup.find_all('section', id='students_teachers_section')[0].find_all('div',
																			 class_='Box-w0dun1-0 Key__Container-sc-12afmmk-4 iOBzTK dZHGGK')
	long = [2, 4, 6, 8, 10, 12, 14]
	temp = []
	if len(c) > 0:
		p_list = c[0].find_all('p')
		for j in range(len(long)):
			temp.append(str(p_list[long[j]].text + ':' + p_list[long[j] + 1].text + ';'))
		info_df['Student Diversity'][i] = temp[0] + temp[1] + temp[2] + temp[3] + temp[4] + temp[5] + temp[6]
		count += 1

	d = soup.find_all('section', id='school_data_section')[0].find_all('div',
																	   class_='Box-w0dun1-0 DataRow__Row-sc-1udybh3-0 dJBYVI lhoQNa RowSection__Row-kw6jgz-4 eFvuZG')
	if len(d) > 0:
		for j in range(len(d)):
			p_list = d[j].find_all('p')
			if p_list[0].text not in info_df.columns:
				info_df[p_list[0].text] = 'N/A'
			info_df[p_list[0].text][i] = p_list[1].text
			count += 1

	e = soup.find_all('section', id='district_section')[0].find_all('div',
																	class_='Box-w0dun1-0 DataRow__Row-sc-1udybh3-0 dJBYVI lhoQNa RowSection__Row-kw6jgz-4 eFvuZG')
	if len(e) > 0:
		for j in range(len(e)):
			p_list = e[j].find_all('p')
			if p_list[0].text not in info_df.columns:
				info_df[p_list[0].text] = 'N/A'
			info_df[p_list[0].text][i] = p_list[1].text
			count += 1

	if count > max_count:
		max_count = count

	if i % 1000 == 0:
		info_df.to_csv('results/other info temp.csv')

info_df.to_csv('results/other info.csv')

