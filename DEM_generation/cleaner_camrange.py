import os

# Specify the directory containing the files
directory_path = '/home/ec2-user/SageMaker/Artemis_III_Sites_Alex_Coordinates/Connecting_Ridge/Viktoriia_practice/cubs_coord'

# Iterate through all files in the specified directory
for filename in os.listdir(directory_path):
    # Check if the file ends with the specified extensions
    if filename.endswith('.cal.camrange.cub.txt') or filename.endswith('.cal.echo.camrange.cub.txt'):
        # Construct full file path
        file_path = os.path.join(directory_path, filename)
        try:
            # Delete the file
            os.remove(file_path)
            print(f'Deleted: {file_path}')
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')

print('Deletion process completed.')