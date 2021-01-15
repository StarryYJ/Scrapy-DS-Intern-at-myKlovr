from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
from requests_html import HTMLSession
import re
import time


def window_handler(brs):
	try:
		s_window = brs.find_element_by_xpath("/html/body/div[3]/div/div/button")
		s_window.click()
	except:
		pass

	try:
		s_window = brs.find_element_by_xpath("/html/body/div[5]/div/div/button")
		s_window.click()
	except:
		pass

	try:
		s_window = brs.find_element_by_xpath('/html/body/div[6]/div/div/button')
		s_window.click()
	except:
		pass


def window_handler2(brs):
	try:
		s_window = brs.find_element_by_xpath("/html/body/div[3]/div/div/button")
		s_window.click()
	except:
		pass

	try:
		s_window = brs.find_element_by_xpath("/html/body/div[5]/div/div/button")
		s_window.click()
	except:
		pass

	try:
		s_window = brs.find_element_by_css_selector(
			'#app > div > div:nth-child(1) > div:nth-child(8) > div > div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > div > div.Generic__ContentBox-sc-1itie0w-0.cPiuYB.content > div.section-box > div.mt6 > react-trigger > div > div.Slideshow__Container-bw1gs6-0.gCuKqa > div.Arrows__Container-sc-1s7bkvt-2.jAYcej > button:nth-child(3)')
		s_window.click()
	except:
		pass

	try:
		s_window = brs.find_element_by_xpath('/html/body/div[6]/div/div/button')
		s_window.click()
	except:
		pass


Urls = pd.read_csv('material/urls.csv', names=['University', 'URL'])
options = Options()
options.add_argument("--disable-notifications")

session = HTMLSession()

# record_df = pd.DataFrame(index=Urls['University'], columns=['Num'])
# img_df = pd.DataFrame(index=Urls['University'])
# for i in range(24):
# 	col_name = 'Img_{0}'.format(i)
# 	img_df[col_name] = 'N/A'
record_df = pd.read_csv('campus/image count.csv', index_col=0)
img_df = pd.read_csv('campus/image links new 8.csv', index_col=0).fillna('N/A')

i = 111
for i in range(233, len(Urls)):
	url = ('https://www.usnews.com' + Urls.iloc[i, 1] + '/campus-info').replace(' ', '')
	browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
	browser.get(url)

	content = session.get(url)
	soup = BeautifulSoup(browser.page_source, "html.parser")

	basic_address = "#app > div > div:nth-child(1) > div:nth-child(8) > div > div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > div > " \
					"div > div.section-box > div.mt6"
	results_0 = content.html.find(basic_address)
	# print('mark 1')
	if len(results_0) > 0:
		text = results_0[0].text
		a = re.search('\d.*of.*\d', text)
		N = int(a.group().split(' of ')[1].split('\n')[0])
		record_df.iloc[i, 0] = N
		# print(text)

		print(url + '\t has \t' + str(N) + '\timages')
		# if numbers of pictures are more then previous setting
		if N > img_df.shape[1]:
			for n in range(img_df.shape[1], N):
				col_name = 'Img_{0}'.format(n)
				img_df[col_name] = 'N/A'

		while True:
			# print('mark 2')
			try:
				element1 = soup.find_all("img", {"class": "SlideshowInContent__SlideImage-ecnkfw-2 tSQUx"})[0]
			# print('mark 3')
			except:
				try:
					window_handler(browser)
					soup = BeautifulSoup(browser.page_source, "html.parser")
				# print('mark 4')
				except:
					window_handler(browser)
					soup = BeautifulSoup(browser.page_source, "html.parser")
			# print('mark 5')
			else:
				break

		try:
			link = element1['src']
		except:
			link = 'EMPTY'
		img_df.iloc[i, 0] = link

		# map all images
		n = 1
		if N >= 2:
			while img_df.iloc[i, N - 1] == 'N/A':
				print("page" + str(n))
				# while True:
				print('mark 6-1')
				try:
					page_next = browser.find_element_by_css_selector(
						'#app > div > div:nth-child(1) > div:nth-child(8) > div > div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > '
						'div > div > div.section-box > div.mt6 > react-trigger > div > '
						'div.Slideshow__Container-bw1gs6-0.gCuKqa > div.Arrows__Container-sc-1s7bkvt-2.jAYcej > '
						'button:nth-child(3)')
					print('mark 6-2')
					page_next.click()
					print('mark 6-3')
				except:
					print('mark 7-1')
					# time.sleep(1)
					window_handler(browser)
					soup = BeautifulSoup(browser.page_source, "html.parser")
					print('mark 7-2')
					count = browser.find_element_by_css_selector(
						'#app > div > div:nth-child(1) > div:nth-child(8) > div > '
						'div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > div > '
						'div.Generic__ContentBox-sc-1itie0w-0.cPiuYB.content > '
						'div.section-box > div.mt6 > react-trigger > div > '
						'div.Slideshow__Container-bw1gs6-0.gCuKqa > '
						'div.Slideshow__SlideContainer-bw1gs6-1.kcTrLh > div > span')
					compare = count.text.split(' of ')
					print(compare)
					if compare[0] != compare[1] and int(compare[0]) <= n:
						print('mark 8-1')
						page_next = browser.find_element_by_css_selector(
							'#app > div > div:nth-child(1) > div:nth-child(8) > div > div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > '
							'div > div > div.section-box > div.mt6 > react-trigger > div > '
							'div.Slideshow__Container-bw1gs6-0.gCuKqa > div.Arrows__Container-sc-1s7bkvt-2.jAYcej > '
							'button:nth-child(3)')
						print('mark 8-2')
						location = page_next.location
						size = page_next.size
						print('mark 8-3')
						browser.execute_script("window.scrollTo({0}, {1})".format(0, location['y']-size['height']*2))
						print('mark 8-4')
						while True:
							try:
								page_next.click()
							except:
								window_handler(browser)
							else:
								break
					else:
						print('mark 8-break')
						break
			# else:
			# 	break

				print("link and ...")
				while True:
					try:
						soup = BeautifulSoup(browser.page_source, "html.parser")
						element1 = \
							soup.find_all("img", {"class": "SlideshowInContent__SlideImage-ecnkfw-2 tSQUx"})[0]
						count = browser.find_element_by_css_selector(
							'#app > div > div:nth-child(1) > div:nth-child(8) > div > '
							'div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > div > '
							'div.Generic__ContentBox-sc-1itie0w-0.cPiuYB.content > '
							'div.section-box > div.mt6 > react-trigger > div > '
							'div.Slideshow__Container-bw1gs6-0.gCuKqa > '
							'div.Slideshow__SlideContainer-bw1gs6-1.kcTrLh > div > span')
						n = int(count.text.split(' of ')[0]) - 1
					except:
						try:
							window_handler(browser)
							soup = BeautifulSoup(browser.page_source, "html.parser")
							element1 = \
								soup.find_all("img", {"class": "SlideshowInContent__SlideImage-ecnkfw-2 tSQUx"})[0]
							count = browser.find_element_by_css_selector(
								'#app > div > div:nth-child(1) > div:nth-child(8) > div > '
								'div.Cell-sc-1abjmm4-0.kXBDnR.mb0 > div > '
								'div.Generic__ContentBox-sc-1itie0w-0.cPiuYB.content > '
								'div.section-box > div.mt6 > react-trigger > div > '
								'div.Slideshow__Container-bw1gs6-0.gCuKqa > '
								'div.Slideshow__SlideContainer-bw1gs6-1.kcTrLh > div > span')
							n = int(count.text.split(' of ')[0]) - 1
						except:
							window_handler2(browser)
					else:
						break

				try:
					link = element1['src']
				except:
					link = 'EMPTY'
				if img_df.iloc[i, n] == 'N/A':
					img_df.iloc[i, n] = link
				print('Time {0} finished'.format(n))
				n += 1

	browser.close()

# img_df.to_csv('campus/image links new 5.csv')
img_df.to_csv('campus/image links new 9.csv')
record_df.to_csv('campus/image count.csv')
# print(img_df.iloc[111, :])
