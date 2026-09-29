from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "demo_mode" in data


def test_homepage():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text
    assert "/static/style.css" in response.text
    assert "/static/app.js" in response.text


def test_static_files():
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_qa_demo():
    response = client.post("/qa", json={"question": "What is photosynthesis?"})
    assert response.status_code == 200
    assert response.json()["answer"]


def test_explain_demo():
    response = client.post("/explain", json={"text": "Explain gravity"})
    assert response.status_code == 200
    assert response.json()["explanation"]


def test_quiz_demo():
    response = client.post("/quiz", json={"text": "Plants need sunlight."})
    assert response.status_code == 200
    questions = response.json()["questions"]
    assert len(questions) == 3
    assert all(len(q["options"]) == 4 for q in questions)
    assert all(q["correct_answer"] in q["options"] for q in questions)


def test_summary_demo():
    response = client.post("/summarize", json={"text": "Photosynthesis uses light energy."})
    assert response.status_code == 200
    assert response.json()["summary"]


def test_learning_path_demo():
    response = client.post(
        "/learn/recommendations",
        json={"topic": "Python", "level": "beginner"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Python"
    assert len(data["steps"]) == 3
