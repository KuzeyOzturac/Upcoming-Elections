import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import re


def scrape_elections(url):
    # Fetch the content from the URL
    headers = {'User-Agent': 'Mozilla/5.0'}  # To prevent potential blocking
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the current date
    current_date = datetime.now()

    # Find the content division
    content = soup.find('div', {'class': 'mw-parser-output'})
    if not content:
        print("Couldn't find the main content division.")
        return []

    # Initialize variables
    elections = []
    region = ''
    country = ''

    # Regular expressions for cleaning and date extraction
    footnote_pattern = re.compile(r'\[\w+\]')
    country_year_pattern = re.compile(r'^([A-Za-z\s]+)(\d{4})')
    date_patterns = [
        r'\b\d{1,2}\s+\w+\s+\d{4}\b',  # 7 September 2024
        r'\b\d{1,2}\s+\w+\b',  # 7 September
        r'\b\w+\s+\d{1,2},\s*\d{4}\b',  # September 7, 2024
        r'\b\w+\s+\d{1,2}\b',  # September 7
        r'\b\w+\s+\d{4}\b',  # September 2024
        r'\b\d{1,2}\s+\w+,\s*\d{4}\b',  # 7 September, 2024
    ]

    date_regex = re.compile('|'.join(date_patterns), re.IGNORECASE)

    # Find all headings and lists in the content
    for element in content.find_all(['h2', 'h3', 'ul']):
        if element.name == 'h2':
            # Update the region
            region = element.get_text(strip=True).replace('[edit]', '')
        elif element.name == 'h3':
            # Update the country
            country = element.get_text(strip=True).replace('[edit]', '')
        elif element.name == 'ul':
            # Iterate over each list item in the unordered list
            for li in element.find_all('li', recursive=False):
                text = li.get_text(separator=' ', strip=True)
                # Remove footnotes like [a], [1], etc.
                text = footnote_pattern.sub('', text)
                # Remove concatenated country names and years at the start
                text = country_year_pattern.sub('', text).strip()
                # Extract the election name up to the first comma
                election_name = text.split(',')[0].strip()
                # Extract the link to the election page
                link_tag = li.find('a', href=True)
                if link_tag:
                    link_href = link_tag['href']
                    link = 'https://en.wikipedia.org' + link_href
                    # Only include links that point to election pages
                    if 'election' not in link_href.lower():
                        continue  # Skip this entry if it's not an election page
                else:
                    continue  # Skip if there's no link

                # Attempt to parse all dates from the text
                date_strings = date_regex.findall(text)
                parsed = False
                for date_str in date_strings:
                    # Clean up the date string
                    date_str = date_str.strip(',').strip()
                    # Append the year if missing
                    if re.match(r'^\d{1,2}\s+\w+$|^\w+\s+\d{1,2}$', date_str):
                        # Use the current year
                        date_str += f' {current_date.year}'
                    try:
                        # Parse the date
                        election_date = parser.parse(date_str, fuzzy=True, dayfirst=True)
                        # Normalize dates to exclude time
                        current_date_normalized = current_date.date()
                        election_date_normalized = election_date.date()
                        # Check if the election date is after the current date and within the same year
                        if current_date_normalized < election_date_normalized and election_date.year == current_date.year:
                            elections.append({
                                'date': election_date.strftime('%d %B %Y'),
                                'election': election_name,
                                'country': country,
                                'region': region,
                                'link': link,
                                'sort_date': election_date_normalized  # Added for sorting
                            })
                            parsed = True
                            break  # Stop after finding the first valid future date
                    except (ValueError, OverflowError) as e:
                        print(f"Date parsing error for '{text}': {e}")
                        continue
                if not parsed:
                    # Handle cases where no valid date was found
                    pass

    # Remove duplicates
    elections_unique = {election['election']: election for election in elections}.values()
    elections_list = list(elections_unique)

    # Sort the list by 'sort_date'
    elections_list.sort(key=lambda x: x['sort_date'])

    # Print the upcoming elections before the end of this year
    if elections_list:
        print("Upcoming Elections Before the End of This Year:\n")
        for election in elections_list:
            print(f"Date: {election['date']}")
            print(f"Election: {election['election']}")
            #print(f"Country: {election['country']}")
            print(f"Region: {election['region']}")
            print(f"Link: {election['link']}\n")
    else:
        print("No upcoming elections found before the end of this year.")

    return elections_list
