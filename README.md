# Sleep Clinic Location Analyzer

Interactive AI-powered Streamlit dashboard for identifying optimal U.S. counties for sleep clinic placement based on CDC health data and machine learning analysis.

## Project Description

This application analyzes CDC PLACES health data to identify optimal locations for sleep clinic expansion. It correlates sleep deprivation rates with lifestyle risk factors (obesity, physical inactivity, diabetes, mental distress) across 677 U.S. counties to recommend high-priority placement opportunities.

### Key Features

**Interactive Filtering:**
- State selection (14 states available)
- Priority tier filtering (Tier 1, 2, 3)
- Sleep deprivation range slider

**Analysis Views:**
- Top Counties: Ranked bar chart with color-coded opportunity tiers
- Geographic Analysis: State-level distribution and patterns
- Correlation Analysis: Statistical relationships with trendlines (r=0.784 for obesity)

**Phase 2 Expansion:**
- County Comparison Tool: Side-by-side evaluation of candidate locations
- Automatic recommendations based on opportunity scores

**AI-Powered Features:**
- Natural Language Query: Ask questions in plain English
- Auto-Generated Insights: AI analyzes data and provides business recommendations

**Data:**
- 677 counties analyzed
- 14 states covered
- 3.3M adult population
- 11 health metrics per county

## App Deployment URL

🚀 **Live App:** [https://team18-sleep-clinic.streamlit.app](https://team18-sleep-clinic.streamlit.app)

## Local Setup Instructions

### Prerequisites
- Python 3.10 or higher
- uv package manager (recommended) or pip

### Installation with uv

```bash
git clone https://github.com/adubbak1/sleep-clinic-analyzer.git
cd sleep-clinic-analyzer
uv sync
uv run streamlit run app.py
```

### Installation with pip

```bash
git clone https://github.com/adubbak1/sleep-clinic-analyzer.git
cd sleep-clinic-analyzer
pip install -r requirements.txt
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## Project Structure

```
sleep-clinic-analyzer/
├── app.py                    # Main Streamlit application
├── data/
│   └── counties_ranked.csv   # Analyzed county health data
├── .streamlit/
│   └── secrets.toml          # API keys (not committed to git)
├── pyproject.toml            # uv project configuration
├── requirements.txt          # pip dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Usage Guide

### Basic Navigation

1. **Filters (Sidebar):** Select state, priority tier, and sleep deprivation range
2. **Top Counties Tab:** View ranked counties with color-coded opportunity tiers
3. **Geographic Analysis Tab:** Explore state-level distributions
4. **Correlation Analysis Tab:** Examine statistical relationships between health metrics

### Phase 2 Features

**County Comparison Tool:**
- Select two counties from dropdowns
- View side-by-side metrics comparison
- See automatic recommendation

### AI Features

**Natural Language Query:**
- Type questions like "Show me Alabama counties with high obesity"
- AI parses your question and filters data automatically

**AI-Generated Insights:**
- Click "Generate AI Insights About This Data"
- AI analyzes current data and provides business recommendations
- Mentions specific counties and states with actionable suggestions

## Technology Stack

- **Streamlit** - Interactive web framework
- **Plotly** - Dynamic visualizations with interactivity
- **Pandas** - Data processing and analysis
- **Statsmodels** - Statistical analysis and correlations
- **Groq AI** - Natural language processing and insight generation

## Data Source

CDC PLACES 2022-2023 dataset
- Sleep deprivation data from 2022
- Lifestyle health metrics from 2023
- County-level aggregation from census tract data

## Team

**Team 18:**
- Akshitha Dubbaka
- Neha Nannapaneni
- Ruthvika Salloju



**Course:** ITCS 5122 U02 - Visual Analytics  
**Institution:** UNC Charlotte  
**Semester:** Spring 2026

## License

This project is for educational purposes as part of coursework at UNC Charlotte.
