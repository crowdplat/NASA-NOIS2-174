import os
import requests

# Specify the path to the text file containing the image URLs
url_file_path = '/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Viktoriia_practice/imgs_sample/img_urls.txt'  # Change this to your text file path

# Specify the directory where images will be saved
download_directory = '/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Viktoriia_practice/imgs_sample'  # Change this to your desired directory

# Create the download directory if it doesn't exist
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Read the URLs from the text file
with open(url_file_path, 'r') as file:
    urls = file.readlines()

# Download each image
for url in urls:
    url = url.strip()  # Remove any leading/trailing whitespace
    if url:  # Check if the URL is not empty
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses

            # Extract the image name from the URL
            image_name = os.path.basename(url)

            # Create the full path for saving the image
            image_path = os.path.join(download_directory, image_name)

            # Write the image content to a file
            with open(image_path, 'wb') as image_file:
                image_file.write(response.content)

            print(f'Downloaded: {image_name}')

        except requests.exceptions.RequestException as e:
            print(f'Failed to download {url}: {e}')