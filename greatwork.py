""" 
Better Search Space, Creating an interconnecting web of topics that maps out the
relationships and evolution of human knowledge, Something like how innovation works
by Matt Ridley for the whole human knowledge with automation 

"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Function to fetch content from an encyclopedia page
def fetch_encyclopedia_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch {url}")
        return None

# Function to extract topics from an encyclopedia page
def extract_topics_from_html(html_content, base_url):
    topics = []
    soup = BeautifulSoup(html_content, 'html.parser')
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/science-and-technology/') and ':' not in href:
            # Extract the topic name from the link text
            topic_name = link.get_text().strip()
            full_url = urljoin(base_url, href)
            topics.append((topic_name, full_url))
    return topics

# Main function to explore related topics starting from a given URL
def explore_related_topics(start_url, max_depth=4, output_file='explored_topics.txt'):
    explored_topics = set()
    topics_to_explore = [(start_url, 0)]  # (url, depth)

    with open(output_file, 'w') as f:
        while topics_to_explore:
            current_url, depth = topics_to_explore.pop(0)
            
            if current_url in explored_topics:
                continue
            
            explored_topics.add(current_url)
            print(f"Exploring {current_url} (Depth: {depth})")
            f.write(f"URL: {current_url}\n")

            if depth < max_depth:
                html_content = fetch_encyclopedia_page(current_url)
                if html_content:
                    related_topics = extract_topics_from_html(html_content, current_url)
                    for topic_name, topic_url in related_topics:
                        f.write(f"  Topic: {topic_name}\n")
                        topics_to_explore.append((topic_url, depth + 1))
    
    print(f"Exploration complete. Explored topics saved to {output_file}")

# Example usage:
if __name__ == "__main__":
    start_url = "https://www.encyclopedia.com/science-and-technology/computers-and-electrical-engineering/computers-and-computing?page=0"  # Start with this encyclopedia page
    max_depth = 2  # Maximum depth of exploration
    output_file = "explored_topics.txt"  # Output file to save explored topics

    explore_related_topics(start_url, max_depth, output_file)
