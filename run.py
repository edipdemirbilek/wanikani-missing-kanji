import requests
from bs4 import BeautifulSoup
import sys
import io
import time

# Set standard output to use UTF-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Function to extract text from a table row
def extract_value(soup, label):
    row = soup.find('td', text=label)
    if row:
        return row.find_next_sibling('td').text.strip()
    return None


def get_kanji_info(kanji):
    # URL for the kanji search on jpdb.io
    url = f"https://jpdb.io/kanji/{kanji}"

    print(url)
    
    # Send a GET request to the website
    response = requests.get(url)
    
    # Ensure the response is decoded as UTF-8
    response.encoding = 'utf-8'
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data for kanji: {kanji}")
        return None
    
    # Parse the HTML content using BeautifulSoup with UTF-8 encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the keyword
    keyword = ''

    # Find the <h6> tag with the text "Keyword"
    keyword_label = soup.find('h6', class_='subsection-label', text='Keyword')

    # If the keyword label is found, find the corresponding value
    if keyword_label:
        value_div = keyword_label.find_next_sibling('div', class_='subsection')
        if value_div:
            keyword = value_div.text.strip()
        else:
            print("Value not found for 'Keyword'.")
    else:
        print("Keyword label not found.")

    # Retrieve values for Frequency, Type, Kanken, and Heisig
    frequency = extract_value(soup, "Frequency")
 
    # Retrieve readings
    readings = []
    readings_td = soup.find('td', text="Readings").find_next_sibling('td') if soup.find('td', text="Readings") else None
    if readings_td:
        for a_tag in readings_td.find_all('a'):
            readings.append(a_tag.text.strip())

    # Combine readings into a comma-separated string
    readings_str = ", ".join(readings)
    
    # Find the "Composed of" section
    composed_of_section = soup.find('div', class_='subsection-composed-of-kanji')

    # Initialize a list to store the composed of data
    composed_of_data = []

    try:
        # Check if the "Composed of" section exists
        if composed_of_section:
            # Find the <div class="subsection"> inside the "Composed of" section
            subsection = composed_of_section.find('div', class_='subsection')
            
            # Iterate over the top-level <div> elements inside the subsection
            for item in subsection.find_all('div', recursive=False):
                # Extract the radical
                radical = item.find('a', class_='plain').text.strip()
                
                # Extract the description
                description = item.find('div', class_='description').text.strip()
                
                # Append the radical and description to the list
                composed_of_data.append(f"{radical}: {description}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Join the data into a single string with semicolon separators
    composed_of_string = ", ".join(composed_of_data)

    
    # Return the extracted information
    return {
        "Kanji": kanji,
        "Keyword": keyword,
        "Frequency": frequency,
        "Readings": readings_str,
        "Composed Of": composed_of_string
    }

def read_kanji_from_file(file_path):
    # Read kanji from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        kanji_list = file.read().split()  # Split lines into a list
    return kanji_list

def main():
    # Path to the kanji.txt file
    file_path = 'kanji.txt'
    
    # Read kanji from the file
    kanji_list = read_kanji_from_file(file_path)
    
    # Open a text file to write the output
    with open('kanji_info.txt', 'w', encoding='utf-8') as output_file:
        # Retrieve and print information for each kanji
        for kanji in kanji_list:
            print(f"Fetching information for kanji: {kanji}")
            info = get_kanji_info(kanji.strip())
            if info:
                # Write the info dictionary to the file
                for key, value in info.items():
                    output_file.write(f"{key}: {value}\n")
            else:
                output_file.write(f"No information found for kanji: {kanji}\n")
            output_file.write("-" * 40 + "\n")  # Separator for readability

            # to not get API rate limits
            time.sleep(5)

# Run the script
if __name__ == "__main__":
    main()