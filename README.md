# ⚽ UEFA Champions League: End-to-End Data Pipeline & Analytics

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Power_BI](https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![SQL](https://img.shields.io/badge/SQL-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

## 📌 Project Overview
This project is a full-stack data engineering and business intelligence solution designed to track, store, and visualize live data from the UEFA Champions League. The pipeline automates data ingestion from a REST API, structures it within a relational PostgreSQL database using a Star Schema, and serves it to a dynamic, broadcast-quality Power BI dashboard.

It demonstrates a complete data lifecycle: from raw JSON extraction to advanced SQL feature engineering, culminating in a premium UI/UX analytics experience.

---

## 🏗️ Architecture & Workflow

### 1. Data Ingestion (The Extraction Layer)
* **Tech:** Python, `requests`, `psycopg2`, `python-dotenv`
* **Process:** A Python script securely authenticates with the `Football-Data.org` API to retrieve live league standings, historical match results, and high-resolution official team crest URLs.

### 2. Data Storage & Modeling (The Database Layer)
* **Tech:** PostgreSQL
* **Process:** Designed a relational database utilizing a **Star Schema** approach for analytical efficiency:
  * **`ucl_standings` (Dimension):** Stores team metadata, current points, goal statistics, and image URLs.
  * **`ucl_matches` (Fact):** Stores individual match records, including home/away teams, scores, and match status.
  * **Feature Engineering:** Utilized complex SQL queries, including `UNION ALL`, `CASE` statements, and `LAG()` window functions, to calculate a dynamic, rolling 3-match form guide (W-D-L) for every team.

### 3. Business Intelligence & UI (The Analytics Layer)
* **Tech:** Power BI, DAX
* **Process:** * Engineered custom **DAX measures** for dynamic KPIs (e.g., Win Rate, Net Goal Difference).
  * Designed a "Dark Mode" broadcast-style UI inspired by official UEFA graphics, utilizing transparent visual overlays and custom starball backgrounds.
  * Implemented an interactive dashboard where selecting a team dynamically filters the Performance Matrix (Scatter Plot), Goal Difference charts, and instantly updates a high-resolution team crest component.

---

## 📊 The Dashboard

![UCL Dashboard Preview](dashboard_preview.gif) 
<img width="1432" height="817" alt="image" src="https://github.com/user-attachments/assets/b921d069-9cd0-44e1-b6d6-52d323a332ee" />


---

## 🚀 Key Competencies Demonstrated
* **API Integration:** Securely fetching and parsing nested JSON payloads.
* **Relational Database Design:** Creating primary/foreign key relationships (`team_id`) to bridge summary standings with historical match logs.
* **Advanced SQL:** Utilizing Window Functions for chronological data analysis.
* **Data Visualization & UI/UX:** Transforming raw data URLs into rendered images within Power BI and overriding default visual constraints for a premium, application-like user experience.

---

## 🛠️ Setup & Execution
1. Clone the repository: `git clone [Insert your repo link here]`
2. Install dependencies: `pip install requests psycopg2 python-dotenv`
3. Create a `.env` file with your database credentials and `FOOTBALL_API_TOKEN`.
4. Run the ETL pipeline: `python main.py`
5. Open `UCL_Analytics_Dashboard.pbix` in Power BI Desktop to view the live dashboard.

---

## 🔮 Roadmap & Future Scope
* **Live Match Updates:** Automating the Python script via Windows Task Scheduler/Cron to fetch live match updates during game days.
* **Predictive Modeling:** Integrating a Python-based Win-Probability model based on historical team form.
* **🚧 *Stay Tuned: Major updates for the Knockout Rounds and later stages are coming soon!***
