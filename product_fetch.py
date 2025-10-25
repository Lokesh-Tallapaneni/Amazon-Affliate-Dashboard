from amazon_paapi import AmazonApi
import pandas as pd
from time import sleep



# Create a DataFrame
product_data_list = []
keyword=["deals","electronics","mobiles","today deals","offers","kitchen ware","sports","shirts","men shirts","appliances","pants","shoes","toys","laptops","bags","wallets","hand bags","saree","televisions","ear buds","mobile accessories","watches","grocery","household supplies"]
def gen_product(KEY, SECRET, TAG):
    def search_product(i):
        amazon = AmazonApi(KEY, SECRET, TAG, country='IN', throttling=1)
        search_result = amazon.search_items(keywords=i)
        # print(search_result)
        products = search_result._items

        # Iterate over the products and add the product data to the DataFrame
        for item in products:
            try:
                Title = str(item.item_info.title.display_value)
                # print(Title)
            except Exception as e:
                Title=None
            try:
                current_price = int(float(item.offers.listings[0].price.amount))
                # print(current_price)
            except Exception as e:
                current_price=None
            try:
                original_price = int(float(item.offers.listings[0].saving_basis.amount))
                # print(original_price)
            except Exception as e:
                # discount = int(float(item.offers.listings[0].price.savings.percentage))
                original_price=None
            try:
                primary_image=str(item.images.primary.large.url)
                # print(primary_image)
            except Exception as e:
                primary_image=None
            genlink = item.detail_page_url
            # print(genlink)
            product_data = {
            'Product_Name': Title,
            'Primary_Image': primary_image,
            'Original_Price': original_price,
            'Current_Price': current_price,
            'Product_Link': genlink
        }
            product_data_list.append(product_data)
            # print(f'products are found..')

    for i in keyword:
        search_product(i)
        sleep(2)

    df = pd.DataFrame(product_data_list)
    sht_name="Product_details"
    # Create an Excel writer object
    with pd.ExcelWriter('product_details.xlsx', engine='xlsxwriter') as writer:
        # Write the DataFrame to the Excel file
        df.to_excel(writer, sheet_name=sht_name, index=False)
    
    return True

# gen_product()