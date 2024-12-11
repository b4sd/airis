import requests
import re

url = "https://ebookvie.com/wp-admin/admin-ajax.php"

def make_request(product_id):
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryhPG3Vig9xTsgJCdI",
        "priority": "u=1, i",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "cookie": "wordpress_sec_395a7ab6c36620345b2b32e5ac989385=duyanhle%7C1735110714%7CHA2or4dIipPxjmO1DuyRKsYuJcHglmaLkBelRCq6emk%7C00cec7f2fb4e39b737157aa7e561a0fe66b978bbabd5ae42463f87be61b5c428; _ga=GA1.1.102920724.1733476554; wordpress_test_cookie=WP%20Cookie%20check; _lscache_vary=3d629a7682ae24b8fd31f37f77fc2208; wordpress_logged_in_395a7ab6c36620345b2b32e5ac989385=duyanhle%7C1735110714%7CHA2or4dIipPxjmO1DuyRKsYuJcHglmaLkBelRCq6emk%7C50940e90fe0b3ae17a9e45f94b41dbaea84b684361258484603153e6183de82f; _ga_9DWTK7W9TB=GS1.1.1733900864.3.1.1733906571.53.0.1448828886",
        "Referer": "https://ebookvie.com/ebook/song-o-day-song/",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }

    # Correctly formatted body with the boundary
    body = f'''------WebKitFormBoundaryhPG3Vig9xTsgJCdI
Content-Disposition: form-data; name="action"

get_download_link
------WebKitFormBoundaryhPG3Vig9xTsgJCdI
Content-Disposition: form-data; name="product_id"

{product_id}
------WebKitFormBoundaryhPG3Vig9xTsgJCdI
Content-Disposition: form-data; name="field_name"

link1
------WebKitFormBoundaryhPG3Vig9xTsgJCdI--'''

    # Send the POST request
    response = requests.post(url, headers=headers, data=body)

    return response

def download_file(download_url, filename):
    # Send a GET request to the download URL
    file_response = requests.get(download_url)

    # Check if the request was successful
    if file_response.status_code == 200:
        # Save the file to the current directory
        with open(filename, 'wb') as f:
            f.write(file_response.content)
        print(f"File downloaded successfully: {filename}")
    else:
        print(f"Failed to download the file from {download_url}")

# Loop over product_ids from 33000 to 33054 and make the request for each
for product_id in range(33000, 33055):
    response = make_request(product_id)

    # Use regex to extract the download URL
    match = re.search(r'https://drive\.google\.com/uc\?id=[^"]+', response.text)
    if match:
        download_url = match.group(0)
        filename = f"file_{product_id}.pdf"  # Adjust the file name as needed
        download_file(download_url, filename)
    else:
        print(f"No valid download link found for product_id {product_id}")
