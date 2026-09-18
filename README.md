# GEN DATA AI — AI-Powered Synthetic Dataset Generator

GEN DATA AI is a state-of-the-art synthetic data generation platform that allows you to create high-quality, realistic datasets using natural language prompts. Whether you need 50 students for testing, 1,000 employee records for a demo, or complex healthcare data, GEN DATA AI understands your intent and generates the data instantly.

\---

## 🌟 Key Features

* **🗣️ Natural Language Prompts**: Describe your dataset in plain English (e.g., *"Generate 100 employees with name, salary between 40k-120k, and department"*).
* **⚡ Instant Generation**: High-performance engine that generates thousands of rows in seconds.
* **🎯 Smart Constraints**: Automatically applies ranges, distributions, and value bounds based on your description.
* **🌐 Multi-Domain Support**: Specialized support for Students, Employees, Healthcare, Sales, and more.
* **📊 Export Options**: Download your datasets in **CSV** or **JSON** format.
* **🔒 Privacy-First**: 100% synthetic data—no real personal information is used, making it safe for compliance and testing.

\---

## 🛠️ Tech Stack

* **Frontend**: Next.js 15 (App Router), React 19, Vanilla CSS (Premium Aesthetics)
* **Backend**: FastAPI (Python) — *Handles NLP parsing and data generation*
* **Database**: MongoDB — *Stores user chats and generated schemas*
* **Auth**: JWT-based authentication with secure cookies
* **Styling**: Modern, responsive design with glassmorphism and smooth animations

\---

## 🚀 Getting Started

Follow these steps to get the project running on your local machine.

### 1\. Prerequisites

Ensure you have the following installed:

* [Node.js](https://nodejs.org/) (v18 or higher)
* [Python](https://www.python.org/) (v3.10 or higher)
* [MongoDB](https://www.mongodb.com/try/download/community) (Running locally or a MongoDB Atlas URI)

### 2\. Clone the Repository

```bash
git clone https://github.com/Dhanish-AI/GEN\_DATA\_AI.git
cd GEN\_DATA\_AI
```

### 3\. Setup Backend

1. Navigate to the backend directory:

```bash
   cd backend
   ```

2. Create a virtual environment:

```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   * **Windows**: `venv\\Scripts\\activate`
   * **Mac/Linux**: `source venv/bin/activate`
4. Install dependencies:

```bash
   pip install -r requirements.txt
   ```

5. Download the Spacy language model:

```bash
   python -m spacy download en\_core\_web\_sm
   ```

6. Run the FastAPI server:

```bash
   uvicorn main:app --reload
   ```

   *The backend will be running at http://localhost:8000*

### 4\. Setup Frontend

1. Navigate to the frontend directory:

```bash
   cd ../frontend
   ```

2. Install dependencies:

```bash
   npm install
   ```

3. Create a `.env.local` file in the `frontend` folder and add:

```env
   MONGODB\_URI=mongodb://localhost:27017/gendataai
   JWT\_SECRET=your\_super\_secret\_key\_here
   BACKEND\_URL=http://localhost:8000
   ```

4. Run the development server:

```bash
   npm run dev
   ```

   *The app will be running at http://localhost:3000*

\---

## 💡 How to Use

1. **Sign Up / Login**: Create an account to save your generated datasets.
2. **Type a Prompt**: In the chat interface, describe the data you need.

   * *Example: "Generate 50 students with name, age (18-25), GPA, and department"*
3. **Preview**: View the generated data in the interactive table.
4. **Download**: Click the download button to get your CSV or JSON file.

\---

## 📂 Project Structure

```text
GEN\_DATA\_AI/
├── frontend/           # Next.js Application
│   ├── app/            # App Router (Pages \& API)
│   ├── components/     # UI Components
│   ├── lib/            # Utilities (Auth, MongoDB)
│   └── public/         # Static Assets
├── backend/            # FastAPI Application
│   ├── main.py         # Entry point
│   └── venv/           # Python Virtual Environment
└── README.md           # Project Documentation
```

\---

## 📜 License

This project is licensed under the MIT License.

