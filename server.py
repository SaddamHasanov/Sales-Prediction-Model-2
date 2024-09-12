from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import pandas as pd

model = joblib.load('app/GradientBoostingRegressorModel.joblib')
product_codes_list = joblib.load('app/unique_train_values.joblib')

app = FastAPI()

class Item(BaseModel):
    MarketNumber : int
    ProductCode : str
    Day : int
    Month : int

@app.get('/')
def reed_root():
    return {'Massege : Market-Sales-Model API'}

@app.post('/predict')
def predict(data : Item):

    # change it to DataFrame
    df = pd.DataFrame([data.dict().values()], columns = data.dict().keys())

    new_df = pd.DataFrame({'Market Number' : df['MarketNumber'], 
                            'Product Code' : df['ProductCode'], 
                            'Day' : df['Day'],
                            'Month' : df['Month']})
    
    # check if product is in product codes list
    is_in_product_list = False

    for product in product_codes_list:
        if str(new_df['Product Code'][0]) == product:
            is_in_product_list = True
            break

    if is_in_product_list:
        # load encoder
        encoder = joblib.load('app/encoder.joblib')

        new_df['Product Code'] = new_df['Product Code'].map(lambda x: '<unknown>' if x not in encoder.classes_ else x)
        encoder.classes_ = np.append(encoder.classes_, '<unknown>')

        # transform data using encoder
        new_df['Product Code'] = encoder.transform(new_df['Product Code'])

        # predict new data
        prediction = list(model.predict(new_df))
        return prediction[0] 
    else:
        return 'Təxmin edilə bilmir'

    