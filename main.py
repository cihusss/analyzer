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
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)

total_results = 10

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

		# path = '/usr/bin/chromedriver'
		path = '/home/admin/scraper/chromedriver'
		# path = '/Users/tmilicevic/Documents/python_scraper/chromedriver'
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
				global total_results
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
				outputData(parameters, scrape_data)

		# already checked if retailer is supported
		else:
			None
			# print('Non-supported retailer')

	def outputData(parameters, scrape_data):
		print('Calculating data...')
		
		# write scrape_data into a local data.json file
		with open('data.json', 'w', encoding='utf-8') as f:
			json.dump(scrape_data, f, ensure_ascii=False, indent=4)

		# perform calculations
		try:
			global output_data
			dateTimeObj = datetime.now()
			# timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S.%f)")
			timestampStr = dateTimeObj.strftime("%d-%b-%Y-%H-%M-%S")
			fileStamp = dateTimeObj.strftime('%H%M%S%f')
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
			return
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
				'timestamp' : timestampStr,
				'retailer' : parameters['retailer'],
				'zipcode' : parameters['zipcode'],
				'category' : parameters['category'],
				'product' : parameters['product'],
				'avg_price' : avg_price,
				'avg_position' : avg_position,
				'shelf_share' : shelf_share + '%'
			})

			# output_data = scrape_data

			# write res_data into a local data.json file
			with open(f'res_data_{fileStamp}.json', 'w', encoding='utf-8') as f:
				json.dump(calc_data, f, ensure_ascii=False, indent=4)

			output_data = calc_data
			sendEmail(fileStamp)

	def sendEmail(fileStamp):
		smtp_server = 'smtp.frontier.com'
		subject = 'An email with attachment from Python'
		body = 'This is an email with attachment sent from Python'
		sender_email = 'cihusss@frontier.com'
		receiver_email = 'cihusss@gmail.com'
		password = input('Type your password and press enter:')

		# create a multipart message and set headers
		message = MIMEMultipart()
		message['From'] = sender_email
		message['To'] = receiver_email
		message['Subject'] = subject
		message['Bcc'] = receiver_email # recommended for mass emails

		# add body to email
		message.attach(MIMEText(body, 'plain'))

		filename = f'res_data/res_data_{fileStamp}.json' # in same directory as script

		# open a file in binary mode
		with open(filename, 'rb') as attachment:
		    # add file as application/octet-stream
		    # email client can usually download this automatically as attachment
		    part = MIMEBase('application', 'octet-stream')
		    part.set_payload(attachment.read())

		# encode file in ASCII characters to send by email    
		encoders.encode_base64(part)

		# add header as key/value pair to attachment part
		part.add_header(
		    'Content-Disposition',
		    f'attachment; filename= {filename}',
		)

		# add attachment to message and convert message to string
		message.attach(part)
		text = message.as_string()

		# log in to server using secure context and send email
		context = ssl.create_default_context()
		with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
		    server.login(sender_email, password)
		    server.sendmail(sender_email, receiver_email, text)

	setup()

	# return 'Successful scrape!'
	return json.dumps(output_data, indent = 4)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=7777, debug=True)
