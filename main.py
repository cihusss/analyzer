from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from flask import Flask, escape, request, render_template
import time
import json
import sys

app = Flask(__name__)

class Params:
	def __init__(self):
		self.category = 'category'
		self.product = 'product'
		self.zipcode = 'zipcode'

@app.route('/', methods = ['GET', 'POST'])
def home():

	if request.form:
		print(request.form)
		global p
		p = Params()
		p.category = request.form.get('category')
		p.product = request.form.get('product')
		p.zipcode = request.form.get('zipcode')

		print('printing Params class ' + p.category)

		run()

	return render_template("home.html")

def run():
	print ('Im running here`')

@app.route('/scrape', methods = ['GET', 'POST'])
def scrape():

	# set up the browser and get url parameters
	def setup():
		chrome_options = Options()
		chrome_options.add_argument('enable-automation');
		chrome_options.add_argument('--headless');
		chrome_options.add_argument('--window-size=1920,1080');
		chrome_options.add_argument('--no-sandbox');
		chrome_options.add_argument('--disable-extensions');
		chrome_options.add_argument('--dns-prefetch-disable');
		chrome_options.add_argument('--disable-gpu');

		# path = '/home/admin/scraper/chromedriver'
		path = '/Users/tmilicevic/Documents/python_scraper/chromedriver'
		driver = webdriver.Chrome(path, options=chrome_options)

		retailers = ['amazon', 'walmart', 'target', 'kroger', 'publix', 'albertsons', 'instacart']
		scrape_data = {}
		parameters = {}
		retailer = 'https://www.' + request.args.get('retailer') + '.com'
		zipcode = request.args.get('zipcode')
		category = request.args.get('category')
		product = request.args.get('product')

		# store url parameters/variables in parameters scrape_data
		for variable in ['retailer', 'zipcode', 'category', 'product']:
			parameters[variable] = eval(variable)
		
		# check if retailer is supported
		res = [ele for ele in retailers if(ele in request.args.get('retailer'))] 

		# navigate if retailer is suppored
		if res:
			print('Supported retailer... moving along...')
			navigateSite(driver, parameters, scrape_data)
		else:
			print('Unsupported retailer... stopping the scrape...')
			driver.quit()


	def navigateSite(driver, parameters, scrape_data):
		
		driver.get(parameters['retailer'])

		# walmart routine
		if (parameters['retailer'].find('walmart') != -1):
			print('Navigating: ' + parameters['retailer'])
			
			try:
				wmclick = WebDriverWait(driver, 10).until(
					EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[1]/section/div[5]/div[1]/div[3]/button"))
				)
				wmclick.click()
				driver.implicitly_wait(1)
				wminput = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[1]/section/div[4]/div[1]/div/div[2]/div[1]/div/div[1]/input')
				wminput.send_keys(parameters['zipcode'])
				wminput.send_keys(Keys.TAB)
				wminput.send_keys(Keys.RETURN)
				wmcontinue = driver.find_element_by_xpath('//*[@id="next-day-location-modal"]/div[1]/div/div[2]/div[2]/div/button[1]/span')
				wmcontinue.click()

				wmquery = driver.find_element_by_id('global-search-input')
				wmquery.send_keys(parameters['category'])
				wmquery.send_keys(Keys.RETURN)

				# get and populate scrape_data
				scrapes = driver.find_elements_by_class_name('search-result-gridview-item-wrapper')
				total_results = len(scrapes)
				for idx, scrape in enumerate(scrapes):
					pname = scrape.find_element_by_css_selector('a.product-title-link > span').text
					pwhole = scrape.find_element_by_css_selector('span.price-characteristic').text
					pfraction = scrape.find_element_by_css_selector('span.price-mantissa').text
					if (pname.find(parameters['product']) != -1):
						scrape_data.update({idx: {'name' : pname, 'price' : pwhole, 'fraction' : pfraction}})
					else:
						None
			# print errors
			except Exception as e:
				print('Navigate function error: ' + str(e))

			# wrap up
			finally:
				driver.quit()
				outputData(parameters, scrape_data, total_results)

		# already checked if retailer is supported
		else:
			None
			# print('Non-supported retailer')

	def outputData(parameters, scrape_data, total_results):
		print('Calculating data...')
		
		# write scrape_data into a local data.json file
		with open('data.json', 'w', encoding='utf-8') as f:
			json.dump(scrape_data, f, ensure_ascii=False, indent=4)

		# perform calculations
		try:
			global output_data
			calc_data = {}
			price_sum = 0
			tot_pos = 0
			avg_price = 0
			avg_position = 0
			matched_results = str(len(scrape_data))
			shelf_share = "{:.2f}".format(len(scrape_data) / total_results * 100)

			# add all prices and shelf position indexes
			for i in scrape_data:
				price_sum += float(scrape_data[i]['price'].replace(',','')) + int(scrape_data[i]['fraction']) / 100
				tot_pos += i

			# calculate averages
			avg_position = "{:.0f}".format(int(tot_pos) / int(matched_results))
			avg_price = "{:.2f}".format(price_sum / len(scrape_data))

		# throw & print errors
		except Exception as e:
			print('Output function error: ' + str(e))
		# print calculated output to term
		finally:
			print('-' * 60)
			print('RETAILER: ' + parameters['retailer'])
			print('ZIP CODE: ' + parameters['zipcode'])
			print('CATEGORY: ' + parameters['category'])
			print('TOTAL ' + parameters['category'] + ' on SHELF: ' + str(total_results))
			print('TOTAL ' + parameters['product'] + ' ' + parameters['category'] +' on SHELF: ' + matched_results)
			print(parameters['product'] + ' BRAND SHARE of SHELF: ' + str(shelf_share) + '%')
			print('AVERAGE ' + parameters['product'] + ' PRODUCT PRICE: $' + str(avg_price))
			print('AVERAGE SHELF POSITION: ' + str(avg_position))
			print('-' * 60)

			# populate calc_data dictionary
			calc_data.update({
				'retailer' : parameters['retailer'],
				'zipcode' : parameters['zipcode'],
				'category' : parameters['category'],
				'product' : parameters['product'],
				'avg_price' : avg_price,
				'avg_position' : avg_position,
				'shelf_share' : shelf_share + '%'
			})

			# output_data = scrape_data
			output_data = calc_data

	setup()

	# return 'Successful scrape!'
	return output_data

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=7777, debug=True)