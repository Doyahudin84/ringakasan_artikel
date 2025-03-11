import requests
import streamlit as st
import validators
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Function to extract URLs from a webpage
def extract_urls(webpage_url):
    try:
        response = requests.get(webpage_url)
        response.raise_for_status()  # Memastikan response tidak error (status code bukan 200)
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred while fetching the webpage: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = []

    for a in soup.find_all('a', href=True):
        href = a['href']
        
        # Mengabaikan URL mailto atau URL fragment (yang hanya '#')
        if href.startswith('mailto:') or href.startswith('#'):
            continue
        
        # Menambahkan skema dan domain jika URL relatif
        if not href.startswith('http') and not href.startswith('www'):
            href = urljoin(webpage_url, href)

        # Memastikan URL valid
        if validators.url(href):
            urls.append(href)
    
    return urls

# Function to summarize an article using Gemini API
def summarize_article(article_url, gemini_api_key):
    try:
        response = requests.get(article_url)
        response.raise_for_status()
        article_text = response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching article at {article_url}: {e}")
        return None

    # Menggunakan API Gemini untuk menghasilkan konten
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_api_key}"
    headers = {
        'Content-Type': 'application/json',
    }
    
    data = {
        "contents": [{
            "parts": [{"text": article_text}]
        }]
    }

    try:
        # Kirim permintaan POST ke API Gemini
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Memastikan tidak ada error pada permintaan
        result = response.json()
        summary = result.get('content', 'No summary generated.')
        return summary
    except requests.exceptions.RequestException as e:
        st.error(f"Error during summary generation: {e}")
        return None

# Streamlit app
st.title('Ringkasan artikel dengan menggunakan Gemini AI by Doyahudin')

webpage_url = st.text_input('Enter the webpage URL:')
gemini_api_key = st.text_input('Enter your Gemini API key:', type='password')

# Validasi URL
if webpage_url and not validators.url(webpage_url):
    st.error("The entered URL is not valid.")

if st.button(Ringkasan'):
    if webpage_url and gemini_api_key:
        urls = extract_urls(webpage_url)
        if urls:  # Jika ada URL yang diekstrak
            for url in urls:
                summary = summarize_article(url, gemini_api_key)
                if summary:
                    st.write(f"Summary of {url}:\n{summary}\n")
                else:
                    st.error(f"Failed to summarize article at {url}")
        else:
            st.error('No valid URLs found in the provided webpage.')
    else:
        st.error('Please enter both the webpage URL and Gemini API key.')
