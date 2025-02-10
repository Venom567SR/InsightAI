from typing import List, Optional
from pydantic import BaseModel, Field
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from exa_py import Exa
from langchain.schema import HumanMessage

class CompetitorAnalyzer:
    def __init__(self, EXA_API_KEY: str, GOOGLE_API_KEY: str):
        self.exa = Exa(api_key=EXA_API_KEY)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY
        )
    
    def get_competitor_urls(self, description: str, country: Optional[str] = None) -> List[str]:
        try:
            search_query = f"{description}"
            if country and country != "Global":
                search_query += f" companies in {country}"
            
            results = self.exa.search(
                query=search_query,
                num_results=3,
                type="neural",
                category="company"
            )
            
            urls = []
            if hasattr(results, 'results'):
                urls = [result.url for result in results.results]
            
            return urls[:3]
            
        except Exception as e:
            print(f"Error in get_competitor_urls: {e}")
            raise Exception(f"Failed to fetch competitor URLs: {str(e)}")

    def analyze_competitors(self, competitor_data: List[dict]) -> dict:
        try:
            country_context = competitor_data[0].get('country', 'Global') if competitor_data else 'Global'
            
            prompt = HumanMessage(content=f"""
            As a competitive analysis expert, analyze these competitors in the {country_context} market:
            {json.dumps(competitor_data, indent=2)}

            Based on their websites and market presence, provide a detailed analysis focusing on:
            1. Market gaps they're not addressing
            2. Their key weaknesses
            3. Features that could differentiate from them
            4. Pricing strategy recommendations
            5. Growth opportunities in {country_context}

            Return your analysis in this exact JSON format:
            {{
                "market_gaps": [
                    "Specific gap 1 with explanation",
                    "Specific gap 2 with explanation",
                    "Specific gap 3 with explanation"
                ],
                "competitor_weaknesses": [
                    "Detailed weakness 1",
                    "Detailed weakness 2",
                    "Detailed weakness 3"
                ],
                "recommended_features": [
                    "Specific feature 1 with justification",
                    "Specific feature 2 with justification",
                    "Specific feature 3 with justification"
                ],
                "pricing_strategy": "Detailed pricing recommendation based on competitor analysis",
                "growth_opportunities": [
                    "Specific opportunity 1 in {country_context}",
                    "Specific opportunity 2 in {country_context}",
                    "Specific opportunity 3 in {country_context}"
                ]
            }}

            Ensure all recommendations are specific, actionable, and based on the competitor data provided.
            """)
            
            response = self.llm.invoke([prompt])

            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)

            clean_response = content.strip()
            if '```json' in clean_response:
                clean_response = clean_response.split('```json')[1].split('```')[0]
            
            try:
                analysis_result = json.loads(clean_response)

                required_keys = ["market_gaps", "competitor_weaknesses", 
                               "recommended_features", "pricing_strategy", 
                               "growth_opportunities"]
                
                if all(key in analysis_result for key in required_keys):
                    return analysis_result
                else:
                    raise ValueError("Missing required keys in analysis result")
                    
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing response: {e}")
                return {
                    "market_gaps": [
                        "Untapped market segment identified",
                        "Service quality gap",
                        "Technology implementation gap"
                    ],
                    "competitor_weaknesses": [
                        "Limited feature set",
                        "Poor user experience",
                        "Lack of innovation"
                    ],
                    "recommended_features": [
                        "AI-powered analytics",
                        "Advanced automation capabilities",
                        "Integrated workflow solutions"
                    ],
                    "pricing_strategy": "Implement a value-based pricing model with competitive entry-level options",
                    "growth_opportunities": [
                        "Expand to enterprise market",
                        "Develop industry-specific solutions",
                        "Focus on international expansion"
                    ]
                }
                
        except Exception as e:
            print(f"Error in analyze_competitors: {e}")
            return {
                "market_gaps": [
                    "Error analyzing market gaps",
                    "Please try again with more specific competitor information"
                ],
                "competitor_weaknesses": [
                    "Error analyzing competitor weaknesses",
                    "Please check the competitor data provided"
                ],
                "recommended_features": [
                    "Error generating feature recommendations",
                    "Please ensure competitor information is complete"
                ],
                "pricing_strategy": "Error determining pricing strategy. Please try again.",
                "growth_opportunities": [
                    "Error analyzing growth opportunities",
                    "Please verify the market context provided"
                ]
            }