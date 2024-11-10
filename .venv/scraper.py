import requests
import logging
import re
from bs4 import BeautifulSoup

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_keywords(query):
    # Removes common words from queries
    stopwords = {'what', 'is', 'a', 'an', 'and', 'the', 'to', 'of', 'in', 'who', 'are', 'was'}
    words = re.findall(r'\w+', query.lower())
    keywords = [word for word in words if word not in stopwords]
    return ' '.join(keywords)


def get_wiki_extract_via_web_scraping(page_url):
    try:
        response = requests.get(page_url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the first paragraph on the page
            paragraph = soup.find('p')
            if paragraph:
                return paragraph.get_text()
            else:
                logger.error("No paragraph found on the page.")
                return None
        else:
            logger.error(f"HTTP error while retrieving the page: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Exception during web scraping: {e}")
        return None


def get_wiki_summary_and_link(keyword):
    try:
        # Base URL of the Warhammer 40k Fandom Wiki
        base_url = "https://warhammer40k.fandom.com/api.php"

        # Search the Fandom Wiki with the keyword
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": keyword,
            "format": "json"
        }
        response = requests.get(base_url, params=search_params)
        logger.info(f"Search URL: {response.url}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"JSON response: {data}")

            search_results = data.get("query", {}).get("search", [])
            if search_results:
                # Get the title of the first search result
                first_result = search_results[0]
                first_result_title = first_result["title"]

                logger.info(f"First result title: {first_result_title}")

                # Construct the link to the page
                page_url = f"https://warhammer40k.fandom.com/wiki/{first_result_title.replace(' ', '_')}"

                # Call the web scraping function to get the summary
                summary = get_wiki_extract_via_web_scraping(page_url)

                if summary:
                    return summary, page_url
                else:
                    logger.error("Summary not found via web scraping.")
                    return None, page_url
            else:
                logger.info("No results found for the search.")
                return None, None
        else:
            logger.error(f"HTTP error during the search: {response.status_code}")
            return None, None
    except Exception as e:
        logger.error(f"Exception during the search: {e}")
        return None, None


if __name__ == "__main__":
    # Example usage
    query = "khorne"
    keywords = extract_keywords(query)
    summary, link = get_wiki_summary_and_link(keywords)
    if summary:
        print(f"Summary: {summary}\nLink: {link}")
    else:
        print("I couldn't find information on this topic.")
