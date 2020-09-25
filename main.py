from flask import Flask, escape, request, render_template
import scraper
import json

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

		print(f'printing Params class {p.category}')

		run()

	return render_template("home.html")
	sys.exit()

def run():
	print ('Im running here`')

@app.route('/scrape', methods = ['GET', 'POST'])
def scrape():

	scraper.setup()

	return 'Successful scrape!'
	# return json.dumps(scraper.output_data, indent = 4)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=9000, debug=True)
