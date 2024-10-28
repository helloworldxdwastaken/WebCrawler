import requests
from bs4 import BeautifulSoup
import os

def fetch_and_parse(url):
    """Fetch content from a URL and parse it with BeautifulSoup, handling HTTP errors."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.HTTPError as e:
        print(f"Failed to fetch {url}: {e}")
        return None  # Return None if there's an error fetching the page

def extract_text(soup):
    """Extract main content from the parsed HTML."""
    content = ""
    for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'pre', 'code']):
        if header.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
            content += f"\n# {'#' * (int(header.name[1]) - 1)} {header.text.strip()}\n\n"
        elif header.name == 'p':
            content += f"{header.text.strip()}\n\n"
        elif header.name in ['pre', 'code']:
            content += f"```\n{header.text.strip()}\n```\n\n"
    return content

def save_to_md(file_name, content):
    """Save extracted content to a Markdown file."""
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)

def crawl_and_save(base_url, start_page, output_file="Documentation.md"):
    """Crawl starting from the given page and save content to a Markdown file."""
    visited_urls = set()
    content = ""

    def crawl(url):
        if url in visited_urls or url is None:
            return
        visited_urls.add(url)

        soup = fetch_and_parse(url)
        if soup is None:
            return  # Skip this page if it couldn't be fetched

        content_chunk = extract_text(soup)
        nonlocal content
        content += content_chunk

        # Find and follow links
        for link in soup.find_all('a', href=True):
            full_url = link['href']
            if full_url.startswith('/'):
                full_url = base_url + full_url
            if base_url in full_url and full_url not in visited_urls:
                crawl(full_url)

    crawl(base_url + start_page)
    save_to_md(output_file, content)
    print(f"Documentation saved to {output_file}")

# Update these with ur website:
base_url = "https://docs.openwebui.com"  # Replace with the base URL of the site
start_page = "/getting-started"          # Starting page relative to the base URL
output_file = "Open_WebUI_Documentation.md"

crawl_and_save(base_url, start_page, output_file)
