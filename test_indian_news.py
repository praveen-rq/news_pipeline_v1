#!/usr/bin/env python3
"""
Test script for the Indian News Pipeline
This demonstrates the functionality without requiring actual API keys
"""

import json
from datetime import datetime

def test_pipeline_demo():
    """Demonstrate the pipeline functionality with mock data"""
    
    print("🚀 Indian News Pipeline Demo")
    print("=" * 50)
    
    # Mock Indian news articles (similar to what would come from NewsAPI)
    mock_articles = [
        {
            "title": "India Wins Cricket World Cup Semi-Final Against Australia",
            "description": "In a thrilling match, Team India defeated Australia by 5 wickets to secure their place in the World Cup final. Virat Kohli scored a brilliant century.",
            "url": "https://example.com/news1",
            "publishedAt": "2024-01-15T10:30:00Z",
            "source": {"name": "Times of India Sports"}
        },
        {
            "title": "New Metro Line Opens in Mumbai, Reduces Commute Time by 40%",
            "description": "The newly inaugurated Metro Line 3 in Mumbai has started operations, connecting Colaba to SEEPZ and significantly reducing travel time for thousands of commuters.",
            "url": "https://example.com/news2",
            "publishedAt": "2024-01-15T09:15:00Z",
            "source": {"name": "Mumbai Mirror"}
        },
        {
            "title": "India's Space Mission Successfully Lands on Moon's South Pole",
            "description": "ISRO's Chandrayaan-4 mission has achieved a historic milestone by successfully landing near the Moon's south pole, making India the first country to accomplish this feat.",
            "url": "https://example.com/news3",
            "publishedAt": "2024-01-15T08:00:00Z",
            "source": {"name": "The Hindu Science"}
        }
    ]
    
    print("📰 Fetched Top 3 Indian News Articles:")
    print("-" * 30)
    for i, article in enumerate(mock_articles, 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Description: {article['description'][:80]}...")
        print()
    
    # Mock Gemini-generated tweet (what the AI would create)
    mock_tweet = "🇮🇳 Cricket fever + Metro magic + Moon mission success! India's having quite the day - from World Cup finals to space victories, we're literally reaching for the stars! 🏏🚇🌙 #IndiaShines #ProudMoment ✨"
    
    print("🤖 Generated Tweet (Gemini AI):")
    print("-" * 30)
    print(f'"{mock_tweet}"')
    print(f"Character count: {len(mock_tweet)}/280")
    print()
    
    # Mock data structure that would be stored in Supabase
    news_data = {
        "articles": mock_articles,
        "generated_tweet": mock_tweet,
        "processing_timestamp": datetime.now().isoformat(),
        "article_count": len(mock_articles)
    }
    
    supabase_record = {
        "source": "indian_news_pipeline",
        "news": news_data,
        "status": True
    }
    
    print("💾 Data Structure for Supabase:")
    print("-" * 30)
    print(json.dumps(supabase_record, indent=2, default=str))
    print()
    
    print("✅ Pipeline Demo Completed Successfully!")
    print()
    print("📋 Next Steps:")
    print("1. Get NewsAPI key from https://newsapi.org/")
    print("2. Get Gemini API key from https://makersuite.google.com/app/apikey")
    print("3. Add keys to your .env file")
    print("4. Run: python src/indian_news_pipeline.py")

if __name__ == "__main__":
    test_pipeline_demo() 