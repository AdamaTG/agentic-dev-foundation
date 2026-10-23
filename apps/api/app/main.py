from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4

app = FastAPI(title='ADF Reference API')

class ReportIn(BaseModel):
    description: str = Field(min_length=3)

@app.get('/health')
def health() -> dict[str, str]:
    return {'status':'ok'}

@app.post('/reports', status_code=201)
def create_report(report: ReportIn) -> dict[str, str]:
    if not report.description.strip():
        raise HTTPException(status_code=422, detail='description required')
    return {'id':str(uuid4()), 'status':'nouveau'}
