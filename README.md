# 🗂️ Web Scraping & Data Structuring Projects – Yasham Software Services Pvt. Ltd.

## 📌 Overview
This repository contains **two major Python-based web scraping solutions** developed during my internship at **Yasham Software Services Pvt. Ltd.**:
1. **Earth911 Recycling Locator Scraper** – Extracts information about recycling centers from Earth911.com.
2. **BestBuy Store Locator Scraper** – Collects detailed store data including services and phone numbers from BestBuy.com.

Both scripts use **Selenium** for browser automation, **BeautifulSoup** for parsing HTML, and **Pandas** for structuring scraped data into CSV format.

---

## 🚀 Features
- ✅ Dynamic scraping of JavaScript-rendered content  
- ✅ Pagination handling for multiple pages  
- ✅ Cleans and structures data for analytics  
- ✅ Saves results in **CSV** format  
- ✅ Error handling and logging for better reliability  

---

## 🛠️ Technologies Used
- Python 3
- Selenium (Edge WebDriver)
- BeautifulSoup4
- Pandas
- Regular Expressions (re)

---

## 📂 Project Structure
```
├── earth911_final.py                # Earth911 scraping script
├── bestbuy.py                       # BestBuy scraping script
├── msedgedriver.exe                 # Microsoft Edge WebDriver
├── recycling_locations.csv          # Sample output for Earth911
├── bestbuy_stores_with_details.csv  # Sample output for BestBuy
└── README.md                        # Project documentation
```

---

# 🌎 **1. Earth911 Recycling Locator Scraper**

### ✅ Description
Automates the extraction of recycling center details from **Earth911.com**, including business names, addresses, accepted materials, and last update dates.

### ▶️ Usage Instructions
1. Install required dependencies:
   ```bash
   pip install selenium beautifulsoup4 pandas
   ```
2. Ensure `msedgedriver.exe` is in the same directory.
3. Run the script:
   ```bash
   python earth911_final.py
   ```
4. Output is saved as **`recycling_locations.csv`**.

### 🔧 Configuration
Modify parameters in `main()` to customize scraping:
```python
results = scraper.scrape(
    material_type='Electronics',
    location='10001',
    max_distance=100,
    max_pages=5
)
```

---

# 🏬 **2. BestBuy Store Locator Scraper**

### ✅ Description
Scrapes store details from **BestBuy.com**, including name, address, phone, services, store hours, and more.

### ⚠️ Important Note
After Microsoft Edge opens, **you may need to manually refresh the website once** if it does not load properly during scraping.  
This ensures the elements are loaded correctly for Selenium to proceed.

### ▶️ Usage Instructions
1. Install required dependencies:
   ```bash
   pip install selenium pandas
   ```
2. Keep `msedgedriver.exe` in the same folder as the script.
3. Run the scraper:
   ```bash
   python bestbuy.py
   ```
4. Scraped data will be saved as **`bestbuy_stores_with_details.csv`**.

---

## ✅ Example Output

### Earth911 Sample:
| Business Name   | Last Updated | Address                | Materials Category | Accepted Materials |
|-----------------|--------------|------------------------|--------------------|--------------------|
| XYZ Recycling   | 2025-07-26   | 123 Main St, New York  | Electronics        | TVs, Batteries     |

### BestBuy Sample:
| Store Name      | Phone        | Services                |
|-----------------|--------------|-------------------------|
| Best Buy NYC    | (212) 555-1234 | Geek Squad, Curbside Pickup |

---

## 🏢 Project Context
These projects were implemented during my internship at **Yasham Software Services Pvt. Ltd.** under the **Python Web Scraping & Data Structuring** module.  
They demonstrate:
- Automated extraction of structured data from dynamic websites
- Use of Selenium for web automation
- Handling pagination, delays, and data cleaning
- Exporting structured CSV outputs for analytics

---

## ✅ Author
**Aman Tiwari**  
Intern - Python Web Scraping & Data Structuring  
Yasham Software Services Pvt. Ltd.
