import pandas as pd
import pickle
import openpyxl




def prediction(name):
    # name="1698492451662-Fee-Earnings-85f7091e-f0a8-4a18-b86c-82f1b689cc09-XLSX.xlsx"
    with open('cmodel_pkl', 'rb') as f:
        lr = pickle.load(f)

    with open('feature_extraction','rb') as f:
        feature_extraction=pickle.load(f)

    products="product_details.xlsx"

    sht=pd.read_excel(products,sheet_name="Product_details")
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

    product_name=sht["Product_Name"]
    # print(product_name)

    X_train_features = feature_extraction.transform(product_name)

    pred=lr.predict(X_train_features)

    sht['result'] = pred
    if not pd.ExcelFile("product_details.xlsx").sheet_names.__contains__("Results"):
        with pd.ExcelWriter(products, engine='openpyxl', mode='a') as writer:
            sht.to_excel(writer, sheet_name='Results', index=False)
    else:
        # Delete the Results sheet
        wb = openpyxl.load_workbook(products)
        ws = wb.get_sheet_by_name("Results")
        wb.remove_sheet(ws)
        wb.save(products)
        with pd.ExcelWriter(products, engine='openpyxl', mode='a') as writer:
            sht.to_excel(writer, sheet_name='Results', index=False)
            
    return True

# prediction(name="1698492451662-Fee-Earnings-85f7091e-f0a8-4a18-b86c-82f1b689cc09-XLSX.xlsx")