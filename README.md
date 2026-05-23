# Bicycle Accidents in Great Britain (1979–2018)
---

## Live Dashboard

**[bike-accidents-gb.streamlit.app](https://bike-accidents-gb.streamlit.app/)**

An interactive, multi-tab dashboard built with Streamlit and Plotly. Filter by year range, injury severity, gender, and road conditions — all charts update instantly across every tab.

---

## Project Overview

This project presents a comprehensive **Exploratory Data Analysis (EDA)** of bicycle accident records from Great Britain spanning 40 years (1979–2018). The goal is to uncover temporal patterns, demographic risk factors, and environmental conditions associated with cyclist accidents, and to translate those findings into actionable safety recommendations.

### Dataset

| File | Description | Rows |
|------|-------------|------|
| `Accidents.csv` | Accident context: date, time, road & weather conditions, speed limit, road type, light conditions | 827,861 |
| `Bikers.csv` | Cyclist demographics: gender, age group, injury severity | 827,871 |

Both files are merged on `Accident_Index` to produce a single analysis-ready dataset of **827,861 records**.

Source: [Bicycle Accidents in Great Britain — Kaggle](https://www.kaggle.com/)

---

## Notebook Analysis (`Bike_Accidents_GB.ipynb`)

The Jupyter notebook walks through the full analysis pipeline across seven sections:

### 1. Data Loading & Exploration
Initial inspection of both datasets — shape, column types, and a missing-value audit. Notably, the dataset is nearly complete with zero missing values across all key fields.

### 2. Data Preprocessing
- Date parsing and extraction of `Year`, `Month`, and `Hour` features
- Speed limit cast to integer
- Correction of a source-data typo (`One way sreet` → `One way street`)
- Definition of ordered categorical variables used throughout (day order, age groups, severity levels)

### 3. Descriptive Statistics
Summary statistics for numerical columns (vehicles, casualties, speed limit) alongside key counts:
- **82.3%** of accidents result in slight injuries
- **16.9%** serious injuries
- **0.81%** fatal

### 4. Exploratory Data Analysis

**4.1 Temporal Trends**
Accident frequency peaked around **1983** (~25,000/year) and declined substantially through the 2010s. Clear commuter patterns emerge — accident spikes at **8–9 AM** and **5–6 PM** on weekdays, with summer months (June–August) recording the highest annual counts.

**4.2 Severity Analysis**
Both serious and fatal accident rates have declined proportionally over the study period. A donut chart and time-series breakdown show the long-run improvement in outcomes, likely driven by road safety legislation, cycling infrastructure investment, and advances in vehicle safety.

**4.3 Demographic Analysis**
Males account for approximately **80%** of all cyclist accident records. The **26–45 age group** is most frequently involved, consistent with the core commuter population. Older cyclists (56+) show elevated serious/fatal rates per accident, likely due to reduced physical resilience.

**4.4 Environmental Factors**
Dry roads dominate raw accident counts simply because most cycling happens in dry conditions. Road surface, weather, and light conditions are all examined. Accidents in **darkness without lighting** are significantly more likely to be severe than daylight accidents.

**4.5 Road Characteristics**
Single carriageways account for the largest share of accidents by road type. High-speed roads (60–70 mph) have substantially elevated fatality rates — reflected clearly in the speed limit analysis.

### 5. Risk Factor Analysis (Prescriptive Statistics)
Rather than raw counts, this section computes **serious-or-fatal rates** to remove volume bias. Key findings:

| Condition | Serious + Fatal Rate |
|-----------|----------------------|
| Flooded roads | 25.4% |
| Darkness, no lighting | 26.2% |
| 70 mph speed limit | Highest fatality rate |
| Frost / ice | 19.8% |

### 6. Interactive Dashboard
A nine-panel static overview chart is embedded in the notebook, covering all key dimensions at a glance — serving as the basis for the full Streamlit dashboard.

### 7. Key Insights & Recommendations

| Priority | Recommendation |
|----------|----------------|
| High | Enforce reduced speed limits on rural roads and near cycle routes |
| High | Expand street lighting on routes with high nighttime cycling volumes |
| Medium | Launch winter cycling safety campaigns before November |
| Medium | Target male commuter cyclists (ages 26–45) during peak hours |
| Low | Improve intersection design on single carriageways |

---

## Interactive Dashboard

The Streamlit dashboard extends the notebook analysis with live filtering and six tabs:

| Tab | Contents |
|-----|----------|
| Overview | KPI metrics + 9-panel summary across all dimensions |
| Temporal Trends | Annual trend, monthly/daily patterns, hour × day heatmap |
| Severity | Distribution donut, time-series trends, hourly severity breakdown |
| Demographics | Gender and age counts, severity by demographic group |
| Environment & Roads | Road/weather/light conditions, road type, speed limit charts |
| Risk Analysis | Serious/fatal rate charts, detailed risk tables, recommendations |

**Run locally:**
```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

---

## Repository Structure

```
.
├── Accidents.csv            # Accident-level data (827,861 rows)
├── Bikers.csv               # Cyclist-level data (827,871 rows)
├── Bike_Accidents_GB.ipynb  # Full EDA notebook
├── dashboard.py             # Streamlit dashboard
└── requirements.txt         # Python dependencies
```

## Dependencies

- Python 3.14
- `streamlit==1.57.0`
- `pandas==2.3.3`
- `numpy==2.4.1`
- `plotly==6.7.0`
