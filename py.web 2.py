from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import openai
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="MarketMind AI Backend")

# Database setup
engine = create_engine("sqlite:///marketmind.db")

# ----------------------------
# Data Models
# ----------------------------

class SalesData(BaseModel):
    product_name: str
    sales: float
    marketing_spend: float

class MarketingPrompt(BaseModel):
    prompt: str

# ----------------------------
# AI Content Generator
# ----------------------------

@app.post("/generate-marketing-content")
def generate_content(data: MarketingPrompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a marketing strategist."},
                {"role": "user", "content": data.prompt}
            ]
        )
        return {"generated_content": response['choices'][0]['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# Sales Data Storage
# ----------------------------

@app.post("/add-sales-data")
def add_sales_data(data: SalesData):
    df = pd.DataFrame([data.dict()])
    df.to_sql("sales", engine, if_exists="append", index=False)
    return {"message": "Sales data added successfully"}

# ----------------------------
# Marketing Intelligence Analytics
# ----------------------------

@app.get("/sales-insights")
def sales_insights():
    try:
        df = pd.read_sql("SELECT * FROM sales", engine)
        
        total_sales = df["sales"].sum()
        total_spend = df["marketing_spend"].sum()
        roi = (total_sales - total_spend) / total_spend if total_spend > 0 else 0

        return {
            "total_sales": total_sales,
            "total_marketing_spend": total_spend,
            "ROI": roi
        }
    except:
        return {"message": "No sales data available"}