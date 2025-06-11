# AutoGen React Builder

An intelligent React application generator powered by AutoGen agents that creates modern, production-ready React applications with Vite and optional features.

## Features

- 🤖 AI-powered code generation using AutoGen agents
- ⚛️ Modern React + Vite setup
- 🎨 Tailwind CSS for styling
- 📦 Optional integrations:
  - Zustand for state management
  - React Router for routing
  - Modern UI Components
  - Framer Motion animations

## Project Structure

```
autogen-react-builder/
├── backend/              # FastAPI + AutoGen backend
│   ├── agents/          # Specialized AutoGen agents
│   ├── services/        # Core services
│   ├── templates/       # Project templates
│   └── api/            # FastAPI routes
├── frontend/           # Streamlit UI
└── generated/         # Generated project outputs
```

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables

## Usage

1. Start the backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Start the frontend:
   ```bash
   cd frontend
   streamlit run streamlit_app.py
   ```

3. Visit http://localhost:8501 to access the UI

## Generated Project Features

- Modern React 18+ setup with Vite
- Tailwind CSS for styling
- Optional features:
  - State management with Zustand
  - Routing with React Router
  - Custom UI Components
  - Animations with Framer Motion