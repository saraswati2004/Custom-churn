from fastapi import FastAPI,HTTPException
import os
import joblib

app = FastAPI(
    title = ' Customer churn API',
    description = 'an API to predict customer churn'
              )
@app.get("/")
def greet():
    return {'massage':'whats up'}

MODEL_PATH = 'best_balanced_churn_model.pkl'
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"file not found")
model = joblib.load(MODEL_PATH)

from pydantic import BaseModel,Field,field_validator

class CustomerData(BaseModel):
    Gender: str = Field(...,example= 'female')
    Age: int = Field(...,ge= 18,le = 100,example=45)
    Tenure : int = Field(...,ge=0,le=100,example=13)
    Services_Subscribed : int = Field(...,ge= 0,le=10,example=3)
    Contract_Type: str = Field(...,example = 'Months-to-month')
    MonthlyCharges: float = Field(...,gt = 0,example=70.5)
    TotalCharges: float = Field(...,ge = 0,example = 500.75)
    TechSupport : str = Field(...,example = 'yes')
    OnlineSecurity :str = Field(...,example = 'yes')
    InternetService: str = Field(..., example='fibar optic')
    @field_validator('Gender')
    @classmethod
    def validate_gender(cls,value):
        allowed = { 'Male','Female'}
        if value not in allowed:
            raise ValueError(f"gender must be {allowed}")

    @field_validator('Contract_Type')
    @classmethod  
    def validation_contray(cls,value):
        allowed = {'Month-to-month','One year','Two year'}
        if value not in allowed:
            raise ValueError(f"incorrect value must be {allowed}")

    @field_validator('TechSupport','OnlineSecurity')
    @classmethod
    def validate_yes_no(cls,value):
        allowed = {'yes','no'}
        if value not in allowed:
            raise ValueError(f"incoorect value must be {allowed}")

    @field_validator('TechSupport','OnlineSecurity')
    @classmethod
    def vaidate_internet(cls,value):
        allowed = {'DSL','Fibar optic','No'}

# output scheme
from typing import Optional
class predictionResponse(BaseModel):
    Churn_prediction : int
    Churn_label: str
    Churn_probability : Optional[float] = None
import pandas as pd
# prediction endpoint
@app.post('/Predict',response_model=predictionResponse)
def predict(customer: CustomerData):
    try:
        input_df = pd.DataFrame([customer.model_dump()])


        prediction = model.predict(input_df)[0]

    # probability
        probability = None
        if hasattr(model,'predct_prob'):
            probability = model.predict_proba(input_df)[0][1]
        return predictionResponse(
            Churn_prediction=prediction,
            Churn_label="Churn" if prediction == 1 else "Not Churn",
            Churn_probability=probability
)
    except Exception as e:
        raise HTTPException(status_code =500,detail = str(e))
