from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)

def test_health():
    assert client.get('/health').json()=={'status':'ok'}

def test_report():
    response=client.post('/reports',json={'description':'Déchets rue A'})
    assert response.status_code==201
    assert response.json()['status']=='nouveau'
    assert response.json()['id']

def test_empty():
    assert client.post('/reports',json={'description':''}).status_code==422
