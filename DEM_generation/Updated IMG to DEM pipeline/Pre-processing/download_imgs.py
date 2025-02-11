import os
import requests
import pvl
import xml.etree.ElementTree as ET

config = parse_yaml('config.yaml')


url_file_path = 'img_urls.txt' 


download_directory = img_prefix  


if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Read URLs from file
with open(url_file_path, 'r') as file:
    urls = file.readlines()

for url in urls:
    url = url.strip()
    if url:
        try:
            # Download the file
            response = requests.get(url)
            response.raise_for_status()

            # Extract the file name from the URL
            file_name = os.path.basename(url)

            # Create the full path for saving the file
            file_path = os.path.join(download_directory, file_name)

            # Save the raw data
            with open(file_path, 'wb') as f:
                f.write(response.content)

            # Handle different file types
            if file_name.lower().endswith('.IMG'):
                # Parse the PDS label for .img files
                label = pvl.load(file_path)
                print(f'Downloaded and parsed PDS label for: {file_name}')
            elif file_name.lower().endswith('.xml'):
                # Parse XML for .xml files
                tree = ET.parse(file_path)
                root = tree.getroot()
                print(f'Downloaded and parsed XML for: {file_name}')
            else:
                print(f'Downloaded file: {file_name} (unknown format)')

        except requests.exceptions.RequestException as e:
            print(f'Failed to download {url}: {e}')
        except pvl.decoder.ParseError as e:
            print(f'Failed to parse PDS label for {file_name}: {e}')
        except ET.ParseError as e:
            print(f'Failed to parse XML for {file_name}: {e}')
