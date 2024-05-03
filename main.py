from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from bs4 import BeautifulSoup

from schema import Merchant as SchemaMerchant
from schema import Category as SchemaCategory
from schema import MerchantGarage as SchemaMerchantGarage

from models import Merchant as ModelMerchant
from models import Category as ModelCategory
from models import MerchantGarage as ModelMerchantGarage

import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import or_, and_
from sqlalchemy import func

import requests

from pandasai import SmartDataframe, Agent
from pandasai.llm.openai import OpenAI
import pandas as pd
import numpy as np
import psycopg2

import re
import time
import random
import string  # For generating random strings

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

def find_logo_url(website_url):
    try:
        response = requests.get(website_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        logo_image = soup.find('img', alt=lambda value: value and 'logo' in value.lower())
        
        if logo_image:
            logo_src = logo_image.get('src')
            return requests.compat.urljoin(website_url, logo_src)
    except Exception as e:
        print(f"Error finding logo for {website_url}: {e}")
    return ""

def get_data_google(query):
    searchTextData = {
        "textQuery": query
    }

    searchTextHeaders = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GOOGLE_PLACE_API_KEY"),
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.primaryTypeDisplayName,places.location"
    }

    results = {}
    response = requests.post(os.getenv("SEARCHTEXT_URL"), json=searchTextData, headers=searchTextHeaders)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        results["name"] = data["places"][0]["displayName"]["text"]
        results["sub_name"] = data["places"][0]["displayName"]["text"]
        if data["places"][0].get("primaryTypeDisplayName") != None:
            results["category"] = data["places"][0]["primaryTypeDisplayName"]["text"]
        else:
            results["category"] = ""
        results["merchant_code"] = ""
        results["category_id"] = None # get from our model
        results["address"] = data["places"][0]["formattedAddress"]
        results["latitude"] = data["places"][0]["location"]["latitude"]
        results["longitude"] = data["places"][0]["location"]["longitude"]

        response = requests.get(str(os.getenv("SEARCHPLACES_URL"))+"place_id="+str(data["places"][0]["id"])+"&fields=website"+"&key="+str(os.getenv("GOOGLE_PLACE_API_KEY")))
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            if data["result"].get("website") != None:
                results["website"] = data["result"]["website"]
                results["logo"] = find_logo_url(results["website"])
            else:
                results["website"] = ""
                results["logo"] = ""

        # Check if existing in db
        db = SessionLocal()
        existing_data = db.query(ModelMerchantGarage).filter(ModelMerchantGarage.name==results["name"]).first()
        if existing_data:
            return existing_data
        else:
            new_data = ModelMerchantGarage(name=results["name"], sub_name=results["sub_name"], merchant_code=results["merchant_code"], category_id=results["category_id"],  logo=results["logo"], website=results["website"], latitude=results["latitude"], longitude=results["longitude"], address=results["address"])
            db.add(new_data)
            db.commit()
            db.refresh(new_data)
            return new_data

    else:
        # Print an error message if the request failed
        error_message = {}
        error_message["statusCode"] = response.status_code
        error_message["message"] = response._content
        return error_message

# Function to retrieve data merchant
def get_data_merchant(merchant_name):
    start_time = time.time()
    db = SessionLocal()
    try:
        # Execute the query
        merchant = db.query(ModelMerchant).filter(
            or_(
                and_(
                    or_(
                        func.similarity(ModelMerchant.name, merchant_name) > 0.4,
                        func.similarity(ModelMerchant.sub_name, merchant_name) > 0.4,
                        func.similarity(ModelMerchant.website, merchant_name) > 0.25
                    ),
                    func.similarity(ModelMerchant.address, merchant_name) > 0.05
                ),
                func.similarity(ModelMerchant.name, merchant_name) > 0.45,
                func.similarity(ModelMerchant.sub_name, merchant_name) > 0.45
            )
        ).first()
        if merchant != None:
            # Return the result
            end_time = time.time()
            execution_time = end_time-start_time
            print(f"Execution time for using similarity: {execution_time:.2f} seconds")
            return merchant
        else:
            google_data = get_data_google(merchant_name)
            end_time = time.time()
            execution_time = end_time-start_time
            print(f"Execution time for using similarity: {execution_time:.2f} seconds")
            return google_data
    finally:
        # Close the session
        db.close()

# Function to lowercase a string
def lowercase_str(x):        
    if isinstance(x, str):
        return x.lower()
    else:
        return x

# Function to test Pandas AI
def test_pandas_ai_search(merchant_name):
    start_time = time.time()
    db = SessionLocal()

    try:
        # Specify the columns you want to retrieve
        columns_to_query = [
            ModelMerchant.merchant_code,
            ModelMerchant.name,
            ModelMerchant.sub_name,
            ModelMerchant.address,
            ModelMerchant.website
        ]
        # Execute the query
        merchants = db.query(*columns_to_query).all()
        # Convert results to DataFrame
        df = pd.DataFrame(merchants)
        print(df.head())
        # Apply lowercase function to all string columns
        # lowered_df = df.applymap(lowercase_str)
        # print(lowered_df.head())

        llm = OpenAI(api_token=os.getenv("OPENAI_API_KEY"))
        bot = SmartDataframe(df, config={"custom_whitelisted_dependencies": ["collections","fuzzywuzzy"],'llm':llm, 'verbose': True})

        response = bot.chat('cari data dengan name, sub_name, website, atau address yang meliputi' + merchant_name)
        #response = bot.chat('return merchant_code based on the input name ' + merchant_name)
        print(response)
        end_time = time.time()
        execution_time = end_time-start_time
        print(f"Execution time using Pandas AI: {execution_time:.2f} seconds")
        return response
    finally:
        # Close the session
        db.close()

def test_full_text_search_postgre(merchant_name):
    try:
        start_time = time.time()
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(dbname=os.getenv("DATABASE"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"))

        # Create a cursor object
        cur = conn.cursor()

        # Improved search query using parentheses for clarity
        search_query = """SELECT * 
                        FROM merchants m 
                        WHERE (m.name @@ to_tsquery(%s) 
                                or m.sub_name @@ to_tsquery(%s)
                                or m.website @@ to_tsquery(%s)
                                and m.address @@ to_tsquery(%s))
                                or m.name @@ to_tsquery(%s)
                                or m.sub_name @@ to_tsquery(%s)
                        LIMIT 1"""
        # Regular expression to split on whitespace and create OR clauses
        pattern = r"\s+"
        search_terms = re.sub(pattern, "&", merchant_name)  # Replace whitespace with " | "
        print(search_terms)
        # Execute the query with parameter substitution for security
        cur.execute(search_query, (search_terms, search_terms, search_terms, search_terms, search_terms, search_terms))  # Repeat search_terms six times

        # Fetch all matching rows
        rows = cur.fetchall()

        # Process the results (e.g., print or store in a variable)
        if rows:
            print("Found merchants:")
            for row in rows:
                print(row)  # Print each merchant's details
        else:
            print("No merchants found matching the search criteria.")
        end_time = time.time()
        execution_time = end_time-start_time
        print(f"Execution time using full text search postgresql: {execution_time:.2f} seconds")
        return rows
    except Exception as e:
        print("Error:", e)
    finally:
        # Close the cursor
        cur.close()

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
    result["transactionDetail"] = detail
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

# Retrieve all data from merchants_garage table
@app.get("/api/merchants-garage")
async def get_merchants_garage_item():
    db = SessionLocal()
    merchants_garage = db.query(ModelMerchantGarage).all()
    db.close()
    return {"merchantGarage": merchants_garage}

# Retrieve data merchant
@app.post("/api/get-data-merchant")
async def data_merchant(m: DataMerchant):
    return get_data_merchant(m.name)

# Categorize with LLM
@app.post("/api/categorize-transaction")
async def categorize_transaction(t: Transaction):
    return get_category(t)

# Testing Pandas AI to embedded in searching
@app.post("/api/test-pandas-ai")
async def test_pandas_ai(m: DataMerchant):
    return test_pandas_ai_search(m.name)

# Testing posgresql full text search capability
@app.post("/api/test-full-text-search-postgre")
async def test_full_text_search(m: DataMerchant):
    return test_full_text_search_postgre(m.name)

@app.post("/api/inject-data")
async def inject_data():

    # Number of random merchants to generate
    num_merchants = 800000

    # Category options (replace with your actual category IDs)
    category_options = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # Example category IDs

    # Function to generate random string of specified length
    def generate_random_string(length):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))

    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(dbname=os.getenv("DATABASE"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"))

        # Create a cursor object
        cur = conn.cursor()

        # Generate random data for each merchant
        for _ in range(num_merchants):
            name = generate_random_string(10)  # Adjust length as needed
            sub_name = generate_random_string(15)  # Adjust length as needed
            merchant_code = generate_random_string(10)
            category_id = random.choice(category_options)  # Choose random category
            logo = "https://via.placeholder.com/150"  # Example placeholder logo
            website = f"https://www.{generate_random_string(10)}.com"  # Example website
            latitude = random.uniform(-90, 90)  # Random latitude within range
            longitude = random.uniform(-180, 180)  # Random longitude within range
            address = generate_random_string(30) + " Street"  # Example address
            
            # Insert query with parameter substitution for security
            insert_query = """
            INSERT INTO merchants_garage (name, sub_name, merchant_code, category_id, logo, website, latitude, longitude, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            # Execute the query with parameters
            cur.execute(insert_query, (name, sub_name, merchant_code, category_id, logo, website, latitude, longitude, address))

        # Commit the changes
        conn.commit()

        print(f"Successfully generated {num_merchants} random merchants.")
        return "Successfully generated {num_merchants} random merchants."

    except Exception as e:
        print("Error:", e)
        # Rollback any changes in case of errors
        conn.rollback()

    finally:
        # Close the cursor and connection
        cur.close()
        conn.close()
        

if __name__ == "__main__":
    server = run(app, host="0.0.0.0", port=8000)