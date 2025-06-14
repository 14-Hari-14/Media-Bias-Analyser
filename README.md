# Media Bias Analyzer

This project is a browser extension that analyzes media bias on web pages. It extracts the content of the current webpage, sends it to a FastAPI backend for analysis using a BERT-based machine learning model, and displays the bias report in the extension popup. A "Read More" button redirects to a detailed analysis page.

---

## **Prerequisites**

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Firefox Browser**
- **Git** (optional, for cloning the repository)

---

## **Setup Instructions**

### **1. Clone the Repository**

Clone this repository to your local machine using Git:

```bash
git clone https://github.com/math-lover31415/Media-Bias.git
cd Media-Bias
```

---

### **2. Set Up a Python Virtual Environment**

Create a virtual environment to isolate the project dependencies:

```bash
python3 -m venv venv
```

or

```bash
python -m venv venv
```

Activate the virtual environment:

- **On macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```
- **On Windows**:
  ```bash
  venv\Scripts\activate
  ```

---

### **3. Install Python Dependencies**

Install the required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

### **4. Run the FastAPI Backend**

Start the FastAPI backend server:

```bash
uvicorn main:app --reload
```

The backend will be available at `http://127.0.0.1:8000`.

---

### **5. Load the Extension in Firefox**

1. Open Firefox and go to `about:debugging`.
2. In the left sidebar, click on **This Firefox**.
3. Under **Temporary Extensions**, click **Load Temporary Add-on**.
4. Select the `manifest.json` file from the `media-bias-analyzer` directory.

The extension will now be loaded and ready to use.

---

### **6. Test the Extension**

1. Open a news article in Firefox (e.g., [Sample Article](https://www.bbc.com/news/articles/cy8pejl63qqo)).
2. Click the extension icon in the toolbar.
3. Click the **Analyze Bias** button in the popup.
4. The extension will extract the content, send it to the backend, and display the bias report.
5. Click the **Read More** button to view the full content on a separate page.

---

## **Project Structure**

```
media-bias-analyzer/
│
├── Backend/                  # FastAPI backend code
│   ├── main.py               # FastAPI application
│   ├── preprocess.py
│   ├── train.ipynb
│   ├── classify.py
│   └── requirements.txt      # Python dependencies
│
├── Extension/                # Firefox extension code
│   ├── manifest.json         # Extension metadata
│   ├── content.js            # Content script to extract page content
│   ├── popup.html            # Popup UI
│   ├── popup.js              # Popup logic
│   ├── styles.css            # Styles for the popup
│   └── icons/                # Extension icons
│
├── Website/
│   ├── index.html
│   ├── about.html
│   ├── analyze.html
│   ├── details.html
│   ├── details.js
│   ├── analyze.js
│   └── styles/
│       ├── index.css
│       ├── index.css.map
│       └── index.scss
│
├── docs/
│
├── .gitignore
│
├── LICENSE
│
└── README.md                 # This file
```

---

## **License**

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
