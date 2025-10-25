import pandas as pd
from datetime import datetime, timedelta
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# name="1698492451662-Fee-Earnings-85f7091e-f0a8-4a18-b86c-82f1b689cc09-XLSX.xlsx"
def main(name,from_date,to_date):
    file = pd.ExcelFile(name)

    dict={}
    # getting the sheetnames
    sheet_names = file.sheet_names
    for s in sheet_names:
        dict[s]=s.replace("-","_") if "-" in s else s
    # print(dict)

    new=[]
    for old in dict.values():
        new.append(old)

    ind=0
    for sheet_name in sheet_names:
        sheet = file.parse(sheet_name)
        date=sheet.columns[0]
        sheet.columns=sheet.iloc[0]
        globals()[new[ind]] = sheet
        ind+=1

    # print(globals()[new[1]])

    date_pattern = r'\d{2}-\d{2}-\d{4}'

    # Find all matches of dates in the text
    dates = re.findall(date_pattern, date)

    # Extract the start and end dates
    start_date = dates[0]
    end_date = dates[1]

    print(start_date)
    print(end_date)


    # Convert the start_date and end_date strings to datetime objects
    start_date = datetime.strptime(start_date, "%m-%d-%Y")
    end_date = datetime.strptime(end_date, "%m-%d-%Y")

    # Create a list to store the generated dates
    date_list = []

    # Generate dates from start_date to end_date
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    # # Print the list of dates
    # for date in date_list:
    #     print(date)

    global Fee_Earnings
    global Fee_DailyTrends
    Fee_Earnings.to_csv('data.csv', index=False)
    #Ad_Fee
    # print(Fee_Earnings['Date Shipped'])
    Fee_Earnings = Fee_Earnings[pd.to_datetime(Fee_Earnings['Date Shipped'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna()]
    # Convert the 'Date Shipped' column to datetime with the specified format
    Fee_Earnings['Date Shipped'] = pd.to_datetime(Fee_Earnings['Date Shipped'])
    Fee_Earnings['Date Shipped'] = Fee_Earnings["Date Shipped"].dt.date
    # print(Fee_Earnings["Date Shipped"])


    ##Clicks

    Fee_DailyTrends = Fee_DailyTrends[pd.to_datetime(Fee_DailyTrends['Date'], format='%Y-%m-%d', errors='coerce').notna()]
    Fee_DailyTrends['Date'] = pd.to_datetime(Fee_DailyTrends['Date'])
    Fee_DailyTrends['Date'] = Fee_DailyTrends["Date"].dt.date
    print(Fee_DailyTrends['Date'])

    # print(date_list)

    date_list_df = pd.DataFrame({'Date Shipped': pd.to_datetime(date_list)})
    grouped_data = Fee_Earnings.groupby('Date Shipped')['Ad Fees'].sum().reset_index()
    grouped_data1 = Fee_DailyTrends.groupby('Date')['Clicks'].sum().reset_index()
    grouped_data2 = Fee_DailyTrends.groupby('Date')['Total Items Ordered'].sum().reset_index()
    # print(grouped_data)
    grouped_data['Date Shipped'] = pd.to_datetime(grouped_data['Date Shipped'])
    grouped_data1['Date'] = pd.to_datetime(grouped_data1['Date'])
    grouped_data2['Date'] = pd.to_datetime(grouped_data2['Date'])
    # print(grouped_data)
    merged_data = pd.merge(date_list_df, grouped_data, on='Date Shipped', how='left').fillna({'Ad Fees': 0})
    # print(merged_data)
    merged_data = pd.merge(merged_data, grouped_data1, left_on='Date Shipped',right_on='Date' ,how='left').fillna({'Clicks': 0})
    merged_data = merged_data.drop(columns=['Date'])
    merged_data = pd.merge(merged_data, grouped_data2, left_on='Date Shipped',right_on='Date' ,how='left').fillna({'Total Items Ordered': 0})
    merged_data = merged_data.drop(columns=['Date'])
    

    # print(merged_data)
    if main_dash(merged_data,from_date,to_date):
        pass
    if pie_chart(Fee_Earnings,from_date,to_date):
        pass
    if bar_chart(Fee_Earnings,from_date,to_date):
        pass
    if returns(Fee_Earnings,from_date,to_date):
        pass
    mx_adfee=max_adfee(Fee_Earnings,from_date,to_date)
    mx_quan=max_quantity(Fee_Orders,from_date,to_date)
    print(mx_adfee)
    print(mx_quan)
    print("all set")
    return mx_adfee,mx_quan








def main_dash(merged_data,from_date,to_date):
    # Convert from_date and to_date to datetime objects
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    # Filter the data based on the date range
    filtered_data = merged_data[(merged_data['Date Shipped'] >= from_date) & (merged_data['Date Shipped'] <= to_date)]
    fig, ax1 = plt.subplots(figsize=(18, 9))
    formatted_dates=[]
    datecon=filtered_data["Date Shipped"]
    for i in datecon:
        # Convert the date string to a datetime object
        # Extract the month number and name
        date_num=i.strftime("%d")
        month_name = i.strftime("%b")
        # Append the formatted date to the list
        formatted_dates.append(f"{month_name} {date_num}")
    # Create the bar chart for 'Ad Fees'
    formatted_dates = [pd.to_datetime(date_str, format='%b %d') for date_str in formatted_dates]
    bars = ax1.bar(filtered_data.index, filtered_data['Ad Fees'], color='#58e2c2',label='Ad Fees')
    ax1.set_xticks(filtered_data.index)
    ax1.set_xticklabels(formatted_dates, rotation=90, ha='right')
    plt.title('Ad Fees vs. Date Shipped')
    plt.xlabel('Date Shipped')
    plt.ylabel('Ad Fees')

    # Annotate the bars with Ad Fees values
    for bar, ad_fee in zip(bars, filtered_data['Ad Fees']):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2, height, f'{ad_fee:.2f}₹', ha='center', va='bottom', color='black')

    # Set date format for x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Create a second y-axis for 'Clicks'
    ax2 = ax1.twinx()
    ax2.plot(filtered_data.index, filtered_data['Clicks'], color='#d05254', marker='o', linestyle='-', label='Clicks')

    # Set labels and title for the second y-axis
    ax2.set_ylabel('Clicks', color='#d05254')
    ax2.tick_params(axis='y', labelcolor='#d05254')


    # Annotate the 'Clicks' points with values
    for x, y in zip(filtered_data.index, filtered_data['Clicks']):
        offset = 0.1
        ax2.text(x, y + offset, f'{y}', ha='left', va='bottom', color='#d05254')

    # Create a third y-axis for 'Total Items Ordered'
    ax3 = ax1.twinx()
    ax3.plot(filtered_data.index, filtered_data["Total Items Ordered"], color='#f0b83a', marker='o', linestyle='-', label='Orders')

    ax3.set_ylabel('Orders', color='#f0b83a')
    ax3.tick_params(axis='y', labelcolor='#f0b83a')

    # Annotate the 'Total Items Ordered' points with values
    for x, y in zip(filtered_data.index, filtered_data["Total Items Ordered"]):
        offset = 0.1
        ax3.text(x, y + offset, f'{y}', ha='left', va='bottom', color='#f0b83a')

    # Create a single legend for all lines
    lines, labels = ax1.get_legend_handles_labels()
    lines += ax2.get_legend_handles_labels()[0]
    lines += ax3.get_legend_handles_labels()[0]
    labels += ax2.get_legend_handles_labels()[1]
    labels += ax3.get_legend_handles_labels()[1]

    ax1.legend(lines, labels, loc='upper right')
    plt.tight_layout()
    plt.savefig(fname="static/images/dash.png",bbox_inches="tight")
    return True





def pie_chart(Z,from_date,to_date):
    # Convert from_date and to_date to datetime objects
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    Z['Date Shipped'] = pd.to_datetime(Z['Date Shipped'])
    Z = Z[(Z['Date Shipped'] >= from_date) & (Z['Date Shipped'] <= to_date)]

    # Count the occurrences of each category
    category_counts = {}
    for category in Z["Category"]:
        category=category.split()[0]
        category_counts[category] = category_counts.get(category, 0) + 1

    # Extract category names and counts
    categories = list(category_counts.keys())
    category_values = list(category_counts.values())
    # Create a pie chart

    fig=plt.figure(figsize=(10, 10),dpi=125)
    gs=fig.add_gridspec(1,1,left= 0, bottom= 0, right= 0.884, top= 0.994, wspace= 0.2, hspace= 0.2)
    ax=fig.add_subplot(gs[0,0])
    ax.pie(category_values, labels=categories, autopct='%1.1f%%', startangle=190, labeldistance=1.05,textprops={"fontsize":7})
    ax.legend(categories, title='Categories', loc='center left', bbox_to_anchor=(1, 0.6))  # Position the legend
    # Display the pie chart
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.savefig(fname="static/images/piepic.png",bbox_inches="tight")
    return True



def max_adfee(X,from_date,to_date):
    # Convert from_date and to_date to datetime objects
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    X['Date Shipped'] = pd.to_datetime(X['Date Shipped'])
    X = X[(X['Date Shipped'] >= from_date) & (X['Date Shipped'] <= to_date)]
    selected_rows = pd.DataFrame()
    
    while len(selected_rows) < 10:
        max_ad_fee_row = X[X['Ad Fees'] == X['Ad Fees'].max()]
        
        if len(max_ad_fee_row) == 0:
            print("No more rows with a negative revenue for the maximum ad fee product found.")
            break
        
        if max_ad_fee_row['Revenue'].values[0] >= 0:
            # Append the max_ad_fee_row to the selected_rows DataFrame
            selected_rows = pd.concat([selected_rows, max_ad_fee_row])
            # Drop the product from the X DataFrame
            X = X[X['ASIN'] != max_ad_fee_row['ASIN'].values[0]]
        else:
            break
    print(selected_rows["Date Shipped"])
    return selected_rows.iloc[0:10]


# max_adfee(Fee_Earnings,from_date,to_date)


def max_quantity(Y,from_date,to_date):
    # Convert from_date and to_date to datetime objects
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    Y = Y[pd.to_datetime(Y['Date'], format='%Y-%m-%d %H:%M:%S', errors='coerce').notna()]
    Y['Date'] = pd.to_datetime(Y['Date'])
    Y = Y[(Y['Date'] >= from_date) & (Y['Date'] <= to_date)]
    max_qaun = Y[Y['Qty'] == Y['Qty'].max()]
    return max_qaun

# max_quantity(Fee_Orders,from_date,to_date)


def bar_chart(Z,from_date,to_date):
    # Convert from_date and to_date to datetime objects
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    Z['Date Shipped'] = pd.to_datetime(Z['Date Shipped'])
    Z = Z[(Z['Date Shipped'] >= from_date) & (Z['Date Shipped'] <= to_date)]

    # Count the occurrences of each category
    category_counts = {}
    for category in Z["Category"]:
        category=category.split()[0]
        category_counts[category] = category_counts.get(category, 0) + 1

    # Extract category names and counts
    categories = list(category_counts.keys())
    category_values = list(category_counts.values())
    df=pd.DataFrame()
    df["Category"]=categories
    df['values']=category_values
    # Create a list of distinct colors for the bars
    colors = plt.cm.viridis(np.linspace(0, 1, len(df)))

    # Create a bar chart
    plt.figure(figsize=(18, 9))  # Set the figure size

    # Create the bar chart with different colors
    bars = plt.bar(df['Category'], df['values'], color=colors)
    plt.xlabel('Category')
    plt.ylabel('No.of Items')
    plt.title('Category vs. No.of Items')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Add values on top of each bar
    for bar, value in zip(bars, df['values']):
        plt.text(bar.get_x() + bar.get_width() / 2 - 0.15, bar.get_height() + 0.2, value, fontsize=10)

    # # Add category names as labels on the bars
    # for bar, category in zip(bars, df['Category']):
    #     plt.text(bar.get_x() + bar.get_width() / 2 - 0.2, -0.8, category, fontsize=10, rotation=45, ha='right')

    # Show the bar chart
    plt.tight_layout()
    plt.savefig(fname="static/images/barpic.png",bbox_inches="tight")
    return True


def returns(r,from_date,to_date):
    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    r['Date Shipped'] = pd.to_datetime(r['Date Shipped'])
    r = r[(r['Date Shipped'] >= from_date) & (r['Date Shipped'] <= to_date)]
    r['Returns'] = r['Returns'].astype(int)
    returns_by_category = r.groupby('Category')['Returns'].sum()
    
    
    short_category_names = returns_by_category.index.str.split().str[0]

    # Create a bar chart
    plt.figure(figsize=(18, 9)) 
    bars = plt.bar(short_category_names, returns_by_category, color="red") 
    plt.xlabel('Category ')
    plt.ylabel('Number of Returns')
    plt.title('Number of Returned Products by Category')
    plt.xticks(rotation=45, ha='right')

    # Add count labels on top of bars
    for bar, count in zip(bars, returns_by_category):
        plt.text(bar.get_x() + bar.get_width() / 2 - 0.15, bar.get_height() + 0.05, count, fontsize=10)
    plt.legend('Returns', loc='upper right')
    plt.tight_layout()
    plt.savefig(fname="static/images/returns.png",bbox_inches="tight")
    return True


