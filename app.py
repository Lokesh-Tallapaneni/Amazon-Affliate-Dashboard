from flask import Flask, render_template, request, render_template_string,redirect,url_for,session,jsonify
import warnings
import pandas as pd
from datetime import datetime,timedelta
warnings.filterwarnings("ignore")
from amazon_paapi import AmazonApi
from amazon_paapi.errors.exceptions import RequestError
import os
import ml
import re
import product_fetch
# import work
import main
import multiprocessing
# from flask_cors import CORS
# import panda_ai
import aichat
import random


app = Flask(__name__)
# CORS(app)
app.secret_key = 'your_secret_key'


KEY=None
SECRET=None
TAG=None

pf=multiprocessing.Process(target=product_fetch.gen_product,args=[KEY, SECRET, TAG])

start_date=None
end_date=None
one_month_ago_str=None

def check(api_key,api_secret,associate_tag):
    amazon = AmazonApi(api_key, api_secret, associate_tag, country="IN")

    items = amazon.get_items(["B07L6YYK6B"])

    # Iterate over the products and add the product data to the DataFrame
    for item in items:
        Title = str(item.item_info.title.display_value)
    if Title:
        return True
    else:
        return False

message = "API details are correct."

@app.route('/', methods=['GET', 'POST'])
def redirect_to_index():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/submit',methods=["POST"])
def submit():
    global pf
    try:
        # Handle the POST request to /check_api here
        # Check the API details and display a message
        api_key = request.form.get('api_key')
        secret_key = request.form.get('secret_key')
        tag = request.form.get('associate_tag')
        api_file=request.files['api_file']
        # Check the API details
        if check(api_key, secret_key, tag):
            session['logged_in'] = True
            KEY, SECRET, TAG = api_key,secret_key,tag
            message = "API details are correct."
            file_path = os.path.join(os.path.dirname(__file__), api_file.filename)
            file_path = os.sep.join(file_path.split(os.sep)[:-1] + ["data.xlsx"])
            print(file_path)
            api_file.save(file_path)
            pf=multiprocessing.Process(target=product_fetch.gen_product,args=[KEY, SECRET, TAG])
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
    if 'logged_in' in session and session['logged_in']:
        return redirect(url_for('dash'))
    else:
        return redirect(url_for('index'))


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
    if 'logged_in' in session and session['logged_in']:
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
    else:
        return redirect(url_for('index'))
# product_details = 'product_details.xlsx'


@app.route('/data', methods=['GET'])
def data():
    if 'logged_in' in session and session['logged_in']:
        df = pd.read_excel("data.xlsx", sheet_name="Fee-Earnings")
        df.columns = df.iloc[0]
        df = df[pd.to_datetime(df['Date Shipped'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna()]
        df['Date Shipped'] = pd.to_datetime(df['Date Shipped'])
        df['Date Shipped'] = df['Date Shipped'].dt.strftime('%Y-%m-%d')
        df=df.drop("Direct Sale",axis=1)
        data = df.to_dict(orient='records')
        return render_template('excel_products.html', data=data)
    else:
        return redirect(url_for('index'))


@app.template_filter('shuffle')
def shuffle_list(lst):
    shuffled_lst = lst[:]
    random.shuffle(shuffled_lst)
    return shuffled_lst


@app.route('/get_recommendations', methods=['GET','POST'])
def get_recommendations():
    if 'logged_in' in session and session['logged_in']:
        if pf.is_alive():
            return render_template_string("<p style= text-align:center;font-size:16px;font-style:italic;font-family:sans-serif;>Wait for sometime to fetch the products... try again after sometime..</p>")
        else:
            if ml.prediction("product_details.xlsx"):
                products=pd.read_excel("product_details.xlsx",sheet_name="Results")
                filter_products=products[products["result"]==0]
                shuffled_products = filter_products.sample(frac=1, random_state=100)
            # Pass the shuffled products to the template
            return render_template('recommendations.html', products=shuffled_products.to_dict(orient='records'))
    else:
        return redirect(url_for('index'))


# Route for user logout
@app.route('/logout', methods=["POST"])
def logout():
    global pf
    session['logged_in']=False
    session.pop('logged_in', None)
    if pf.is_alive():
        pf.terminate()
    try:
        os.remove('data.xlsx')
        os.remove('cmodel_pkl')
        os.remove('feature_extraction')
        os.remove('product_details.xlsx')
        os.remove('data.csv')
        os.remove('api_credintials.txt')
    except:
        pass
    return redirect('/login')


@app.route('/chat')
def chat():
    if 'logged_in' in session and session['logged_in']:
        df=pd.read_excel('data.xlsx',sheet_name='Fee-Earnings')
        df.columns=df.iloc[0]
        df = df[1:].reset_index(drop=True)
        df.to_csv('data.csv')
        return render_template('chat.html')
    else:
        return redirect("/login")


@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.form['user_message']
    print(user_message)
    agent= aichat.load('data.csv')
    res= aichat.chat(agent,user_message)
    print(res)
    # res=input("Enter the input : ")
    return jsonify({'user_message': user_message, 'model_response': res})
            
    # try:
    #     x=panda_ai.inp(user_message)
    #     while "unfortunately" in x.lower():
    #         print('done')
    #         x=panda_ai.inp(user_message)
    # except Exception as e:
    #     try:
    #         x=panda_ai.inp(user_message)
    #     except Exception:
    #         pass
    # # model_response = 'This is a simulated response from the language model.'+x

    # return jsonify({'user_message': user_message, 'model_response': x})

    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
    
