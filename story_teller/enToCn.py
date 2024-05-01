import requests
import random
import json
from hashlib import md5

# Baidu Translate API credentials
appid = '20240428002037926'
appkey = 'ofWpAAdmWPiFLA0cg5DP'

# Translation parameters
from_lang = 'en'
to_lang = 'zh'

# Baidu Translate API endpoint and path
endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path
# Function to generate MD5 hash for the signature
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()

def translate_text(query):
    # Generate a random salt and calculate the signature
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build the request payload and headers
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'appid': appid,
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'salt': salt,
        'sign': sign
    }

    # Send the POST request to Baidu Translate API
    response = requests.post(url, params=payload, headers=headers)

    # Get the JSON response
    result = response.json()

    # Extract and print the translated text (dst value)
    if "trans_result" in result:
        # Extract the translated text
        translated_text = result["trans_result"][0]["dst"]
        # Print the translated text
        return translated_text
    else:
        # Handle errors, if any
        print("Error in translation:", result.get("error_msg", "Unknown error"))

# # Test the function with a sample text
# query = "Hello, how are you?"
# translated_text = translate_text(query)
# print("Translated text:", translated_text)
