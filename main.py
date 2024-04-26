from fastapi import FastAPI
from pydantic import BaseModel, Field
from openai import OpenAI
import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# data mockup
mock_data_merchants = [
    {
        "id": 1,
        "name": "Amuya Cafe",
        "sub_name": "Amuya Cafe Kemayoran",
        "merchant_code": "AMYC",
        "category_id": 10,
        "logo": "test-amuya.jpg",
        "website": "https://www.amuyacoffee.com/",
        "latitude": -6.1549693,
        "longitude": 106.8403106,
        "address": "Gedung Graha Kana, Jl. Angkasa 1 No.Kav.4 Blok B16, Gn. Sahari Sel., Kota Jakarta Pusat",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"        
    },
    {
        "id": 2,
        "name": "Family Mart",
        "sub_name": "Family Mart Pejompongan",
        "merchant_code": "FAMI",
        "category_id": 10,
        "logo": "test-fami.jpg",
        "website": "https://www.familymart.co.id/",
        "latitude": -6.20369,
        "longitude": 106.80206,
        "address": "Menara BNI Pejompongan",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"        
    }
]

mock_data_categories = [
    {
        "id": 1,
        "name": "Uang Keluar",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 2,
        "name": "Tabungan & Investasi",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 3,
        "name": "Pinjaman",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 4,
        "name": "Tagihan",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 5,
        "name": "Hadiah & Amal",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 6,
        "name": "Transportasi",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 7,
        "name": "Belanja",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 8,
        "name": "Top Up",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 9,
        "name": "Hiburan",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 10,
        "name": "Makanan & Minuman",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 11,
        "name": "Biaya & Lainnya",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 12,
        "name": "Hobi & Gaya Hidup",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 13,
        "name": "Perawatan Diri",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 14,
        "name": "Kesehatan",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 15,
        "name": "Pendidikan",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 16,
        "name": "Uang Masuk",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 17,
        "name": "Gaji",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 18,
        "name": "Pencairan Investasi",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 19,
        "name": "Bunga",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 20,
        "name": "Refund",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 21,
        "name": "Pencairan Pinjaman",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
    {
        "id": 22,
        "name": "Cashback",
        "created_at": "2023-11-15 01:02:03",
        "updated_at": "2023-11-15 01:02:03"   
    },
]
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

# function to retrieve data merchant
def get_data_merchant(merchant_name, category):
    cat_id = None
    merchant = None
    for cat in mock_data_categories:
        if cat["name"].lower() == category.lower():
            cat_id = cat["id"]
            break
    for merc in mock_data_merchants:
        if merc["category_id"] == cat_id and merc["sub_name"].lower() == merchant_name.lower():
            merchant = merc
            break
    
    return merchant

# function to retrieve data category
def get_category(Transaction):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Kamu adalah personal financial manager"},
            {"role": "user", "content": "Kategorisasikan data transaksi berikut " + str(Transaction) + " dengan kategori ['Uang Keluar','Tabungan & Investasi', 'Pinjaman', 'Tagihan', 'Hadiah & Amal', 'Transportasi', 'Belanja', 'Top Up', 'Hiburan', 'Makanan & Minuman', 'Biaya & Lainnya', 'Hobi & Gaya Hidup', 'Perawatan Diri', 'Kesehatan', 'Pendidikan', 'Uang Masuk', 'Gaji', 'Pencairan Investasi', 'Bunga', 'Refund', 'Pencairan Pinjaman', 'Cashback'] jawab hanya dengan kategorinya saja. Jika input data transaksi terlalu random atau tidak dapat dimengerti atau tidak memiliki arti, masukkan ke dalam kateogri 'Other'"}
        ]
    )
    return completion.choices[0].message

app = FastAPI()

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

class Merchant(BaseModel):
    name: str
    category: str

@app.get("/")
async def home():
    return {"messages": "Welcome to API services"}

# retrieve data merchant
@app.post("/api/data-merchant")
async def data_merchant(m: Merchant):
    return get_data_merchant(m.name, m.category)

# categorize with LLM
@app.post("/api/categorize-transaction")
async def categorize_transaction(t: Transaction):
    return get_category(t)