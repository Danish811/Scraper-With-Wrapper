
---

## 🚀 Setup Instructions for `danish811-scraper-with-wrapper`

Follow these steps to set up and run the scraper project on your machine.

---

### 1️⃣ **Clone the repository**

```bash
git clone https://github.com/danish811/scraper-with-wrapper.git
cd scraper-with-wrapper
```


---

### 2️⃣ **Install Python 3.11 (if not installed)**

Download and install Python 3.11:
👉 [https://www.python.org/downloads/release/python-3110/](https://www.python.org/downloads/release/python-3110/)

✅ Make sure to check **Add Python to PATH** during installation.

Verify:

```bash
python --version
```

---

### 3️⃣ **Install `uv` package manager**

```bash
pip install uv
```

Verify:

```bash
uv --version
```

---

### 4️⃣ **Create a virtual environment**

```bash
uv venv venv
```

Activate it:

```bash
# On Windows
venv\Scripts\activate

```

---

 Install walmart-python-scrapy-scraper as editable module
Assuming the folder is inside the main project directory:

```bash
uv pip install -e walmart-python-scrapy-scraper

```
✅ This allows you to edit code inside walmart-python-scrapy-scraper and have changes take effect immediately without reinstalling.


---

### 6️⃣ **Install project dependencies using `uv`**

```bash
uv pip install -r requirements.txt
```

---

### 7️⃣ **Install Playwright browsers**

```bash
playwright install
```

---

### 8️⃣ **Run the scrapers**


```bash
python utils/scraper.py
```

---

