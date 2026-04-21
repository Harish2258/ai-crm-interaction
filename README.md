# AI CRM Backend

## 🚀 Features
- Log doctor interactions using AI (Groq)
- Extract:
  - Doctor name
  - Drug
  - Notes
  - Sentiment
- Store in SQLite database
- Search interactions

## 🛠 Tech Stack
- FastAPI
- Groq (LLM)
- LangGraph
- SQLAlchemy

## ▶️ Run Project

pip install -r requirements.txt  
uvicorn app.main:app --reload  

## 🔑 Setup

Create `.env` file:

GROQ_API_KEY=your_key_here

## 📡 API Endpoints

- POST /interaction/log  
- GET /interaction/all  
- GET /interaction/search  

## 🧪 Example

Input:  
Met Dr Sharma and discussed insulin treatment  

Output:  
Doctor: Dr Sharma  
Drug: Insulin  
Sentiment: Neutral  