from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI

from schema import Merchant as SchemaMerchant
from schema import Category as SchemaCategory
from schema import Merchant
from schema import Category
from models import Merchant as ModelMerchant
from models import Category as ModelCategory

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_

import requests

# Load .env file
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up sqlalchemy
engine = create_engine(os.getenv("DB_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

"""
trx_body = {
    "description": "FAMI FAMILY MART PEJOMPONGAN",
    "entry_type": "outgoing",
    "amount": 20000.00,
    "iso_currency_code": "Rupiah",
    "date": "2023-01-01",
    "transaction_id": "4yp49x3tbj9mD8DB4fM8DDY6Yxbx8YP14g565Xketw3tFmn",
    "country": "ID",
    "account_holder_id": "id-1",
    "account_holder_type": "consumer"
}
"""

def get_data_google(query):
    data = {
        "textQuery": query
    }

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GOOGLE_PLACE_API_KEY")
    }

    response = requests.post(os.getenv("BASE_URL"), json=data, headers=headers)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        print(data)
        return data['results'][0]
    else:
        # Print an error message if the request failed
        return None

# Function to retrieve data merchant
def get_data_merchant(merchant_name):
    db = SessionLocal()
    try:
        # Execute the query
        merchant = db.query(ModelMerchant).filter(or_(
                str(ModelMerchant.sub_name).lower() == merchant_name.lower(),
                ModelMerchant.sub_name.ilike(f"%{merchant_name}%")
            )).first()
        if merchant != None:
            # Return the result
            return merchant
        else:
            return None
    finally:
        # Close the session
        db.close()

# Function to retrieve data category
def get_category(detail):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Kamu adalah personal financial manager"},
            {"role": "user", "content": "Kategorisasikan data transaksi berikut " + str(detail) + " dengan kategori ['Uang Keluar','Tabungan & Investasi', 'Pinjaman', 'Tagihan', 'Hadiah & Amal', 'Transportasi', 'Belanja', 'Top Up', 'Hiburan', 'Makanan & Minuman', 'Biaya & Lainnya', 'Hobi & Gaya Hidup', 'Perawatan Diri', 'Kesehatan', 'Pendidikan', 'Uang Masuk', 'Gaji', 'Pencairan Investasi', 'Bunga', 'Refund', 'Pencairan Pinjaman', 'Cashback'] jawab hanya dengan kategorinya saja. Jika input data transaksi terlalu random atau tidak dapat dimengerti atau tidak memiliki arti, masukkan ke dalam kateogri 'Other'"}
        ]
    )
    result = {}
    result["transaction_detail"] = detail
    result["category"] = vars(completion.choices[0].message)["content"]
    return result

app = FastAPI()

# to avoid csrftokenError
app.add_middleware(DBSessionMiddleware, db_url=os.getenv("DB_URL"))

# Model for transaction
class Transaction(BaseModel):
    description: str
    entry_type: str
    amount: float
    iso_currency_code: str
    date: str
    transaction_id: str
    country: str
    account_holder_id: str
    account_holder_type: str

# Model for merchant
class DataMerchant(BaseModel):
    name: str

@app.get("/")
async def home():
    return {"messages": "Welcome to API services"}

# Retrieve all data from merchants table
@app.get("/api/merchants")
async def get_merchants():
    db = SessionLocal()
    merchants = db.query(ModelMerchant).all()
    db.close()
    return {"merchants": merchants}

# Retrieve all data from categories table
@app.get("/api/categories")
async def get_categories():
    db = SessionLocal()
    categories = db.query(ModelCategory).all()
    db.close()
    return {"categories": categories}

# Retrieve data merchant
@app.post("/api/get-data-merchant")
async def data_merchant(m: DataMerchant):
    return get_data_merchant(m.name)

# Categorize with LLM
@app.post("/api/categorize-transaction")
async def categorize_transaction(t: Transaction):
    return get_category(t)