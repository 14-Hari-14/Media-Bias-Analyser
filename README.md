Media Bias Analyzer
The Media Bias Analyzer is a tool for detecting media bias in news articles, comprising a Firefox browser extension and a web application. The browser extension extracts text from a webpage and sends it to a FastAPI backend, which uses a large language model (LLM) API to generate a bias report, including a summary, political leaning, and detailed reasoning. The web application allows users to input article URLs directly for analysis. Both components display the bias report, with a "Read More" link to a detailed analysis page served locally.

Prerequisites
Before you begin, ensure you have the following installed:

Python 3.8+
Firefox Browser (for the extension)
Git (optional, for cloning the repository)
Sass (for compiling Website/styles/index.scss to index.css)
Install globally: npm install -g sass

Setup Instructions

1. Clone the Repository
   Clone this repository to your local machine using Git:
   git clone https://github.com/math-lover31415/Media-Bias.git
   cd Media-Bias

2. Set Up a Python Virtual Environment
   Create a virtual environment to isolate backend dependencies:
   python3 -m venv venv

or
python -m venv venv

Activate the virtual environment:

On macOS/Linux:source venv/bin/activate

On Windows:venv\Scripts\activate

3. Install Python Dependencies
   Install the required Python packages for the FastAPI backend:
   pip install -r Backend/requirements.txt

4. Compile Frontend Styles
   Compile the Sass stylesheet to CSS for the web application:
   sass Website/styles/index.scss Website/styles/index.css

5. Run the FastAPI Backend
   Start the FastAPI backend server:
   uvicorn Backend.main:app --reload

The backend will be available at http://localhost:8000. Verify by visiting http://localhost:8000/docs.

6. Serve the Web Application
   The web application (Website/) is static and requires a local HTTP server due to CORS restrictions. Run the following command in the project root:
   python -m http.server 8080

Access the web application at http://localhost:8080/Website/index.html.

7. Load the Extension in Firefox

Open Firefox and navigate to about:debugging#/runtime/this-firefox.
Click This Firefox in the left sidebar.
Under Temporary Extensions, click Load Temporary Add-on.
Select the manifest.json file from the Extension/ directory.

The extension will be loaded and ready to use.

8. Test the Project
   Web Application

Open http://localhost:8080/Website/index.html in your browser.
Navigate to the analysis page (analyze.html).
Enter a news article URL (e.g., Sample Article).
Submit the URL to view the bias report, including summary, political leaning, and reasoning.
Click Read More to access the detailed analysis page (details.html).

Browser Extension

Ensure the backend is running (http://localhost:8000).
Open a news article in Firefox (e.g., Sample Article).
Click the extension icon in the toolbar.
Click the Analyze Bias button in the popup.
The extension extracts the page content, sends it to the backend for LLM analysis, and displays the bias report (summary, political leaning, and detailed reasoning).
Click Read More to view the full analysis at http://localhost:8080/Website/details.html.
If errors occur (e.g., "Error: undefined"), open the console (Ctrl+Shift+J) and check logs from popup.js and content.js. Ensure content.js is updated and the backend is running.

Project Structure
Media-Bias/
│
├── Backend/ # FastAPI backend code
│ ├── classify.py # Legacy BERT classification (optional)
│ ├── llm_call.py # LLM API integration
│ ├── main.py # FastAPI application
│ ├── preprocess.py # Text preprocessing
│ ├── requirements.txt # Python dependencies
│ ├── test.py # Backend tests
│ ├── train.ipynb # Legacy BERT training notebook
│ └── venv/ # Virtual environment (ignored)
│
├── Website/ # Web application frontend
│ ├── about.html # About page
│ ├── analyze.html # Analysis input page
│ ├── analyze.js # Analysis page logic
│ ├── assets/ # Static assets (e.g., background.png)
│ ├── details.html # Detailed analysis page
│ ├── details.js # Detailed page logic
│ ├── index.html # Homepage
│ └── styles/ # CSS and Sass styles
│ ├── index.css # Compiled CSS
│ ├── index.css.map # Source map
│ └── index.scss # Source Sass
│
├── Extension/ # Firefox browser extension
│ ├── content.js # Content script for page extraction and API calls
│ ├── icons/ # Extension icons
│ ├── manifest.json # Extension metadata
│ ├── popup.html # Popup UI
│ ├── popup.js # Popup logic
│ └── styles.css # Popup styles
│
├── docs/ # Documentation
│ ├── Abstract.docx # Project abstract
│ ├── Literature Review (docs) .pdf
│ ├── Literature Review (ppt).pdf
│ ├── Papers/ # Research papers
│ ├── SDD.pdf # Software Design Document
│ └── SRS.pdf # Software Requirements Specification
│
├── .gitignore # Git ignore rules
├── LICENSE # MIT License
└── README.md # Project documentation

Troubleshooting

Extension Error: "Error: undefined"
Cause: Likely due to an outdated content.js not making the API call.
Fix: Ensure Extension/content.js matches the version that calls http://localhost:8000/analyze. Check console logs (Ctrl+Shift+J) for Response from content.js: { content: ... } (indicates old content.js) vs. { status, data }.

Backend Not Responding
Symptoms: "Failed to analyze content" or network errors in console.
Fix: Verify the backend is running (http://localhost:8000/docs). Test the API with curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"text":"test content","url":false}'.

CORS Issues
Symptoms: "Cross-Origin Request Blocked" in console.
Fix: Ensure manifest.json includes "host_permissions": ["http://localhost:8000/*"].

Storage Errors
Symptoms: "Failed to store result" in popup.
Fix: Confirm manifest.json includes "storage" permission.

No Results Displayed
Fix: Check the API response format in content.js logs (API response: ...). Ensure it matches { analysis: "Summary: ...\n\n**Political Leaning:** ...\n\n**Reasoning:** ..." }.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Notes

The backend uses an LLM API for bias analysis, replacing the previous BERT-based model. Configure API keys in Backend/llm_call.py (e.g., via .env, ignored by .gitignore).
The web application requires a local HTTP server to avoid CORS issues with analyze.js.
The browser extension depends on the backend (http://localhost:8000) for analysis. Ensure the backend is running before using the extension.
For production, deploy the backend to a cloud service (e.g., Heroku) and host the web application on a static file server (e.g., Netlify). Update content.js, analyze.js, and manifest.json to use the deployed API URL.
The extension and web application exhibit basic Agentic AI behavior, autonomously extracting or accepting content and delegating analysis to the LLM API.
