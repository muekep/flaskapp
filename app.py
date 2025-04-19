from flask import Flask, render_template, request, redirect, url_for, Response, make_response
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from urllib.parse import quote  # Replaced url_quote with quote
import csv

app = Flask(__name__)

# MongoDB setup
uri = "mongodb+srv://muekecosmas:eAT%40Rtze4Ht9ZU9@cluster0.5tmyrg2.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['income_spending']
collection = db['user_data']

# Home route
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit_data():
    if request.method == 'POST':
        age = int(request.form['age'])
        gender = request.form['gender']
        total_income = float(request.form['total_income'])
        data = request.form
        # Collect expenses from checkboxes and text inputs
        utilities = bool(data.get('utilities'))
        entertainment = bool(data.get('entertainment'))
        school_fees = bool(data.get('school_fees'))
        shopping = bool(data.get('shopping'))
        healthcare = bool(data.get('healthcare'))

        expenses = {}

        if utilities:
            amount = data.get('utilities_amt')
            if amount:
                expenses['utilities'] = float(amount)
        if entertainment:
            amount = data.get('entertainment_amt')
            if amount:
                expenses['entertainment'] = float(amount)
        if school_fees:
            amount = data.get('school_fees_amt')
            if amount:
                expenses['school_fees'] = float(amount)
        if shopping:
            amount = data.get('shopping_amt')
            if amount:
                expenses['shopping'] = float(amount)
        if healthcare:
            amount = data.get('healthcare_amt')
            if amount:
                expenses['healthcare'] = float(amount)

        # Create user data
        user_data = {
            'age': age,
            'gender': gender,
            'total_income': total_income,
            **expenses
        }

        # Insert user data into MongoDB
        collection.insert_one(user_data)

        return redirect(url_for('index'))

# Route to export data to CSV and process in Jupyter notebook
@app.route('/export', methods=['GET'])
def export_data():
    # Fetch data from MongoDB
    exported_data = list(collection.find())
    data = pd.DataFrame(exported_data)

    # Processing: Calculate total spending
    # Use the actual keys that might be present in your MongoDB documents
    expense_columns = ['utilities', 'entertainment', 'school_fees', 'shopping', 'healthcare']
    present_columns = [col for col in expense_columns if col in data.columns]

    if present_columns:
        data['total_spent'] = data[present_columns].sum(axis=1)
    else:
        data['total_spent'] = 0.0  # Or handle the case where no expenses are present

    response = make_response(data.to_csv(encoding='utf-8', index=False, header=True))
    response.headers["Content-Disposition"] = "attachment; filename=data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

from werkzeug.middleware.proxy_fix import ProxyFix

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0')
