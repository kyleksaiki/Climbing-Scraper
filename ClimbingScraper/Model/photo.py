import os

import requests


class Photo:
    # A model representing a downloadable image for a climb
    def __init__(self, link, climb_name, folder):
        # Construct a filename by combining the climb name with the URL's basename (strip query params)
        self.filename = climb_name + link.split("/")[-1].split("?")[0]
        # Store the image URL for later download
        self.link = link
        # Trigger immediate download into the specified folder
        self.download_image(folder)

    # Download the image from self.link into the given folder
    def download_image(self, folder):
        # Determine this script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build target folder path relative to project: ../View/images/<folder>
        target_folder = os.path.normpath(
            os.path.join(current_dir, '..', 'View', 'images', folder)
        )

        # Ensure the target directory exists
        os.makedirs(target_folder, exist_ok=True)

        # Full filesystem path for saving the image
        save_path = os.path.join(target_folder, self.filename)

        try:
            # Stream the HTTP GET to avoid loading entire content at once
            response = requests.get(self.link, stream=True)
            # Raise on HTTP error status codes (4xx/5xx)
            response.raise_for_status()
            # Write the content to file in chunks
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            # Return the local path if successful
            return save_path
        except requests.exceptions.RequestException as e:
            # Print an error message if download fails
            print(f"❌ Failed to download image: {e}")
            return None
