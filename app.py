from flask import Flask, render_template, request, render_template_string,redirect,url_for
import warnings
import pandas as pd
from time import sleep
from datetime import datetime,timedelta
warnings.filterwarnings("ignore")
from amazon_paapi import AmazonApi
from amazon_paapi.errors.exceptions import RequestError
import os
import ml
import re
import product_fetch
import work
import main
import multiprocessing

app = Flask(__name__)


pf=multiprocessing.Process(target=product_fetch.gen_product)

start_date=None
end_date=None
one_month_ago_str=None

def check(api_key,api_secret,associate_tag):
    amazon = AmazonApi(api_key, api_secret, associate_tag, country="IN")

    items = amazon.get_items(["B07L6YYK6B"])
    # print(search_result)

    # Iterate over the products and add the product data to the DataFrame
    for item in items:
        Title = str(item.item_info.title.display_value)
    if Title:
        return True
    else:
        return False

message = "API details are correct."

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/submit',methods=["POST"])
def submit():
    try:
        # Handle the POST request to /check_api here
        # Check the API details and display a message
        api_key = request.form.get('api_key')
        secret_key = request.form.get('secret_key')
        tag = request.form.get('associate_tag')
        api_file=request.files['api_file']
        # Check the API details
        if check(api_key, secret_key, tag):
            message = "API details are correct."
            file_path = os.path.join(os.path.dirname(__file__), api_file.filename)
            file_path = os.sep.join(file_path.split(os.sep)[:-1] + ["data.xlsx"])
            print(file_path)
            api_file.save(file_path)
            credentials = f"{api_key}\n{secret_key}\n{tag}"
            with open('api_credentials.txt', 'w') as file:
                file.write(credentials)
            # sleep(5)
            pf.start()
            ml.model("data.xlsx")

            return redirect(url_for('success'))            
        else:
            message = "Enter the correct details."
            print(message)
            return render_template('index.html', message=message)
        
    except RequestError as e:
        message = "Enter the correct details."
        print(message)
        return render_template('index.html', message=message)
        

@app.route('/success')
def success():
    return redirect(url_for('dash'))


def dates(file):
    global start_date,end_date,one_month_ago_str
    gt=pd.read_excel(file,sheet_name="Fee-Earnings")

    gts=gt.columns[0]
    date_pattern = r'\d{2}-\d{2}-\d{4}'

    # Find all matches of dates in the text
    dates = re.findall(date_pattern, gts)

    formtdts=[]
    for i in dates:
        # Convert the date to the "2023-10-27" format
        date_obj = datetime.strptime(i, "%m-%d-%Y")
        formtdts.append(date_obj.strftime("%Y-%m-%d")) 

    # Extract the start and end dates
    start_date = formtdts[0]

    end_date = formtdts[1]
    date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    one_month_ago = date_obj - timedelta(days=30)

    # Format the result back to "YYYY-MM-DD" format
    one_month_ago_str = one_month_ago.strftime("%Y-%m-%d")

def summary(file):
    sm=pd.read_excel(file,sheet_name="Fee-Tracking")
    sm.columns=sm.iloc[0]
    sm=sm[1:]
    return sm

@app.route('/dash', methods=['GET', 'POST'])
def dash():
    dates("data.xlsx")
    sm=summary("data.xlsx")
    global default_from_date, default_to_date

    if request.method == 'POST':
        from_date = request.form.get('from_date')
        to_date = request.form.get('to_date')
    
        # Parse the user-provided dates, or use the default values
        try:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
            to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
        except ValueError:
            # Handle invalid date format
            from_date = default_from_date
            to_date = default_to_date

    else:
        from_date = one_month_ago_str
        to_date = end_date

    # Update default values
    default_from_date = from_date
    default_to_date = to_date
    print(f"from date {default_from_date}")
    # Pass from_date and to_date to your function
    max_fee,mx_quan=main.main("data.xlsx", from_date, to_date)
    print(mx_quan)
    max_fee = max_fee[pd.to_datetime(max_fee['Date Shipped'], format='%Y-%m-%d', errors='coerce').notna()]
    max_fee['Date Shipped'] = pd.to_datetime(max_fee['Date Shipped'], format='%Y-%m-%d')
    max_fee['Date Shipped'] = max_fee['Date Shipped'].dt.strftime('%Y-%m-%d')
    max_fee=max_fee.drop("Direct Sale",axis=1)
    mx_fee = max_fee.to_dict(orient='records')
    mx_quan=mx_quan.to_dict(orient='records')
    sm=sm.to_dict(orient='records')
    return render_template('dash.html',sm=sm,mx_fee=mx_fee,mx_quan=mx_quan,start_date=start_date,end_date=end_date, from_date=from_date, to_date=to_date)

# product_details = 'product_details.xlsx'


@app.route('/data', methods=['GET'])
def data():
    df = pd.read_excel("data.xlsx", sheet_name="Fee-Earnings")
    df.columns = df.iloc[0]
    df = df[pd.to_datetime(df['Date Shipped'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna()]
    df['Date Shipped'] = pd.to_datetime(df['Date Shipped'])
    df['Date Shipped'] = df['Date Shipped'].dt.strftime('%Y-%m-%d')
    df=df.drop("Direct Sale",axis=1)
    # print(df['Date Shipped']) 
    data = df.to_dict(orient='records')
    return render_template('excel_products.html', data=data)





@app.route('/get_recommendations', methods=['GET','POST'])
def get_recommendations():
    if pf.is_alive():
        return render_template_string("<p style= text-align:center;font-size:16px;font-style:italic;font-family:sans-serif;>Wait for sometime to fetch the products... try again after sometime..</p>")
    else:
        if work.prediction("product_details.xlsx"):
            products=pd.read_excel("product_details.xlsx",sheet_name="Results")
            filter_products=products[products["result"]==0]
            shuffled_products = filter_products.sample(frac=1, random_state=42)
        # Pass the shuffled products to the template
        return render_template('recommendations.html', products=shuffled_products.to_dict(orient='records'))

    
    
if __name__ == '__main__':
    app.run(debug=True)
    
