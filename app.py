from flask import Flask, render_template_string, request
import requests
from bs4 import BeautifulSoup
import urllib.parse

app = Flask(__name__)

# ইউজার এজেন্ট (এটি ব্রাউজার হিসেবে ইন্টারনেটে রিকোয়েস্ট পাঠাতে সাহায্য করে)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36"
}

def fetch_live_results(query):
    search_results = []
    try:
        # আমরা গুগল থেকে লাইভ ডাটা স্ক্র্যাপ করে আমাদের BanglaNet-এ দেখাবো
        # শুধু বাংলা রেজাল্ট ফিল্টার করার জন্য 'lr=lang_bn' ব্যবহার করা হয়েছে
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded_query}&lr=lang_bn&hl=bn"
        
        response = requests.get(url, headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # গুগলের সার্চ রেজাল্টের প্রধান বক্সগুলো খুঁজে বের করা
            search_divs = soup.find_all("div", class_="g")
            
            for div in search_divs:
                title_tag = div.find("h3")
                link_tag = div.find("a")
                snippet_tag = div.find("div", class_="VwiC3b") # ডেসক্রিপশন টেক্সট
                
                if title_tag and link_tag:
                    title = title_tag.get_text()
                    link = link_tag["href"]
                    snippet = snippet_tag.get_text() if snippet_tag else "কোনো বিবরণ পাওয়া যায়নি।"
                    
                    search_results.append({
                        "title": title,
                        "link": link,
                        "text": snippet
                    })
                    
    except Exception as e:
        print(f"Error fetching data: {e}")
        
    return search_results

# HTML ডিজাইন পরিবর্তন করা হয়েছে আসল লিংক দেখানোর জন্য
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BanglaNet Search</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }
        .header { text-align: center; padding: 40px 10px 20px 10px; background: white; border-bottom: 1px solid #e0e0e0; }
        .logo { font-size: 45px; font-weight: bold; color: #1a73e8; margin-bottom: 15px; }
        .logo span { color: #ea4335; }
        input[type="text"] { width: 80%; max-width: 500px; padding: 12px 20px; font-size: 16px; border: 1px solid #ccc; border-radius: 24px; outline: none; }
        button { padding: 12px 25px; font-size: 16px; background-color: #1a73e8; color: white; border: none; border-radius: 24px; cursor: pointer; margin-top: 10px; }
        .results { width: 90%; max-width: 700px; margin: 20px auto; }
        .result-item { background: white; padding: 15px; margin-bottom: 15px; border-radius: 8px; border: 1px solid #e0e0e0; }
        .result-title { font-size: 18px; color: #1a0dab; font-weight: bold; text-decoration: none; }
        .result-title:hover { text-decoration: underline; }
        .result-link { font-size: 12px; color: #006621; margin-bottom: 5px; word-break: break-all; }
        .result-text { font-size: 14px; color: #4d5156; margin-top: 5px; }
    </style>
</head>
<body>

    <div class="header">
        <div class="logo">Bangla<span>Net</span></div>
        <form method="POST">
            <input type="text" name="query" placeholder="ইন্টারনেট থেকে খুঁজুন..." value="{{ query }}" required><br>
            <button type="submit">BanglaNet লাইভ সার্চ</button>
        </form>
    </div>

    <div class="results">
        {% if results %}
            <p style="color: #70757a;">আপনার জন্য লাইভ ফলাফল নিচে দেওয়া হলো:</p>
            {% for res in results %}
                <div class="result-item">
                    <div class="result-link">{{ res.link }}</div>
                    <a class="result-title" href="{{ res.link }}" target="_blank">{{ res.title }}</a>
                    <div class="result-text">{{ res.text }}</div>
                </div>
            {% endfor %}
        {% elif query %}
            <p>দুঃখিত, ইন্টারনেট থেকে কোনো তথ্য লোড করা যায়নি। আবার চেষ্টা করুন।</p>
        {% endif %}
    </div>

</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    query = ""
    search_results = []
    
    if request.method == 'POST':
        query = request.form['query']
        # লাইভ ইন্টারনেট থেকে ডাটা আনা হচ্ছে
        search_results = fetch_live_results(query)
                
    return render_template_string(HTML_TEMPLATE, query=query, results=search_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
