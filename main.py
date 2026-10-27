from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
        
    return data

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
