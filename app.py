import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from groq import Groq 

# Initialize Groq client 
def get_groq_client():
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception as e:
        st.error("API key not found. Please add GROQ_API_KEY to .streamlit/secrets.toml")
        api_key = None
    if api_key:
        return Groq(api_key=api_key)
    return None
st.set_page_config(page_title="Sleep Clinic Analyzer", layout="wide")

# Title
st.title("🌙 Sleep Clinic Location Analyzer")
st.markdown("### Finding Optimal Locations for Sleep Clinic Placement")

# Load data
@st.cache_data
def load_data():
    import os
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to project directory
    project_dir = os.path.dirname(script_dir)
    # Build path to data file
    data_path = os.path.join(project_dir, 'data', 'counties_ranked.csv')
    
    df = pd.read_csv(data_path)
    
    # Add tier column if it doesn't exist
    if 'tier' not in df.columns:
        df['tier'] = pd.cut(df['opportunity_score'], 
                            bins=[0, 50, 70, 100], 
                            labels=['Tier 3', 'Tier 2', 'Tier 1'])
    
    return df
    
    # Add tier column if it doesn't exist
    if 'tier' not in df.columns:
        df['tier'] = pd.cut(df['opportunity_score'], 
                            bins=[0, 50, 70, 100], 
                            labels=['Tier 3', 'Tier 2', 'Tier 1'])
    
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")

# State filter
states = ['All States'] + sorted(df['StateDesc'].unique().tolist())
selected_state = st.sidebar.selectbox("Select State:", states)

# Tier filter
tiers = ['All Tiers', 'Tier 1', 'Tier 2', 'Tier 3']
selected_tier = st.sidebar.selectbox("Select Priority Tier:", tiers)

# Sleep deprivation range
sleep_col = 'Short sleep duration among adults'
min_sleep, max_sleep = st.sidebar.slider(
    "Sleep Deprivation Range (%):",
    float(df[sleep_col].min()),
    float(df[sleep_col].max()),
    (float(df[sleep_col].min()), float(df[sleep_col].max()))
)

# Filter data based on selections
filtered_df = df.copy()

if selected_state != 'All States':
    filtered_df = filtered_df[filtered_df['StateDesc'] == selected_state]

if selected_tier != 'All Tiers':
    filtered_df = filtered_df[filtered_df['tier'] == selected_tier]

filtered_df = filtered_df[
    (filtered_df[sleep_col] >= min_sleep) & 
    (filtered_df[sleep_col] <= max_sleep)
]

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Counties Shown", len(filtered_df))
with col2:
    st.metric("Total Adult Population", f"{filtered_df['TotalPop18plus'].sum():,.0f}")
with col3:
    st.metric("Avg Sleep Deprivation", f"{filtered_df[sleep_col].mean():.1f}%")
with col4:
    st.metric("Avg Opportunity Score", f"{filtered_df['opportunity_score'].mean():.1f}")

# Tab layout
tab1, tab2, tab3 = st.tabs(["📊 Top Counties", "🗺️ Geographic Analysis", "🔍 Correlation Analysis"])

with tab1:
    st.subheader("Top Counties by Opportunity Score")
    
    # Top N selector
    top_n = st.slider("Show top N counties:", 5, 50, 25)
    
    top_counties = filtered_df.nlargest(top_n, 'opportunity_score')
    
    # Create labels for y-axis
    top_counties['label'] = top_counties['CountyName'] + ', ' + top_counties['StateAbbr']
    
    # Bar chart
    fig = px.bar(
        top_counties,
        y='label',
        x='opportunity_score',
        color='tier',
        color_discrete_map={'Tier 1': '#C1292E', 'Tier 2': '#F1A208', 'Tier 3': '#2E86AB'},
        orientation='h',
        labels={'opportunity_score': 'Opportunity Score', 'label': 'County'},
        title=f'Top {top_n} Counties for Sleep Clinic Placement'
    )
    fig.update_layout(height=600, showlegend=True, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    display_df = top_counties[['CountyName', 'StateDesc', sleep_col, 'opportunity_score', 'TotalPop18plus', 'tier']].copy()
    display_df.columns = ['County', 'State', 'Sleep Deprivation (%)', 'Opportunity Score', 'Population', 'Tier']
    st.dataframe(display_df, use_container_width=True)

with tab2:
    st.subheader("Geographic Distribution")
    
    # State summary
    state_summary = filtered_df.groupby('StateDesc').agg({
        'CountyFIPS': 'count',
        'TotalPop18plus': 'sum',
        sleep_col: 'mean',
        'opportunity_score': 'mean'
    }).reset_index()
    state_summary.columns = ['State', 'Counties', 'Total Population', 'Avg Sleep Deprivation (%)', 'Avg Opportunity Score']
    state_summary = state_summary.sort_values('Avg Opportunity Score', ascending=False)
    
    # Bar chart by state
    fig = px.bar(
        state_summary.head(15),
        x='State',
        y='Avg Opportunity Score',
        color='Avg Sleep Deprivation (%)',
        color_continuous_scale='YlOrRd',
        title='Top 15 States by Opportunity Score'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("State Summary Table")
    st.dataframe(state_summary, use_container_width=True)

with tab3:
    st.subheader("Correlation Analysis")
    
    # Scatter plot
    x_var = st.selectbox("Select X-axis variable:", 
                         ['Obesity among adults', 'No leisure-time physical activity among adults', 
                          'Diagnosed diabetes among adults', 'Frequent mental distress among adults',
                          'Current cigarette smoking among adults'])
    
    fig = px.scatter(
        filtered_df,
        x=x_var,
        y=sleep_col,
        size='TotalPop18plus',
        color='opportunity_score',
        hover_name='CountyName',
        hover_data={'StateDesc': True, sleep_col: ':.1f', x_var: ':.1f'},
        trendline='ols',
        color_continuous_scale='YlOrRd',
        labels={x_var: x_var, sleep_col: 'Sleep Deprivation (%)'},
        title=f'{x_var} vs Sleep Deprivation'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation value
    corr = filtered_df[x_var].corr(filtered_df[sleep_col])
    st.metric(f"Correlation: {x_var} vs Sleep Deprivation", f"{corr:.3f}")

# Footer
# ==================== PHASE 2 FEATURE ====================
st.markdown("---")
st.header("🔄 Phase 2: County Comparison Tool")
st.markdown("*Self-Generated Expansion Feature: Compare counties side-by-side for informed decision-making*")

# Two-column layout for county selection
col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 County A")
    county1 = st.selectbox("Select First County:", sorted(df['CountyName'].unique()), key='county1')
    
with col2:
    st.subheader("📍 County B")
    county2 = st.selectbox("Select Second County:", sorted(df['CountyName'].unique()), key='county2')

# Get data for selected counties
data1 = df[df['CountyName'] == county1].iloc[0]
data2 = df[df['CountyName'] == county2].iloc[0]

# Comparison metrics with delta indicators
st.subheader("Key Metrics Comparison")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(
        label="Sleep Deprivation",
        value=f"{data1[sleep_col]:.1f}%",
        delta=f"{data1[sleep_col] - data2[sleep_col]:.1f}%",
        delta_color="inverse"
    )
    
with metric_col2:
    st.metric(
        label="Opportunity Score",
        value=f"{data1['opportunity_score']:.1f}",
        delta=f"{data1['opportunity_score'] - data2['opportunity_score']:.1f}"
    )
    
with metric_col3:
    st.metric(
        label="Adult Population",
        value=f"{data1['TotalPop18plus']:,.0f}",
        delta=f"{int(data1['TotalPop18plus'] - data2['TotalPop18plus']):,}"
    )

with metric_col4:
    winner = county1 if data1['opportunity_score'] > data2['opportunity_score'] else county2
    st.metric(
        label="Recommended",
        value=winner[:15] + "..."
    )

# Side-by-side health metrics comparison
st.subheader("Health Metrics Comparison")

comparison_data = []
metrics = [
    ('Sleep Deprivation', sleep_col),
    ('Obesity', 'Obesity among adults'),
    ('Physical Inactivity', 'No leisure-time physical activity among adults'),
    ('Diabetes', 'Diagnosed diabetes among adults'),
    ('Mental Distress', 'Frequent mental distress among adults')
]

for metric_name, metric_col_name in metrics:
    comparison_data.append({
        'Metric': metric_name,
        f"{data1['CountyName']}, {data1['StateAbbr']}": data1[metric_col_name],
        f"{data2['CountyName']}, {data2['StateAbbr']}": data2[metric_col_name]
    })

comparison_df = pd.DataFrame(comparison_data)

# Create grouped bar chart
fig = px.bar(
    comparison_df,
    x='Metric',
    y=[f"{data1['CountyName']}, {data1['StateAbbr']}", 
       f"{data2['CountyName']}, {data2['StateAbbr']}"],
    barmode='group',
    title='Head-to-Head Health Metrics Comparison',
    labels={'value': 'Percentage (%)', 'variable': 'County'},
    color_discrete_sequence=['#C1292E', '#2E86AB']
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

# Winner analysis
st.subheader("Decision Support")
col_a, col_b = st.columns(2)

with col_a:
    st.markdown(f"**{data1['CountyName']}, {data1['StateAbbr']}**")
    st.write(f"• Tier: {data1['tier']}")
    st.write(f"• Opportunity Score: {data1['opportunity_score']:.1f}")
    st.write(f"• Sleep Deprivation: {data1[sleep_col]:.1f}%")
    st.write(f"• Population: {data1['TotalPop18plus']:,.0f}")

with col_b:
    st.markdown(f"**{data2['CountyName']}, {data2['StateAbbr']}**")
    st.write(f"• Tier: {data2['tier']}")
    st.write(f"• Opportunity Score: {data2['opportunity_score']:.1f}")
    st.write(f"• Sleep Deprivation: {data2[sleep_col]:.1f}%")
    st.write(f"• Population: {data2['TotalPop18plus']:,.0f}")

if data1['opportunity_score'] > data2['opportunity_score']:
    st.success(f"✅ **Recommendation:** {data1['CountyName']}, {data1['StateAbbr']} has a higher opportunity score ({data1['opportunity_score']:.1f} vs {data2['opportunity_score']:.1f})")
else:
    st.success(f"✅ **Recommendation:** {data2['CountyName']}, {data2['StateAbbr']} has a higher opportunity score ({data2['opportunity_score']:.1f} vs {data1['opportunity_score']:.1f})")
st.markdown("---")
# ==================== AI FEATURE 1: NATURAL LANGUAGE QUERY ====================
st.markdown("---")
st.header("🤖 AI-Powered Natural Language Query")
st.markdown("*Ask questions about the data in plain English*")

user_query = st.text_input(
    "Ask a question:",
    placeholder="Example: Show me counties in Alabama with high obesity"
)

if user_query:
    with st.spinner("🤖 AI is analyzing your question..."):
        try:
            client = get_groq_client()
            
            # Create prompt for AI
            prompt = f"""You are a data analysis assistant. The user has a dataset of 677 U.S. counties with health metrics.

Available filters:
- States: {', '.join(sorted(df['StateDesc'].unique().tolist()))}
- Health metrics: Sleep Deprivation, Obesity, Physical Inactivity, Diabetes, Mental Distress, Smoking
- Opportunity Score (0-100)
- Priority Tier (1, 2, 3)

User question: "{user_query}"

Respond with a JSON object containing filter parameters. Example:
{{"state": "Alabama", "min_obesity": 30, "min_sleep": 35, "explanation": "Showing Alabama counties with obesity above 30% and sleep deprivation above 35%"}}

Only respond with valid JSON, no other text."""

            # Call Groq API
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.3,
            )
            
            response = chat_completion.choices[0].message.content
            
            # Display AI response
            st.success(f"🤖 AI Understanding: {response}")
            
            # Try to parse and filter data
            import json
            try:
                filters = json.loads(response)
                filtered_data = df.copy()
                
                if 'state' in filters and filters['state']:
                    filtered_data = filtered_data[filtered_data['StateDesc'].str.contains(filters['state'], case=False, na=False)]
                
                if 'min_obesity' in filters:
                    filtered_data = filtered_data[filtered_data['Obesity among adults'] >= filters['min_obesity']]
                
                if 'min_sleep' in filters:
                    filtered_data = filtered_data[filtered_data[sleep_col] >= filters['min_sleep']]
                
                st.write(f"**Found {len(filtered_data)} counties matching your criteria:**")
                st.dataframe(filtered_data[['CountyName', 'StateDesc', sleep_col, 'Obesity among adults', 'opportunity_score']].head(10))
                
            except:
                st.info("AI understood your question but couldn't apply filters automatically. Try rephrasing!")
                
        except Exception as e:
            st.error(f"AI Error: {str(e)}")

# ==================== AI FEATURE 2: AUTO INSIGHTS ====================
st.markdown("---")
st.header("💡 AI-Generated Insights")

if st.button("🤖 Generate AI Insights About This Data"):
    with st.spinner("🤖 AI is analyzing the data..."):
        try:
            client = get_groq_client()
            
            # Get top counties
            top_5 = df.nlargest(5, 'opportunity_score')[['CountyName', 'StateDesc', sleep_col, 'opportunity_score']]
            top_states = df.groupby('StateDesc')['opportunity_score'].mean().nlargest(3)
            
            # Create prompt
            prompt = f"""You are a healthcare business analyst. Analyze this sleep clinic opportunity data and provide 3-4 key insights.

Top 5 Counties:
{top_5.to_string()}

Top 3 States by Average Opportunity Score:
{top_states.to_string()}

Total counties analyzed: {len(df)}
Average sleep deprivation: {df[sleep_col].mean():.1f}%
Highest obesity correlation: r=0.784

Provide 3-4 bullet points with actionable business insights. Be specific and mention county/state names. Keep it concise."""

            # Call Groq API
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.7,
            )
            
            insights = chat_completion.choices[0].message.content
            
            st.success("🤖 **AI-Generated Insights:**")
            st.markdown(insights)
            
        except Exception as e:
            st.error(f"AI Error: {str(e)}")
st.markdown("**Team 18:** Neha Nannapaneni, Akshitha Dubbaka, Ruthvika Salloju")
