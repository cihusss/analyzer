from flask import Flask, escape, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import os
import time
import json
import sys
from datetime import datetime

# set up the browser and get url parameters
def setup():
	chrome_options = Options()
	
	# chrome_options.add_argument('--headless')
	chrome_options.add_argument('user-agent=Mozilla/5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Mobile/11B554a')
	# chrome_options.add_argument('--disable-extensions')
	# chrome_options.add_argument('--profile-directory=Default')
	# chrome_options.add_argument('--incognito')
	# chrome_options.add_argument('--disable-plugins-discovery')
	# chrome_options.add_argument('--start-maximized')
	# chrome_options.add_argument('enable-automation');
	chrome_options.add_argument('--window-size=960,1010');
	# chrome_options.add_argument('start-maximized')
	# chrome_options.add_argument('--no-sandbox');
	# chrome_options.add_argument('--disable-extensions');
	# chrome_options.add_argument('--dns-prefetch-disable');
	# chrome_options.add_argument('--disable-gpu');

	path = '/Users/tmilicevic/Documents/python_scraper/chromedriver'

	# urls = ['https://www.walmart.com/ip/Hostess-Voortman-Vanilla-Wafers-10-6oz/782930556', 'https://www.target.com/p/voortman-vanilla-wafers-10-6oz/-/A-14775958#lnk=sametab']
	urls = [
	'https://www.amazon.com/Ragu-Old-World-Style-Traditional/dp/B000Q3G3HU/ref=sr_1_4_0o_fs?almBrandId=QW1hem9uIEZyZXNo&dchild=1&fpw=alm&keywords=Ragu+Old+World+Style+Traditional+Pasta+Sauce&qid=1601559449&sr=8-4',
	'https://www.walmart.com/ip/Rag-Old-World-Style-Traditional-Sauce-24-oz/10291037',
	'https://www.target.com/p/ragu-old-world-style-traditional-pasta-sauce-24oz/-/A-12935613#lnk=sametab'
	]
	zipcodes = ['60007', '33716', '90210', '80002', '33603', '70032', '75001', '94016', '80031', '10017', '29401']
	# zipcodes = ['36101', '99801', '85001', '72201', '94203', '80201', '06101', '19901', '32301', '30301', '96801', '83701', '62701', '46201', '50301', '66601', '40601', '70801', '04330', '21401', '02108', '48901', '55101', '39201', '65101', '59601', '68501', '89701', '03301', '08601', '87501', '12201', '27601', '58501', '43201', '73101', '97301', '17101', '02901', '29201', '57501', '37201', '73301', '84101', '05601', '23218', '98501', '25301', '53701', '82001']
	retailers = ['amazon', 'walmart', 'target']

	# generate dict using comprehension
	# sku_data = {zipcode: {ret: '' for ret in retailers} for zipcode in zipcodes}
	sku_data = {zipcode: {ret: {'price': 'null', 'delivery': 'null', 'pickup': 'null'} for ret in retailers} for zipcode in zipcodes}
	print('')
	print(100 * '-')
	print('Generating Python dictionary...')
	print('')
	print(sku_data)
	print('')

	# generate dict
	# for zip in zipcodes:
	# 	sku_data.update({zip: {'walmart':'price', 'target':'price'}})
	# print(sku_data)

	# loops over zip codes
	for idx, zipcode in enumerate(zipcodes):
		# print(f'grunting {zipcode}')
		for url in urls:
			# print(f'grunting {url}')
			driver = webdriver.Chrome(path, options=chrome_options)
			driver.set_window_position(960, 0)
			goGet(driver, zipcode, url, sku_data)

	print('ALL DONE HERE!')

def goGet(driver, zipcode, url, sku_data):
	
	# print(url)

	# print(f'getting {zipcode} at {url}')

	#amazon routine
	if url.find('amazon') != -1:
		retailer = 'amazon'

		for attempt in range(3):
			try:
				print(100 * '-')
				print(f'Running Amazon routine in {zipcode}...')
				driver.get(url)

				driver.find_element_by_id('nav-global-location-slot').click()
				time.sleep(1)
				driver.find_element_by_id('GLUXZipUpdateInput').send_keys(zipcode)
				driver.find_element_by_id('GLUXZipUpdateInput').send_keys(Keys.RETURN)
				time.sleep(3)
				driver.save_screenshot('screenshot_amz01.png')
				# driver.find_element_by_id('GLUXZipUpdateInput').send_keys(Keys.ESCAPE)
				# driver.find_element_by_xpath('//*[@id="a-autoid-31-announce"]').click()
				driver.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/span/span/span/button').click()
				time.sleep(1)
				driver.save_screenshot('screenshot_amz02.png')
				aprice = driver.find_element_by_id('priceblock_ourprice').text
				adelivery = driver.find_element_by_xpath('//*[@id="almBuyBox_feature_div"]/div/div/div[1]/div/div[2]/div/span').text
				print(f'{zipcode} AMAZON price: {aprice}')
				print(f'{zipcode} AMAZON delivery: {adelivery}')
				print(f'{zipcode} AMAZON pickup: Pickup not available')
				driver.quit()
				# sku_data[zipcode]['amazon'] = aprice
				sku_data[zipcode][retailer]['price'] = aprice
				sku_data[zipcode][retailer]['delivery'] = adelivery
				sku_data[zipcode][retailer]['pickup'] = 'Pickup not available'
				with open('output/sku_data.json', 'w', encoding='utf-8') as f:
					json.dump(sku_data, f, ensure_ascii=False, indent=4)
			except Exception as e:
				print('Bummer... something went wrong :(')
				print(f'Re-try {attempt + 1}/3')
				if attempt == 2:
					print('Moving on...')
					driver.quit()
				# print(e)
			else:
				break

	# walmart routine
	elif url.find('walmart') != -1:
		retailer = 'walmart'
		for attempt in range(3):
			try:
				print(100 * '-')
				print(f'Running Walmart routine in {zipcode}...')
				driver.get(url)
				
				wmclick = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.XPATH, '//*[@id="header-Header-sparkButton"]/span'))
				)
				wmclick.click()
				time.sleep(1)
				driver.find_element_by_id('vh-location-button').click()
				time.sleep(1)
				driver.find_element_by_id('zipcode-location-form-input').clear()
				driver.find_element_by_id('zipcode-location-form-input').send_keys(zipcode)
				driver.save_screenshot('screenshot01.png')
				driver.find_element_by_id('zipcode-location-form-input').send_keys(Keys.RETURN)
				time.sleep(1)
				# driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/div[1]/section/div[2]/div/div[3]/div[1]/div[2]/div[2]/div/div[2]/div[2]/div[4]/div/div[2]/form/div[2]/button').click()

				driver.save_screenshot('screenshot02.png')
				pwhole = driver.find_element_by_css_selector('span.price-characteristic').text
				pfraction = driver.find_element_by_css_selector('span.price-mantissa').text
				wdelivery = driver.find_element_by_css_selector('.fulfillment-shipping-text > span').text
				wpickup_a = driver.find_element_by_css_selector('.fulfillment-text > span').text
				wpickup_b = driver.find_element_by_css_selector('.fulfillment-text > p > span').text
				wpickup_c = driver.find_element_by_css_selector('.fulfillment-text > p').text
				
				print(f'{zipcode} WALMART price: ${pwhole}.{pfraction}')
				print(f'{zipcode} WALMART delivery: {wdelivery}')
				print(f'{zipcode} WALMART pickup: {wpickup_a}, {wpickup_c}')
				driver.quit()
				# blah_data.update({zipcode:{retailer:{
				# 	'price' : f'{pwhole}.{pfraction}'
				# }}})
				# sku_data[zipcode][retailer]['price'] = f'{pwhole}.{pfraction}'
				# sku_data[zipcode]['walmart'] = f'${pwhole}.{pfraction}'
				sku_data[zipcode][retailer]['price'] = f'${pwhole}.{pfraction}'
				sku_data[zipcode][retailer]['delivery'] = wdelivery
				sku_data[zipcode][retailer]['pickup'] = f'{wpickup_a}, {wpickup_c}'
				with open('output/sku_data.json', 'w', encoding='utf-8') as f:
					json.dump(sku_data, f, ensure_ascii=False, indent=4)
			except Exception as e:
				print('Bummer... something went wrong :(')
				print(f'Re-try {attempt + 1}/3')
				if attempt == 2:
					print('Moving on...')
					driver.quit()
				# print(e)
			else:
				break

	# target routine
	elif url.find('target') != -1:
		retailer = 'target'
		for attempt in range(3):
			try:
				print(100 * '-')
				print(f'Running Target routine in {zipcode}...')
				driver.get(url)
				trclick = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.ID, 'storeId-utilityNavBtn'))
				)
				trclick.click()
				time.sleep(1)
				driver.find_element_by_id('zipOrCityState').send_keys(zipcode)
				time.sleep(1)
				driver.find_element_by_id('zipOrCityState').send_keys(Keys.RETURN)
				time.sleep(1)
				driver.find_element_by_css_selector('.jwSLus:first-child').click()
				time.sleep(1)
				tprice = driver.find_element_by_class_name('style__PriceFontSize-sc-17wlxvr-0').text
				tdelivery_a = driver.find_element_by_xpath('//*[@id="viewport"]/div[5]/div/div[2]/div[3]/div[1]/div/div[2]/div[1]/div[1]/span[1]').text
				tdelivery_b = driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/div/div[2]/div[3]/div[1]/div/div[2]/div[2]/div[2]').text
				tpickup_a = driver.find_element_by_xpath('//*[@id="viewport"]/div[5]/div/div[2]/div[3]/div[1]/div/div[1]/div/div[2]').text
				tpickup_b = driver.find_element_by_css_selector('.cMLLLs').text
				print(f'{zipcode} TARGET price: {tprice}')
				print(f'{zipcode} TARGET delivery: {tdelivery_a}, {tdelivery_b}')
				print(f'{zipcode} TARGET pickup: {tpickup_a} {tpickup_b}')
				driver.quit()
				# blah_data.update({zipcode:{retailer:{
				# 	'price' : tprice
				# }}})
				# sku_data[zipcode][retailer]['price'] = tprice
				# sku_data[zipcode]['target'] = tprice
				sku_data[zipcode][retailer]['price'] = tprice
				sku_data[zipcode][retailer]['delivery'] = f'{tdelivery_a}, {tdelivery_b}'
				sku_data[zipcode][retailer]['pickup'] = f'{tpickup_a} {tpickup_b}'
				with open('output/sku_data.json', 'w', encoding='utf-8') as f:
					json.dump(sku_data, f, ensure_ascii=False, indent=4)
			except Exception as e:
				print('Bummer... something went wrong :(')
				print(f'Re-try {attempt + 1}/3')
				if attempt == 2:
					print('Moving on...')
					driver.quit()
			else:
				break
	else:
		None

setup()