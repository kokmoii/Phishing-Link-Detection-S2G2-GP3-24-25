from flask import Flask, request, render_template_string
import requests
from bs4 import BeautifulSoup
import tldextract
from urllib.parse import urlparse
import pickle

app = Flask(__name__)

# HTML template for the web page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Link Phishing Detector</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #000000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            color: #333;
        }

        .container {
            background-color: #ffffff;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 500px;
            text-align: center;
        }

        h1 {
            margin-bottom: 20px;
            font-size: 24px;
            color: #4CAF50;
        }

        form {
            margin-bottom: 30px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: bold;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        input[type="text"]:focus {
            border-color: #4CAF50;
            outline: none;
        }

        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #45a049;
        }

        h2 {
            margin-top: 20px;
            font-size: 18px;
            color: #555;
        }

        .result {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-top: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Website Link Phishing Detector By Group S2G2</h1>
        <form method="POST">
            <label for="url">Enter URL:</label>
            <input type="text" id="url" name="url" required>
            <button type="submit">Submit</button>
        </form>

        {% if url_length is not none %}
            <div class="result">
                <h2>Length of the URL: {{ url_length }}</h2>
            </div>
        {% endif %}
        {% if indexed is not none %}
            <div class="result">
                <h2>Indexed by Google: {{ indexed }}</h2>
            </div>
        {% endif %}
        {% if hyperlink_count is not none %}
            <div class="result">
                <h2>Number of Hyperlinks: {{ hyperlink_count }}</h2>
            </div>
        {% endif %}
        {% if subdomain_count is not none %}
            <div class="result">
                <h2>Number of Subdomains: {{ subdomain_count }}</h2>
            </div>
        {% endif %}
        {% if word_count is not none %}
            <div class="result">
                <h2>Number of Words in Raw Text: {{ word_count }}</h2>
            </div>
        {% endif %}
        {% if external_hyperlink_ratio is not none %}
            <div class="result">
                <h2>External Hyperlink Ratio: {{ external_hyperlink_ratio }}</h2>
            </div>
        {% endif %}

        <h2>Prediction Tool</h2>
        {% if prediction_result is not none %}
            <div class="result">
                <h2>Prediction: {{ prediction_result }}</h2>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# Replace with your actual API key and Search Engine ID
API_KEY = 'AIzaSyA3T1zGP7djw4mZYUuuF0vFGDjYs5mJSC0'
SEARCH_ENGINE_ID = 'b12ab8878635f40f2'

# Load the model
with open('tuned_model.pkl', 'rb') as file:
    model = pickle.load(file)

def check_google_index(url):
    search_url = f"https://www.googleapis.com/customsearch/v1?q=site:{url}&key={API_KEY}&cx={SEARCH_ENGINE_ID}"
    
    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data:
                return "Yes"
            else:
                return "No"
        else:
            return "Error fetching data: " + str(response.status_code)
    except requests.exceptions.RequestException as e:
        return "Error fetching data: " + str(e)

def count_hyperlinks(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            hyperlinks = soup.find_all('a')
            return len(hyperlinks)
        else:
            return "Error fetching URL: " + str(response.status_code)
    except requests.exceptions.RequestException as e:
        return "Error fetching URL: " + str(e)

def count_subdomains(url):
    extracted = tldextract.extract(url)
    subdomain_parts = extracted.subdomain.split('.')
    return len(subdomain_parts) if extracted.subdomain else 0

def count_words_raw(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()  # Extract raw text
            words = text.split()  # Split text
            return len(words)  # Count the number of words
        else:
            return "Error fetching URL: " + str(response.status_code)
    except requests.exceptions.RequestException as e:
        return "Error fetching URL: " + str(e)

def calculate_external_hyperlink_ratio(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            hyperlinks = soup.find_all('a', href=True)
            total_hyperlinks = len(hyperlinks)
            external_hyperlinks = 0
            main_domain = urlparse(url).netloc

            for link in hyperlinks:
                href = link['href']
                if urlparse(href).netloc and urlparse(href).netloc != main_domain:
                    external_hyperlinks += 1

            ratio = external_hyperlinks / total_hyperlinks if total_hyperlinks > 0 else 0
            return ratio
        else:
            return "Error fetching URL: " + str(response.status_code)
    except requests.exceptions.RequestException as e:
        return "Error fetching URL: " + str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    url_length = None
    indexed = None
    hyperlink_count = None
    subdomain_count = None
    word_count = None
    external_hyperlink_ratio = None
    prediction_result = None

    if request.method == 'POST':
        url = request.form['url']
        url_length = len(url)
        indexed = check_google_index(url)
        hyperlink_count = count_hyperlinks(url)
        subdomain_count = count_subdomains(url)
        word_count = count_words_raw(url)
        external_hyperlink_ratio = calculate_external_hyperlink_ratio(url)

        # Convert "Yes"/"No" for Google Index into 1/0
        indexed_value = 0 if indexed == "Yes" else 1

        # Generate prediction if all features are available
        if all(x is not None for x in [url_length, indexed_value, hyperlink_count, subdomain_count, word_count, external_hyperlink_ratio]):
            try:
                # Create the feature vector
                features = [url_length, indexed_value, hyperlink_count, subdomain_count, word_count, external_hyperlink_ratio]
                prediction_result = model.predict([features])[0]
            except Exception as e:
                prediction_result = f"Error in prediction: {str(e)}"

    return render_template_string(HTML_TEMPLATE, 
                                  url_length=url_length, 
                                  indexed=indexed, 
                                  hyperlink_count=hyperlink_count, 
                                  subdomain_count=subdomain_count, 
                                  word_count=word_count, 
                                  external_hyperlink_ratio=external_hyperlink_ratio, 
                                  prediction_result=prediction_result)



if __name__ == '__main__':
    app.run(debug=True)
