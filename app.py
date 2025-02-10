import streamlit as st
import os
from dotenv import load_dotenv
from utils.competitor_analysis import CompetitorAnalyzer
from typing import Dict

load_dotenv()

st.set_page_config(
    page_title="InsightsAI - Competitor Analysis",
    layout="wide"
)

if 'competitor_data' not in st.session_state:
    st.session_state.competitor_data = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

def format_analysis_results(results: Dict) -> str:
    """Format analysis results in markdown."""
    formatted_text = ""
    
    #snippet for Market Gaps
    formatted_text += "### 🎯 Market Gaps\n"
    for gap in results.get('market_gaps', []):
        formatted_text += f"* {gap}\n"
    
    #snippet for Competitor Weaknesses
    formatted_text += "\n### ⚠️ Competitor Weaknesses\n"
    for weakness in results.get('competitor_weaknesses', []):
        formatted_text += f"* {weakness}\n"
    
    #snippet for Recommended Features
    formatted_text += "\n### 💡 Recommended Features\n"
    for feature in results.get('recommended_features', []):
        formatted_text += f"* {feature}\n"
    
    #snippet for Pricing Strategy
    formatted_text += "\n### 💰 Pricing Strategy\n"
    formatted_text += f"* {results.get('pricing_strategy', 'No strategy available')}\n"
    
    #snippet for Growth Opportunities
    formatted_text += "\n### 📈 Growth Opportunities\n"
    for opportunity in results.get('growth_opportunities', []):
        formatted_text += f"* {opportunity}\n"
    
    return formatted_text

st.title("🎯 InsightsAI - Competitor Intelligence Platform")

overview_tab, analysis_tab = st.tabs([
    "Overview", "Analysis Results"
])

with overview_tab:
    st.header("Competitor Analysis")
    
    st.subheader("Enter Your Company Information")

    description = st.text_area(
        "Describe your company and its products/services:",
        help="Provide a detailed description of your company's products, services, target market, and key features",
        key="company_desc"
    )

    #Snippet for Country filter
    country = st.selectbox(
        "Select target country for competitor analysis:",
        ["United States", "United Kingdom", "Canada", "Australia", "India", 
         "Germany", "France", "Spain", "Italy", "Japan", "Global"],
        index=10,  #Keeping Default as "Global"
        help="Select the country to focus the competitor analysis on"
    )

    if st.button("Find & Analyze Competitors", type="primary"):
        if description:
            try:
                EXA_API_KEY = os.getenv('EXA_API_KEY')
                GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
                
                if not EXA_API_KEY or not GOOGLE_API_KEY:
                    st.error("Missing API keys. Please check your environment configuration.")
                    st.stop()
                    
                with st.spinner("🔍 Finding and analyzing competitors..."):
                    analyzer = CompetitorAnalyzer(
                        EXA_API_KEY=EXA_API_KEY,
                        GOOGLE_API_KEY=GOOGLE_API_KEY
                    )

                    competitor_urls = analyzer.get_competitor_urls(
                        description=description,
                        country=country if country != "Global" else None
                    )
                    
                    st.write("Found competitors:", competitor_urls)
                    
                    competitor_data = [
                        {
                            "company_name": f"Competitor {i+1}",
                            "url": url,
                            "country": country,
                            "key_features": ["AI Models", "APIs", "Tools"],
                            "tech_stack": ["Python", "TensorFlow", "PyTorch"],
                            "marketing_focus": "Enterprise AI Solutions",
                            "customer_feedback": "Positive"
                        }
                        for i, url in enumerate(competitor_urls)
                    ]
                    
                    st.session_state.competitor_data = competitor_data
                    st.session_state.analysis_results = analyzer.analyze_competitors(competitor_data)
                    
                    st.success("✅ Analysis complete! Switch to Analysis Results tab to view results.")
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
        else:
            st.warning("Please provide your company description.")

with analysis_tab:
    if st.session_state.analysis_results:
        st.header("Competitive Analysis Results")

        if st.session_state.competitor_data:
            st.subheader("Identified Competitors")
            for comp in st.session_state.competitor_data:
                st.markdown(f"* [{comp['company_name']}]({comp['url']}) - {comp['country']}")
        
        st.markdown(format_analysis_results(st.session_state.analysis_results))
        
    else:
        st.info("👉 Run the analysis first to view results.")