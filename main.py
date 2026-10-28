from fastapi import FastAPI, Path, HTTPException, Query
import json
from fastapi.responses import JSONResponse 

app = FastAPI()

from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

class Patient(BaseModel):

    id: Annotated[str, Field(..., description="The unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient", example="John Doe")]
    city: Annotated[str, Field(..., description="The city where the patient resides", example="New York")]
    age: Annotated[int, Field(..., gt=0,lt=120,description="The age of the patient", example=30)]
    gender: Annotated[Literal['Male','Female','Others'], Field(..., description="The gender of the patient")]
    weight: Annotated[float, Field(..., gt=0, description="The weight of the patient in kg", example=70.5)]
    height: Annotated[float, Field(..., gt=0, description="The height of the patient in cm", example=175.0)]

    @computed_field(description="The Body Mass Index (BMI) of the patient")
    @property
    def bmi(self)->float:
        bmi=round(self.weight / ((self.height / 100) ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal weight"
        elif 25 <= self.bmi < 29.9:
            return "Overweight" 
        else:
            return "Obesity"

class PatientUpdate(BaseModel):
        name: Annotated[Optional[str], Field(default=None)]
        city: Annotated[Optional[str], Field(default=None)]
        age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
        gender: Annotated[Optional[Literal['Male','Female','Others']], Field(default=None)]
        weight: Annotated[Optional[float], Field(default=None, gt=0)]
        height: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
        
    return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=4)

@app.get("/") 
def hello():
    return {'message': 'Patient Management API'}

@app.get('/about')
def about():
    return {'message': 'A fully functional API to manage your patient'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    #load all patients
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by: str = Query(..., description="Sorton the basis of weight, height, or age", example="weight"), order: str = Query("asc", description="Sort in asc or desc order", example="asc")):
    data = load_data()
    
    if sort_by not in ['weight', 'height', 'age', 'bmi']:
        raise HTTPException(status_code=400, detail="Invalid sort parameter. Must be 'weight', 'height', 'age', or 'bmi'.")
    valid_fields = ['weight', 'height', 'age', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of {valid_fields}.")

    if order not in ['asc', 'desc']:    
        raise HTTPException(status_code=400, detail="Invalid order parameter. Must be 'asc' or 'desc'.")

    data=load_data()
    sort_order= True if order == "desc" else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by,0), reverse=sort_order)
    return sorted_data


#Cliet sent data and pydantic validate it then it will be stored in the json file
@app.post('/create')
def create_patient(patient: Patient):
    #load Existing data
    data = load_data()

    #Check if patient with the same ID already exists in the database
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient with this ID already exists.")
    
    #new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    #save the updated data back to the JSON file
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully."})

@app.put('/edit/{patient_id}')

def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")

    # Update the existing patient data with the new values
    existing_patient = data[patient_id]
    updated_patient = existing_patient.copy()
    
    for key, value in patient_update.model_dump(exclude_unset=True).items():
        updated_patient[key] = value

    #Updated patient -> pydantic object -> updated bmi + verdict 

    patient_pydantic_object = Patient(id=patient_id, **updated_patient)

    #pydantic object -> dict
    updated_patient = patient_pydantic_object.model_dump(exclude={'id'})
    

    data[patient_id] = updated_patient

    #save data
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient updated successfully."})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found.")

    # Remove the patient from the data
    del data[patient_id] 

    # Save the updated data back to the JSON file
    save_data(data)
    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully."})