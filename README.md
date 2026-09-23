# 🗄️ Talk2DB

Talk2DB is an intelligent, natural language-to-SQL engine and chat interface. Talk to any SQLite database as if you were talking to a human data analyst. 

Built with **FastAPI**, **React**, **Tailwind CSS**, and **Groq**, Talk2DB dynamically reads your database schema, links relevant tables, strictly validates generated SQL for read-only safety via AST parsing, and executes the queries—all in real time.

---

## ✨ Features

- **🗣️ Natural Language to SQL**: Ask complex questions (joins, aggregations, CTEs) in plain English.
- **🧠 Intelligent Schema Linking**: Dynamically routes queries to only the necessary tables, scaling gracefully to databases with 100+ tables without blowing up the LLM context window.
- **🛡️ AST-Based Safety Layer**: Uses `sqlglot` to parse the Abstract Syntax Tree of generated SQL, strictly rejecting any operations that mutate data (`INSERT`, `DROP`, etc.) or chain multiple statements.
- **🔄 Auto-Correction Loop**: If the LLM generates a SQL query that throws a database error, Talk2DB automatically intercepts the error and feeds it back to the LLM to self-correct (up to 3 retries).
- **📝 Conversational Summaries**: After fetching raw data, an additional fast LLM pass reads the data and returns a concise, conversational answer.
- **📱 Sleek React Interface**: A beautiful, minimal chat UI built natively into a single HTML file with React and Tailwind CSS.
- **🔌 Plug-and-Play Databases**: Drop any `.db` or `.sqlite` file into the `data/` folder, update your `.env`, and start querying immediately!

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.12, SQLite3
- **AI/LLM:** Groq API (Configurable models)
- **Security:** `sqlglot` (SQL AST Parsing)
- **Frontend:** React 18, Tailwind CSS, Lucide Icons (CDN-based, zero build step)

---

## 🚀 Quickstart: Local Setup

Follow these simple steps to run Talk2DB locally on your machine.

### 1. Clone the repository
```bash
git clone https://github.com/Thunder07-blip/talk2db.git
cd talk2db
```

### 2. Set up the virtual environment
Make sure you have Python 3.12+ installed.
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```bash
touch .env
```
Add your Groq API key and specify the database path:
```env
# .env
groq_api_1=your_groq_api_key_here
TALK2DB_DB_PATH=data/chinook.db
```
*(Note: A sample `chinook.db` and `company.db` are included in the `data/` folder for testing!)*

### 5. Run the Server
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 6. Chat with your Data!
Open your web browser and navigate to:
👉 **http://127.0.0.1:8000**

---

## 🧪 Running Benchmarks

Talk2DB includes a built-in benchmarking tool to test the AI's accuracy against any database.
```bash
python benchmark.py
```
This script will load a list of complex questions from a JSON file, run them through the Talk2DB engine, and output the success rate and average latency.

---

## 🏗️ Architecture Pipeline

1. **User Question** arrives via the `/ask` API endpoint.
2. **Schema Linker** analyzes the question and selects only the relevant tables.
3. **Context Builder** injects table schemas and sample data into the prompt.
4. **SQL Generator** writes the SQLite query.
5. **AST Validator** parses the query to ensure 100% read-only safety.
6. **Query Executor** runs the query against the database (auto-correcting if it fails).
7. **Summary Generator** reads the raw results and writes a conversational answer.
8. **React UI** displays the SQL, Data Table, and Summary.

---

## 🛡️ License
MIT License
