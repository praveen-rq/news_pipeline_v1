#!/usr/bin/env python3
"""
Indian News Pipeline Script

This script:
1. Fetches top 3 Indian sports & general news articles
2. Uses Gemini LLM to create informational yet funny tweets
3. Stores the results in Supabase database

Requirements:
- News API key for fetching Indian news
- Gemini API key for LLM processing
- Supabase credentials for database storage
"""

import os
import json
import requests
import logging
import traceback
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IndianNewsProcessor:
    """Main class for processing Indian news and creating tweets"""
    
    def __init__(self):
        """Initialize the news processor with API clients"""
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.supabase_url = os.getenv('SUPARBASE_DATA_PIP_PROJECT_URL')
        self.supabase_key = os.getenv('SUPABASE_DATA_PIP_KEY')
        
        # Initialize Gemini AI
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.error("Gemini API key not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Initialize Supabase client
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            logger.error("Supabase credentials not found in environment variables")
            raise ValueError("SUPARBASE_DATA_PIP_PROJECT_URL and SUPABASE_DATA_PIP_KEY are required")
        
        logger.info("Indian News Processor initialized successfully")
    
    def fetch_indian_news(self, category: str = "general", limit: int = 3) -> List[Dict[str, Any]]:
        """
        Fetch top Indian news articles using NewsAPI
        
        Args:
            category: News category (general, sports, etc.)
            limit: Number of articles to fetch
            
        Returns:
            List of news articles
        """
        try:
            # Using NewsAPI for Indian news
            base_url = "https://newsapi.org/v2/top-headlines"
            params = {
                'country': 'in',
                'category': category,
                'apiKey': self.news_api_key,
                'pageSize': limit
            }
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            news_data = response.json()
            
            if news_data.get('status') == 'ok':
                articles = news_data.get('articles', [])
                logger.info(f"Successfully fetched {len(articles)} {category} news articles")
                return articles
            else:
                logger.error(f"NewsAPI error: {news_data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {str(e)}")
            return []
    
    def fetch_alternative_indian_news(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Alternative method to fetch Indian news using RSS feeds
        (In case NewsAPI is not available)
        """
        try:
            import feedparser
            
            # Indian news RSS feeds
            rss_feeds = [
                "https://feeds.feedburner.com/ndtvnews-top-stories",
                "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
                "https://www.thehindu.com/news/national/feeder/default.rss"
            ]
            
            articles = []
            for feed_url in rss_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:2]:  # Get 2 from each feed
                        article = {
                            'title': entry.title,
                            'description': getattr(entry, 'summary', ''),
                            'url': entry.link,
                            'publishedAt': getattr(entry, 'published', ''),
                            'source': {'name': feed.feed.title}
                        }
                        articles.append(article)
                        if len(articles) >= limit:
                            break
                    if len(articles) >= limit:
                        break
                except Exception as e:
                    logger.warning(f"Error parsing RSS feed {feed_url}: {str(e)}")
                    continue
            
            logger.info(f"Successfully fetched {len(articles)} articles from RSS feeds")
            return articles[:limit]
            
        except ImportError:
            logger.error("feedparser not installed. Install with: pip install feedparser")
            return []
        except Exception as e:
            logger.error(f"Error fetching RSS news: {str(e)}")
            return []
    
    def create_tweet_with_gemini(self, articles: List[Dict[str, Any]]) -> str:
        """
        Use Gemini LLM to create an informational yet funny tweet from news articles
        
        Args:
            articles: List of news articles
            
        Returns:
            Generated tweet text
        """
        try:
            # Prepare articles summary for Gemini
            articles_text = ""
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'No title')
                description = article.get('description', 'No description')
                articles_text += f"{i}. {title}\n   {description}\n\n"
            
            # Create prompt for Gemini
            prompt = f"""
            Based on these top 3 Indian news articles, create a single informational yet funny tweet (max 280 characters).
            The tweet should:
            1. Be informative and capture key news points
            2. Add a touch of humor without being insensitive
            3. Be engaging for social media
            4. Stay within Twitter's character limit
            5. Use appropriate emojis if suitable
            
            News Articles:
            {articles_text}
            
            Create just the tweet text, nothing else:
            """
            
            response = self.gemini_model.generate_content(prompt)
            tweet = response.text.strip()
            
            # Ensure tweet is within character limit
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
            
            logger.info(f"Generated tweet: {tweet}")
            return tweet
            
        except Exception as e:
            logger.error(f"Error generating tweet with Gemini: {str(e)}")
            # Fallback tweet
            return "🇮🇳 Latest Indian news updates! Stay informed, stay awesome! 📰✨ #IndiaNews #StayInformed"
    
    def store_in_supabase(self, source: str, news_data: Dict[str, Any], status: bool = True) -> bool:
        """
        Store the processed news data in Supabase
        
        Args:
            source: News source identifier
            news_data: Dictionary containing news and tweet data
            status: Processing status
            
        Returns:
            Success status
        """
        try:
            # Prepare data for insertion according to the table schema
            insert_data = {
                'source': source,
                'news': news_data,
                'status': status
            }
            
            # Insert data into news_daily table
            response = (
                self.supabase.table('news_daily')
                .insert(insert_data)
                .execute()
            )
            
            logger.info(f"Successfully stored news data in Supabase: {response.data}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing data in Supabase: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def run_pipeline(self):
        """
        Main pipeline execution method
        """
        logger.info("Starting Indian News Pipeline...")
        
        try:
            # Step 1: Fetch news articles
            logger.info("Fetching Indian news articles...")
            
            # Try NewsAPI first, fallback to RSS if needed
            articles = []
            if self.news_api_key:
                # Fetch both general and sports news
                general_articles = self.fetch_indian_news("general", 2)
                sports_articles = self.fetch_indian_news("sports", 1)
                articles = general_articles + sports_articles
            
            # Fallback to RSS feeds if NewsAPI fails or no API key
            if not articles:
                logger.info("Falling back to RSS feeds...")
                articles = self.fetch_alternative_indian_news(3)
            
            if not articles:
                logger.error("No articles fetched. Pipeline failed.")
                return False
            
            # Step 2: Generate tweet with Gemini
            logger.info("Generating tweet with Gemini LLM...")
            tweet = self.create_tweet_with_gemini(articles)
            
            # Step 3: Prepare data for storage
            news_data = {
                'articles': articles,
                'generated_tweet': tweet,
                'processing_timestamp': datetime.now().isoformat(),
                'article_count': len(articles)
            }
            
            # Step 4: Store in Supabase
            logger.info("Storing data in Supabase...")
            success = self.store_in_supabase(
                source="indian_news_pipeline",
                news_data=news_data,
                status=True
            )
            
            if success:
                logger.info("✅ Pipeline completed successfully!")
                logger.info(f"Generated Tweet: {tweet}")
                return True
            else:
                logger.error("❌ Pipeline failed at storage step")
                return False
                
        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Store error information in Supabase
            error_data = {
                'error_message': str(e),
                'error_timestamp': datetime.now().isoformat(),
                'pipeline_step': 'execution'
            }
            
            self.store_in_supabase(
                source="indian_news_pipeline_error",
                news_data=error_data,
                status=False
            )
            
            return False

def main():
    """Main execution function"""
    try:
        processor = IndianNewsProcessor()
        success = processor.run_pipeline()
        
        if success:
            print("✅ Indian News Pipeline completed successfully!")
        else:
            print("❌ Indian News Pipeline failed!")
            
    except Exception as e:
        print(f"❌ Failed to initialize pipeline: {str(e)}")
        logger.error(f"Initialization error: {str(e)}")

if __name__ == "__main__":
    main() 