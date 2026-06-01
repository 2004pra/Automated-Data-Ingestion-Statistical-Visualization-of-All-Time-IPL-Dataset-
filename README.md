# Automated Data Ingestion and Statistical Visualization of the All-Time IPL Dataset

## 📌 Overview
This project is an end-to-end Data Engineering and Analytics pipeline built to process, analyze, and visualize the all-time Indian Premier League (IPL) dataset. It features a custom ETL (Extract, Transform, Load) pipeline that ingests raw CSV data, cleanses it, loads it into a relational SQLite database, and runs exploratory data analysis (EDA) to generate robust statistical insights and visualizations.

## 🏗️ Project Architecture
The project follows a structured pipeline:
1. **Extract (`etl/extract.py`)**: Ingests raw `matches.csv` and `deliveries.csv` datasets.
2. **Transform (`etl/transform.py`)**: Cleans data, handles missing values, maps categories, and prepares it for SQL insertion. Outputs intermediate cleaned CSVs.
3. **Load (`etl/load.py`)**: Loads the transformed data into a relational SQLite database (`ipl_database.db`) using SQLAlchemy.
4. **Analyze (`Analysis/insights.py`)**: Executes data queries via pandas and SQLAlchemy to answer 10 complex analytical questions (e.g., Toss Impact, Phase-wise Boundaries, Top Performers, Powerplay Momentum).
5. **Visualize (`charts/visualize.py`)**: Automatically generates publication-ready statistical charts covering all generated insights and saves them to the `charts/` directory.

## 🛠️ Tech Stack
* **Language:** Python
* **Data Processing & ETL:** Pandas, NumPy
* **Database:** SQLite, SQLAlchemy
* **Visualization:** Matplotlib, Seaborn

## 📂 Folder Structure
```text
Ipl_Analytics-pipeline/
│
├── Analysis/
│   └── insights.py         # Analytical queries and metrics calculation
├── charts/                 
│   ├── visualize.py        # Generates charts and graphs
│   └── *.png               # Output visualizations
├── Data/
│   ├── Raw/                # Original uncleaned datasets
│   └── Processed/          # Cleaned CSV files ready for DB ingestion
├── etl/
│   ├── extract.py          # Data extraction logic
│   ├── transform.py        # Data cleaning and transformation
│   └── load.py             # Database loading logic
└── README.md               # You are here!
```

## 🚀 How to Run (For Learners & Students)
If you are a student or a data enthusiast looking to understand how an ETL pipeline works, follow these steps to run the project on your local machine:

### 1. Prerequisites
Ensure you have Python 3.8+ installed. 
Clone the repository and navigate into it:
```bash
git clone https://github.com/2004pra/Automated-Data-Ingestion-Statistical-Visualization-of-All-Time-IPL-Dataset-.git
cd Ipl_Analytics-pipeline
```

### 2. Install Dependencies
Install the required Python libraries:
```bash
pip install pandas numpy sqlalchemy matplotlib seaborn
```

### 3. Run the Pipeline Step-by-Step
Follow the data flow from ingestion to visualization. Run these commands from the root directory:
```bash
# Step 1: Extract and Transform the raw data
python etl/transform.py  

# Step 2: Load the transformed data into SQLite Database
python etl/load.py       

# Step 3: Run the Analysis to print insights in the console
python Analysis/insights.py

# Step 4: Generate Visualizations (Check your /charts folder afterwards)
python -m charts.visualize
```

## 🤝 How to Contribute
We highly encourage contributions from the community! Whether you want to add new insights, optimize the ETL pipeline, or improve the visualizations, here is the standard workflow to contribute to this project:

1. **Fork the Repository:** Click the "Fork" button at the top right of the repository page.
2. **Clone your Fork:** 
   ```bash
   git clone https://github.com/YOUR_USERNAME/Automated-Data-Ingestion-Statistical-Visualization-of-All-Time-IPL-Dataset-.git
   ```
3. **Create a Feature Branch:** Always branch out from `main` before making changes.
   ```bash
   git checkout -b feature/AmazingNewInsight
   ```
4. **Make your Changes:** Add your SQL queries, Python scripts, or chart logic. Be sure to comment your code and follow the existing style.
5. **Commit your Changes:** 
   ```bash
   git commit -m "Add Amazing New Insight for Death Overs"
   ```
6. **Push to the Branch:** 
   ```bash
   git push origin feature/AmazingNewInsight
   ```
7. **Open a Pull Request:** Go to the original repository and click "Compare & pull request". Describe your changes clearly!

### Ideas for Contribution:
If you're looking for inspiration, here are a few things you could build:
* **Machine Learning:** Add predictive models (e.g., predicting match winner based on first innings score).
* **Database Upgrades:** Migrate the SQLite database to PostgreSQL or MySQL for better scalability.
* **Interactive Dashboards:** Create an interactive frontend using Streamlit or Dash instead of static Matplotlib images.
* **Testing:** Add comprehensive unit tests using `pytest` for the `transform.py` functions to ensure data integrity.

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
