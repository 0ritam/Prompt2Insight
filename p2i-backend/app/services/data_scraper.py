import requests
from bs4 import BeautifulSoup
from gnews import GNews
from youtube_transcript_api import YouTubeTranscriptApi
import trafilatura
import feedparser
from typing import List
import os
import random

class DataScraper:
    """
    A class to scrape data from Google News, YouTube reviews, and RSS feeds.
    """

    def __init__(self):
        """Initialize the DataScraper with static user agent rotation."""
        # Static list of user agents to avoid async/event loop issues
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]

    def get_random_user_agent(self):
        """Get a random user agent from the static list."""
        return random.choice(self.user_agents)

    def _fetch_article_with_ua(self, url: str) -> str:
        """
        Smart scraper helper function that downloads and extracts content from a single URL
        while pretending to be a real browser using static User-Agent rotation.
        
        Args:
            url: The URL to fetch and extract content from.
            
        Returns:
            Extracted article text or None if failed.
        """
        try:
            # Get a random user agent from our static list
            user_agent = self.get_random_user_agent()
            headers = {'User-Agent': user_agent}
            
            # Use requests to get the content with headers and timeout
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # If download successful, use trafilatura to extract main article content
            extracted_text = trafilatura.extract(response.text)
            
            if extracted_text and len(extracted_text.strip()) > 100:
                print(f"   ✅ Successfully extracted content from {url} ({len(extracted_text)} chars)")
                return extracted_text
            else:
                print(f"   ⚠️ No meaningful content extracted from {url}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error fetching article from {url}: {e}")
            return None

    def _find_review_urls(self, product_name: str, num_results: int = 5) -> List[str]:
        """
        Source finder helper function that uses Serper.dev API to find the best article URLs.
        
        Args:
            product_name: The name of the product to search for.
            num_results: Number of search results to return.
            
        Returns:
            List of URLs from organic search results.
        """
        try:
            # Get SERPER_API_KEY from environment variables
            serper_api_key = os.getenv("SERPER_API_KEY")
            
            if not serper_api_key:
                print("⚠️ SERPER_API_KEY not found in environment variables")
                return []
            
            # Define the Serper API endpoint
            search_url = "https://google.serper.dev/search"
            
            # Create targeted search query payload
            payload = {
                "q": f"in-depth review for {product_name}",
                "num": num_results
            }
            
            # Define necessary headers including X-API-KEY
            headers = {
                "X-API-KEY": serper_api_key,
                "Content-Type": "application/json"
            }
            
            print(f"🔍 Searching Serper.dev for: {payload['q']}")
            
            # Make POST request to search_url
            response = requests.post(search_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse JSON response and extract URLs from organic search results
            data = response.json()
            urls = []
            
            organic_results = data.get("organic", [])
            for result in organic_results:
                link = result.get("link")
                if link:
                    urls.append(link)
                    print(f"   📰 Found: {result.get('title', 'No title')} - {link}")
            
            print(f"🎯 Serper.dev found {len(urls)} review URLs")
            return urls
            
        except Exception as e:
            print(f"❌ Error with Serper.dev API search: {e}")
            return []

    def scrape_from_rss(self, product_name: str) -> List[str]:
        """
        Scrapes RSS feeds for articles about a product.

        Args:
            product_name: The name of the product to search for.

        Returns:
            A list of strings, where each string is the text content of an article.
        """
        # RSS feeds list - you can add any RSS feed URLs here
        # The code will automatically process all feeds in this list
        rss_feeds = [
            "https://www.trustedreviews.com/reviews/mobile-phones/feed",
            "https://www.trustedreviews.com/reviews/computing/feed",
            "https://www.trustedreviews.com/best/feed"
            # Add more RSS feeds here - one per line
            # Example: "https://example.com/rss.xml",
        ]
        
        # Filter out any empty strings or None values
        rss_feeds = [feed.strip() for feed in rss_feeds if feed and feed.strip()]
        
        documents = []
        product_lower = product_name.lower()
        
        # Create flexible search terms
        search_terms = [product_lower]
        
        # Add variations for better matching
        product_words = product_lower.split()
        search_terms.extend(product_words)  # Add individual words
        
        if "iphone" in product_lower:
            search_terms.extend(["iphone", "apple", "ios"])
        elif "galaxy" in product_lower or "samsung" in product_lower:
            search_terms.extend(["galaxy", "samsung", "android"])
        elif "pixel" in product_lower:
            search_terms.extend(["pixel", "google", "android"])
        elif "oneplus" in product_lower or "one plus" in product_lower:
            search_terms.extend(["oneplus", "one plus", "android"])
        elif "xiaomi" in product_lower or "redmi" in product_lower:
            search_terms.extend(["xiaomi", "redmi", "mi", "android"])
        elif "oppo" in product_lower:
            search_terms.extend(["oppo", "android"])
        elif "vivo" in product_lower:
            search_terms.extend(["vivo", "android"])
        elif "realme" in product_lower:
            search_terms.extend(["realme", "android"])
        
        # Remove duplicates while preserving order
        search_terms = list(dict.fromkeys(search_terms))
        
        print(f"🔍 Searching RSS feeds for: {product_name}")
        print(f"🎯 Search terms: {search_terms}")
        print(f"📚 Total RSS feeds to check: {len(rss_feeds)}")
        
        successful_feeds = 0
        failed_feeds = 0
        
        for i, feed_url in enumerate(rss_feeds, 1):
            try:
                print(f"📡 [{i}/{len(rss_feeds)}] Parsing RSS feed: {feed_url}")
                
                # Add timeout and better error handling for feed parsing
                feed = feedparser.parse(feed_url)
                
                # Check if feed was parsed successfully
                if hasattr(feed, 'status') and feed.status >= 400:
                    print(f"❌ HTTP Error {feed.status} for feed: {feed_url}")
                    failed_feeds += 1
                    continue
                
                if feed.bozo and feed.bozo_exception:
                    print(f"⚠️ Feed parsing warning for {feed_url}: {feed.bozo_exception}")
                
                if not hasattr(feed, 'entries') or not feed.entries:
                    print(f"⚠️ No entries found in feed: {feed_url}")
                    failed_feeds += 1
                    continue
                
                print(f"✅ Successfully parsed feed with {len(feed.entries)} entries")
                successful_feeds += 1
                
                entries_found = 0
                for entry in feed.entries:
                    try:
                        title_lower = entry.title.lower()
                        
                        # Also check description/summary for matching
                        description_lower = ""
                        if hasattr(entry, 'summary') and entry.summary:
                            description_lower = entry.summary.lower()
                        
                        combined_text = f"{title_lower} {description_lower}"
                        
                        # Calculate relevance score
                        relevance_score = 0
                        matched_terms = []
                        
                        # Exact product name match gets highest score
                        if product_lower in combined_text:
                            relevance_score += 10
                            matched_terms.append(f"EXACT:'{product_lower}'")
                        
                        # Individual term matches get scores based on importance
                        for term in search_terms[1:]:  # Skip the full product name (already checked)
                            if term in combined_text:
                                if len(term) > 6:  # Brand names like "samsung", "xiaomi"
                                    relevance_score += 4
                                    matched_terms.append(f"BRAND:'{term}'")
                                elif len(term) > 3:  # Model terms like "note", "pro"  
                                    relevance_score += 2
                                    matched_terms.append(f"MODEL:'{term}'")
                                else:  # Short terms
                                    relevance_score += 1
                                    matched_terms.append(f"TERM:'{term}'")
                        
                        # Only include articles with relevance score >= 5 (instead of 1)
                        if relevance_score >= 5:
                            print(f"✅ Found relevant article (Score: {relevance_score}): {entry.title}")
                            print(f"   🎯 Matched: {', '.join(matched_terms)}")
                            
                            # Extract content with priority order
                            content = None
                            
                            # First try: Get full article content from URL using trafilatura
                            if hasattr(entry, 'link') and entry.link:
                                try:
                                    print(f"   🌐 Trying to fetch full article from: {entry.link}")
                                    downloaded = trafilatura.fetch_url(entry.link)
                                    if downloaded:
                                        article_text = trafilatura.extract(
                                            downloaded,
                                            include_comments=False,
                                            include_tables=True,
                                            include_formatting=False,
                                            favor_precision=False
                                        )
                                        if article_text and len(article_text.strip()) > 200:
                                            content = article_text
                                            print(f"   📄 Using trafilatura extraction ({len(content)} chars)")
                                except Exception as fetch_error:
                                    print(f"   ❌ Trafilatura fetch failed: {fetch_error}")
                            
                            # Fallback 1: entry.content
                            if not content and hasattr(entry, 'content') and entry.content:
                                content = entry.content[0].value
                                print(f"   📄 Using entry.content ({len(content)} chars)")
                            
                            # Fallback 2: entry.summary
                            elif not content and hasattr(entry, 'summary') and entry.summary:
                                content = entry.summary
                                print(f"   📄 Using entry.summary ({len(content)} chars)")
                            
                            if content:
                                # Clean HTML using BeautifulSoup
                                soup = BeautifulSoup(content, 'html.parser')
                                clean_text = soup.get_text(strip=True)
                                
                                # More lenient content length check
                                if len(clean_text) > 50:  # Reduced from 100 to 50
                                    # Add relevance metadata to the document
                                    enhanced_text = f"[Relevance: {relevance_score}/10] {clean_text}"
                                    documents.append(enhanced_text)
                                    entries_found += 1
                                    print(f"   ✅ Added high-relevance article ({len(clean_text)} chars)")
                                else:
                                    print(f"   ⚠️ Article too short ({len(clean_text)} chars), skipping")
                            else:
                                print(f"   ❌ No content found for article")
                        else:
                            print(f"❌ Low relevance article excluded (Score: {relevance_score}): {entry.title}")
                            print(f"   🎯 Matched: {', '.join(matched_terms) if matched_terms else 'None'}")
                            print(f"   📉 Below minimum threshold of 5/10 - not storing")
                    
                    except Exception as entry_error:
                        print(f"❌ Error processing entry: {entry_error}")
                        continue
                
                print(f"📊 Found {entries_found} relevant articles from {feed_url}")
                
            except Exception as feed_error:
                print(f"❌ Error parsing RSS feed {feed_url}: {feed_error}")
                failed_feeds += 1
                continue
        
        print(f"\n📈 RSS Processing Summary:")
        print(f"   ✅ Successful feeds: {successful_feeds}/{len(rss_feeds)}")
        print(f"   ❌ Failed feeds: {failed_feeds}/{len(rss_feeds)}")
        print(f"   🎯 Total articles extracted: {len(documents)}")
        
        return documents

    def get_documents(self, product_name: str) -> List[str]:
        """
        Primary method to get documents about a product using advanced multi-layered strategy.
        1st: Dynamic search-and-scrape using Serper.dev API + Smart Scraper
        2nd: RSS feeds fallback
        3rd: Google News fallback  
        4th: Google Search API fallback

        Args:
            product_name: The name of the product to search for.

        Returns:
            A list of strings, where each string is the text content of an article.
        """
        print(f"🚀 Starting advanced document collection for: {product_name}")
        
        # PRIMARY METHOD: Dynamic search-and-scrape using Serper.dev API
        print("🎯 Phase 1: Dynamic search-and-scrape with Serper.dev API...")
        review_urls = self._find_review_urls(product_name)
        
        documents = []
        if review_urls:
            print(f"📄 Found {len(review_urls)} review URLs, extracting content...")
            
            for i, url in enumerate(review_urls, 1):
                print(f"📰 [{i}/{len(review_urls)}] Processing: {url}")
                content = self._fetch_article_with_ua(url)
                
                if content:
                    # Add source information for tracking
                    enhanced_content = f"[Source: Serper.dev Search - Dynamic Scraper]\n\n{content}"
                    documents.append(enhanced_content)
            
            if documents:
                print(f"✅ Dynamic search-and-scrape successful! Found {len(documents)} high-quality documents")
                return documents
        
        # FALLBACK 1: RSS feeds
        print("📡 Dynamic search and scrape failed, falling back to RSS feeds...")
        documents = self.scrape_from_rss(product_name)
        
        if documents:
            print(f"✅ RSS scraping successful! Found {len(documents)} documents")
            return documents
        
        # FALLBACK 2: Google News
        print("📰 RSS scraping yielded no results, falling back to Google News...")
        documents = self.scrape_google_news(product_name)
        
        if documents:
            print(f"✅ Google News successful! Found {len(documents)} documents")
            return documents
        
        # FALLBACK 3: Google Search API (final fallback)
        print("🔍 Google News failed, trying Google Search API as final fallback...")
        documents = self.scrape_google_search_api(product_name)
        
        if documents:
            print(f"✅ Google Search API successful! Found {len(documents)} documents")
            return documents
        
        print("❌ All scraping methods failed - no documents found")
        return []

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
            print(f"🔍 Attempting to search for news articles about: {product_name}")
            
            # Direct HTTP request to Google News to avoid GNews library event loop issues
            search_url = f"https://news.google.com/rss/search?q={product_name}&hl=en-US&gl=US&ceid=US:en"
            
            try:
                # Use requests instead of GNews to avoid event loop issues
                response = requests.get(search_url, timeout=10)
                if response.status_code == 200:
                    # Parse the RSS feed
                    feed = feedparser.parse(response.text)
                    
                    if feed.entries:
                        articles = feed.entries[:limit]
                        print(f"Found {len(articles)} articles to process")
                        
                        for i, article in enumerate(articles):
                            try:
                                title = article.get('title', 'No title')
                                link = article.get('link', '')
                                print(f"Processing article {i+1}: {title}")
                                
                                if not link:
                                    continue
                                
                                # Try to get full article content using trafilatura
                                try:
                                    downloaded = trafilatura.fetch_url(link)
                                    if downloaded:
                                        # Extract content with trafilatura
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
                                            print(f"⚠️ Trafilatura extracted minimal content for article {i+1}")
                                except Exception as trafilatura_error:
                                    print(f"❌ Trafilatura extraction failed for article {i+1}: {trafilatura_error}")
                                
                                # Fallback: use metadata from the RSS feed
                                fallback_content = []
                                if title:
                                    fallback_content.append(f"Title: {title}")
                                if article.get('summary'):
                                    fallback_content.append(f"Description: {article.get('summary')}")
                                if article.get('published'):
                                    fallback_content.append(f"Published: {article.get('published')}")
                                
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
                        print("No articles found in the RSS feed")
                else:
                    print(f"❌ Failed to fetch news: HTTP status {response.status_code}")
            
            except Exception as request_error:
                print(f"❌ Error fetching Google News RSS: {request_error}")
                
                # Legacy method fallback using GNews only if the RSS method failed
                try:
                    # Only import GNews here if needed to avoid event loop issues
                    from gnews import GNews
                    print("⚠️ Falling back to GNews library (potential event loop issues)")
                    
                    google_news = GNews()
                    google_news.language = 'en'
                    google_news.country = 'us'
                    
                    # Only use the simplest method from GNews to reduce chances of event loop issues
                    articles = google_news.get_news(product_name)
                    
                    if articles:
                        articles = articles[:limit]
                        print(f"Found {len(articles)} articles using GNews fallback")
                        
                        for i, article in enumerate(articles):
                            # Just use the metadata without trying to fetch full content
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
                                print(f"📄 Using article metadata only for article {i+1}")
                    
                except Exception as gnews_error:
                    print(f"❌ GNews fallback also failed: {gnews_error}")

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

    def scrape_google_search_api(self, product_name: str, max_results: int = 5) -> List[str]:
        """
        Uses Google Custom Search API to find product information as final fallback.
        
        Args:
            product_name: The name of the product to search for.
            max_results: Maximum number of results to process.
            
        Returns:
            A list of strings containing extracted content from search results.
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            import trafilatura
            
            # Get API credentials
            api_key = os.getenv("GOOGLE_CSE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_CSE_ENGINE_ID")
            
            if not api_key or not search_engine_id:
                print("❌ Google Search API credentials not found in environment variables")
                return []
            
            # Search for product reviews and information
            search_queries = [
                f"{product_name} review",
                f"{product_name} problems issues",
                f"{product_name} user experience"
            ]
            
            all_documents = []
            
            for query in search_queries:
                try:
                    print(f"🔍 Searching Google for: {query}")
                    
                    # Call Google Custom Search API
                    params = {
                        "key": api_key,
                        "cx": search_engine_id,
                        "q": query,
                        "num": min(max_results, 10),  # Google API max is 10
                        "safe": "medium",
                        "lr": "lang_en"
                    }
                    
                    response = requests.get(
                        "https://www.googleapis.com/customsearch/v1", 
                        params=params, 
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        print(f"❌ Google API error: {response.status_code}")
                        continue
                    
                    data = response.json()
                    items = data.get("items", [])
                    
                    print(f"📄 Found {len(items)} search results for '{query}'")
                    
                    for item in items:
                        try:
                            url = item.get("link", "")
                            title = item.get("title", "")
                            snippet = item.get("snippet", "")
                            
                            if not url:
                                continue
                                
                            print(f"📰 Processing: {title}")
                            
                            # Try to extract full article content
                            content = None
                            try:
                                downloaded = trafilatura.fetch_url(url)
                                if downloaded:
                                    content = trafilatura.extract(
                                        downloaded,
                                        include_comments=False,
                                        include_tables=True,
                                        include_formatting=False
                                    )
                            except Exception as e:
                                print(f"⚠️ Trafilatura failed for {url}: {e}")
                            
                            # If trafilatura failed, use the snippet from search results
                            if not content or len(content.strip()) < 100:
                                content = f"Title: {title}\n\nSummary: {snippet}"
                                print(f"📝 Using search snippet ({len(content)} chars)")
                            else:
                                print(f"📄 Extracted full content ({len(content)} chars)")
                            
                            if content:
                                # Add source information
                                enhanced_content = f"[Source: Google Search - {title}]\n\n{content}"
                                all_documents.append(enhanced_content)
                                
                        except Exception as e:
                            print(f"❌ Error processing search result: {e}")
                            continue
                    
                    # Don't hammer the API - small delay between queries
                    import time
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error with search query '{query}': {e}")
                    continue
            
            print(f"🎯 Google Search API extracted {len(all_documents)} documents total")
            return all_documents
            
        except Exception as e:
            print(f"❌ Google Search API fallback failed: {e}")
            return []

if __name__ == '__main__':
    # Example Usage
    scraper = DataScraper()
    
    # Test the new RSS + fallback method
    print("--- Testing New RSS-First Document Collection for 'iPhone 15' ---")
    documents = scraper.get_documents("iPhone 15")
    if documents:
        print(f"Found {len(documents)} documents total.")
        print("First document snippet:")
        print(documents[0][:500] + "...")
    else:
        print("No documents found.")
        
    print("\n" + "="*50 + "\n")
    
    # Test RSS feeds directly
    print("--- Testing Direct RSS Feed Scraping for 'Pixel 8' ---")
    rss_docs = scraper.scrape_from_rss("Pixel 8")
    if rss_docs:
        print(f"Found {len(rss_docs)} RSS documents.")
        print("First RSS document snippet:")
        print(rss_docs[0][:500] + "...")
    else:
        print("No RSS documents found.")
        
    print("\n" + "="*50 + "\n")
    
    # Test YouTube Reviews
    print("--- Scraping YouTube for 'Samsung Galaxy S24' review transcripts ---")
    transcripts = scraper.scrape_youtube_reviews("Samsung Galaxy S24")
    if transcripts:
        print(f"Found {len(transcripts)} transcripts.")
        print("First transcript snippet:")
        print(transcripts[0][:500] + "...")
    else:
        print("No transcripts found.")
