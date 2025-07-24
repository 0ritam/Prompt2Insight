import requests
from bs4 import BeautifulSoup
from gnews import GNews
from youtube_transcript_api import YouTubeTranscriptApi
import trafilatura
from typing import List

class DataScraper:
    """
    A class to scrape data from Google News and YouTube reviews.
    """

    def scrape_google_news(self, product_name: str, limit: int = 3) -> List[str]:
        """
        Scrapes Google News for articles about a product.

        Args:
            product_name: The name of the product to search for.
            limit: The maximum number of articles to scrape.

        Returns:
            A list of strings, where each string is the text content of an article.
        """
        article_texts = []
        try:
            google_news = GNews()
            google_news.language = 'en'
            google_news.country = 'us'
            
            # Get articles without any keyword arguments to avoid API issues
            print(f"Searching for news articles about: {product_name}")
            articles = google_news.get_news(product_name)
            
            # Limit the results manually
            if articles:
                articles = articles[:limit]
                print(f"Found {len(articles)} articles to process")
                
                for i, article in enumerate(articles):
                    try:
                        print(f"Processing article {i+1}: {article.get('title', 'No title')}")
                        
                        # Try to get full article content using trafilatura
                        try:
                            downloaded = trafilatura.fetch_url(article['url'])
                            if downloaded:
                                # More aggressive extraction with additional options
                                article_text = trafilatura.extract(
                                    downloaded, 
                                    include_comments=False,
                                    include_tables=True,
                                    include_formatting=False,
                                    favor_precision=False  # Favor recall over precision
                                )
                                if article_text and article_text.strip() and len(article_text.strip()) > 100:
                                    article_texts.append(article_text)
                                    print(f"✅ Successfully extracted full article {i+1} using trafilatura ({len(article_text)} chars)")
                                    continue
                                else:
                                    print(f"⚠️ Trafilatura extracted minimal content for article {i+1} ({len(article_text) if article_text else 0} chars)")
                        except Exception as trafilatura_error:
                            print(f"❌ Trafilatura extraction failed for article {i+1}: {trafilatura_error}")
                        
                        # Fallback: try gnews get_full_article method
                        try:
                            full_article = google_news.get_full_article(article['url'])
                            if full_article and hasattr(full_article, 'html') and full_article.html:
                                soup = BeautifulSoup(full_article.html, 'html.parser')
                                paragraphs = soup.find_all('p')
                                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                                if article_text.strip() and len(article_text.strip()) > 100:
                                    article_texts.append(article_text)
                                    print(f"✅ Successfully extracted full article {i+1} using gnews fallback ({len(article_text)} chars)")
                                    continue
                                else:
                                    print(f"⚠️ GNews extracted minimal content for article {i+1}")
                        except Exception as gnews_error:
                            print(f"❌ GNews extraction failed for article {i+1}: {gnews_error}")
                        
                        # Final fallback: use available article metadata (title, description, etc.)
                        fallback_content = []
                        if article.get('title'):
                            fallback_content.append(f"Title: {article['title']}")
                        if article.get('description'):
                            fallback_content.append(f"Description: {article['description']}")
                        if article.get('published date'):
                            fallback_content.append(f"Published: {article['published date']}")
                        
                        if fallback_content:
                            article_text = ' '.join(fallback_content)
                            article_texts.append(article_text)
                            print(f"📄 Using article metadata for article {i+1} ({len(article_text)} chars)")
                        else:
                            print(f"❌ Could not extract any content for article {i+1}")
                            
                    except Exception as article_error:
                        print(f"Error processing individual article {i+1}: {article_error}")
                        continue
            else:
                print("No articles found for this search term")

        except Exception as e:
            print(f"An error occurred while scraping Google News: {e}")
        
        print(f"Successfully extracted {len(article_texts)} articles")
        return article_texts

    def scrape_youtube_reviews(self, product_name: str, limit: int = 2) -> List[str]:
        """
        Scrapes YouTube for video review transcripts about a product.

        Args:
            product_name: The name of the product to search for.
            limit: The maximum number of video transcripts to scrape.

        Returns:
            A list of strings, where each string is the full transcript of a video.
        """
        transcript_texts = []
        try:
            # This is a simplified way to get video IDs. 
            # A more robust solution would use the YouTube Data API.
            search_query = f"{product_name} review"
            search_url = f"https://www.youtube.com/results?search_query={search_query.replace(' ', '+')}"
            
            response = requests.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            video_ids = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and href.startswith('/watch?v='):
                    video_id = href.replace('/watch?v=', '')
                    if video_id not in video_ids:
                        video_ids.append(video_id)
                if len(video_ids) >= limit * 2: # get more to filter for transcripts
                    break
            
            count = 0
            for video_id in video_ids:
                if count >= limit:
                    break
                try:
                    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US'])
                    transcript = ' '.join([item['text'] for item in transcript_list])
                    transcript_texts.append(transcript)
                    count += 1
                except Exception:
                    # Transcript not available for this video, just skip it.
                    continue

        except Exception as e:
            print(f"An error occurred while scraping YouTube transcripts: {e}")
            
        return transcript_texts

if __name__ == '__main__':
    # Example Usage
    scraper = DataScraper()
    
    # Test Google News
    print("--- Scraping Google News for 'iPhone 15' ---")
    news = scraper.scrape_google_news("iPhone 15")
    if news:
        print(f"Found {len(news)} articles.")
        print("First article snippet:")
        print(news[0][:500] + "...")
    else:
        print("No articles found.")
        
    print("\n" + "="*50 + "\n")
    
    # Test YouTube Reviews
    print("--- Scraping YouTube for 'Pixel 8 Pro' review transcripts ---")
    transcripts = scraper.scrape_youtube_reviews("Pixel 8 Pro")
    if transcripts:
        print(f"Found {len(transcripts)} transcripts.")
        print("First transcript snippet:")
        print(transcripts[0][:500] + "...")
    else:
        print("No transcripts found.")
