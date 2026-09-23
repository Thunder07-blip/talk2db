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

## 🗃️ Using Talk2DB with Your Own Database

Talk2DB is fully plug-and-play — it reads your database schema automatically at startup and needs zero code changes. Follow these steps to connect it to any database you own.

### Step 1 — Prepare Your Database File

Talk2DB works with **SQLite** databases (`.db` or `.sqlite` files). If your data is in a different format, first convert it:

<details>
<summary>📄 Converting from CSV files</summary>

```bash
# Install the sqlite-utils tool
pip install sqlite-utils

# Load your CSV into a new SQLite database
# This will create a table named 'sales' from sales_data.csv
sqlite-utils insert my_database.db sales sales_data.csv --csv
```

You can run this for each CSV file you have — each file becomes a separate table.
</details>

<details>
<summary>🐘 Converting from PostgreSQL / MySQL</summary>

Use [pgloader](https://pgloader.io/) for PostgreSQL, or [mysql2sqlite](https://github.com/dumblob/mysql2sqlite) for MySQL to export a `.db` file first.

```bash
# Example: export from PostgreSQL using pgloader
pgloader postgresql://user:pass@localhost/mydb sqlite:///my_database.db
```
</details>

<details>
<summary>📊 Converting from Excel / Google Sheets</summary>

Export your spreadsheet as a `.csv` file (File → Download → CSV), then follow the CSV steps above.
</details>

---

### Step 2 — Place Your Database in the Project

Copy your `.db` file into the `data/` folder of the Talk2DB project:

```
talk2db/
└── data/
    ├── chinook.db      ← (included sample)
    ├── company.db      ← (included sample)
    └── your_database.db  ← YOUR FILE GOES HERE
```

---

### Step 3 — Update Your `.env` File

Open the `.env` file in the project root and change the `TALK2DB_DB_PATH` to point to your database:

```env
# .env
groq_api_1=your_groq_api_key_here
TALK2DB_DB_PATH=data/your_database.db
```

> **Tip:** You can also use an absolute path if your database is stored elsewhere:
> ```env
> TALK2DB_DB_PATH=/home/yourname/projects/mydata.db
> ```

---

### Step 4 — Restart the Server

Stop the currently running server (press `CTRL+C`) and start it again:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Talk2DB will automatically:
- Detect your new database on startup
- Read all its tables, columns, data types, primary keys, and foreign keys
- Update the sidebar schema explorer in the UI with your new tables
- Route all AI queries using your new schema

---

### Step 5 — Open the UI and Start Asking Questions

Navigate to **http://127.0.0.1:8000** in your browser.

The left sidebar will now show **your** database's tables and columns. Start typing questions in plain English!

**Examples of the kinds of questions you can ask:**
- *"How many records are in the orders table?"*
- *"What is the average sale price grouped by category?"*
- *"Show me the top 10 customers by total revenue."*
- *"Find all products that have never been ordered."*
- *"Which region had the highest growth between January and March?"*

---

### (Optional) Step 6 — Create a Benchmark File

To test Talk2DB's accuracy against your database, create a `.json` file with a list of questions you know the answers to:

```json
[
  { "question": "How many total customers are there?" },
  { "question": "What is the most popular product category?" },
  { "question": "List the top 5 salespeople by total revenue." },
  { "question": "Which customers have placed more than 10 orders?" }
]
```

Save it as `my_benchmark.json` in the project root, then run:

```bash
python benchmark.py
```

> **Note:** You'll need to update the last few lines of `benchmark.py` to point to your new database and benchmark file if you want to run them directly. Or just call `run_benchmark()` from a Python script:
> ```python
> from pathlib import Path
> from benchmark import run_benchmark
> run_benchmark(Path("data/your_database.db"), Path("my_benchmark.json"))
> ```

---

### ⚠️ Important Notes

| Requirement | Detail |
|---|---|
| **Database type** | Must be a SQLite `.db` or `.sqlite` file |
| **Read-only safety** | Talk2DB **cannot** modify your data. The database is opened in read-only mode at the driver level, plus an AST security layer validates every query before execution. |
| **Table naming** | SQLite table names are case-sensitive in some contexts. Talk2DB reads the exact names from the database, so the AI will use them correctly. |
| **Large databases** | Talk2DB's Schema Linking feature handles databases with 100+ tables by routing each question to only the relevant subset of tables. |
| **No data is sent to third parties** | Only the **schema structure** (table and column names) and the **user's question** are sent to the Groq AI API. The actual row data in your database stays on your machine. |

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

