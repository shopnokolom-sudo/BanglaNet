from flask import Flask, render_template_string, request
import requests
import urllib.parse

app = Flask(__name__)

def fetch_live_results(query):
    search_results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # ১. আপনার ওয়েবসাইটের অগ্রাধিকার ফিল্টারিং (সবার উপরে আসার জন্য)
    try:
        # পাবলিক এবং ফ্রি SearXNG ইন্সট্যান্স ব্যবহার করে আপনার সাইটের কন্টেন্ট খোঁজা
        url_my = f"https://search.ononoki.org/search?q={urllib.parse.quote(query)}+site:shopnokolom.kesug.com&format=json"
        res_my = requests.get(url_my, headers=headers, timeout=5)
        if res_my.status_code == 200:
            raw_data = res_my.json()
            for item in raw_data.get("results", [])[:3]:
                search_results.append({
                    "title": item.get("title", "স্বপ্ন-কলম সাহিত্য"),
                    "link": item.get("url", "https://shopnokolom.kesug.com"),
                    "text": item.get("content", "স্বপ্ন-কলম সাহিত্য পরিবার থেকে প্রকাশিত বিস্তারিত লেখা।")
                })
    except Exception as e:
        print(f"Priority search error: {e}")

    # ২. সাধারণ লাইভ ইন্টারনেট সার্চ (টাইটেল, লিংক এবং সুন্দর বিবরণসহ)
    try:
        url_gen = f"https://search.ononoki.org/search?q={urllib.parse.quote(query)}&format=json&language=bn"
        res_gen = requests.get(url_gen, headers=headers, timeout=6)
        
        if res_gen.status_code == 200:
            raw_data = res_gen.json()
            for item in raw_data.get("results", [])[:12]: # সেরা ১২টি রেজাল্ট দেখাবে
                title = item.get("title", "")
                link = item.get("url", "")
                snippet = item.get("content", "") # এটি সুন্দর বিবরণ/স্নিপেট এনে দেবে
                
                if not snippet:
                    snippet = "বিস্তারিত তথ্য দেখতে এবং পড়তে লিংকে ক্লিক করুন।"
                
                if title and link:
                    # ডুপ্লিকেট লিংক বাদ দেওয়া
                    if not any(res['link'] == link for res in search_results):
                        search_results.append({
                            "title": title,
                            "link": link,
                            "text": snippet
                        })
    except Exception as e:
        print(f"General search error: {e}")
        
    return search_results

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if query %}{{ query }} - BanglaNet অনুসন্ধান{% else %}BanglaNet{% endif %}</title>
    <style>
        body { font-family: Roboto, arial, sans-serif; margin: 0; padding: 0; background-color: #fff; color: #202124; display: flex; flex-direction: column; min-height: 100vh; }
        .home-wrapper { display: flex; flex-direction: column; height: calc(100vh - 60px); align-items: center; justify-content: center; padding: 20px; box-sizing: border-box; }
        .home-logo { font-size: 80px; font-weight: bold; letter-spacing: -2px; margin-bottom: 25px; font-family: Arial, sans-serif; }
        .home-logo .g1 { color: #006a4e; }
        .home-logo .r1 { color: #f42a41; }
        .home-search-form { width: 100%; max-width: 584px; text-align: center; }
        .search-box-wrapper { display: flex; align-items: center; background: #fff; border: 1px solid #dfe1e5; box-shadow: none; border-radius: 24px; width: 100%; height: 46px; box-sizing: border-box; padding: 0 15px; transition: box-shadow 0.1s; }
        .search-box-wrapper:hover, .search-box-wrapper:focus-within { box-shadow: 0 1px 6px rgba(32,33,36,0.28); border-color: rgba(223,225,229,0); }
        .search-box-wrapper input { flex: 1; height: 100%; border: none; outline: none; font-size: 16px; color: #000; background: transparent; }
        .home-btn-container { margin-top: 25px; }
        .g-btn { background-color: #f8f9fa; border: 1px solid #f8f9fa; border-radius: 4px; color: #3c4043; font-size: 14px; margin: 11px 4px; padding: 0 16px; height: 36px; min-width: 54px; text-align: center; cursor: pointer; font-weight: 500; }
        .g-btn:hover { border: 1px solid #dadce0; color: #202124; box-shadow: 0 1px 1px rgba(0,0,0,0.1); }
        .home-highlights { margin-top: 28px; font-size: 14px; color: #4d5156; text-align: center; line-height: 24px; }
        .home-highlights a { color: #1a0dab; text-decoration: none; margin-left: 10px; display: inline-block; }
        .home-highlights a:hover { text-decoration: underline; }
        .search-header { display: flex; align-items: center; padding: 20px 40px; border-bottom: 1px solid #ebebeb; background: #fff; }
        .search-header .logo-small { font-size: 30px; font-weight: bold; letter-spacing: -1px; text-decoration: none; margin-right: 40px; font-family: Arial, sans-serif; }
        .search-header .logo-small .g1 { color: #006a4e; }
        .search-header .logo-small .r1 { color: #f42a41; }
        .search-header form { flex: 1; max-width: 692px; display: flex; gap: 10px; }
        .results-container { padding: 20px 40px 100px 150px; max-width: 652px; box-sizing: border-box; }
        @media (max-width: 800px) {
            .search-header { padding: 15px; flex-direction: column; align-items: flex-start; gap: 15px; }
            .search-header .logo-small { margin-right: 0; font-size: 26px; }
            .results-container { padding: 15px; }
        }
        .result-stats { font-size: 14px; color: #70757a; margin-bottom: 25px; }
        .chrome-result-item { margin-bottom: 30px; font-size: 14px; line-height: 1.58; word-wrap: break-word; }
        .chrome-result-item .site-url { font-size: 12px; color: #202124; margin-bottom: 4px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-weight: 400; }
        .chrome-result-item .result-title-link { font-size: 20px; color: #1a0dab; text-decoration: none; display: inline-block; margin-bottom: 3px; font-weight: 400; }
        .chrome-result-item .result-title-link:hover { text-decoration: underline; }
        .chrome-result-item .snippet-text { color: #4d5156; margin: 0; }
        footer { padding: 15px 40px; background: #f2f2f2; font-size: 14px; color: #70757a; border-top: 1px solid #e4e4e4; width: 100%; box-sizing: border-box; margin-top: auto; }
        .footer-content { display: flex; gap: 20px; flex-wrap: wrap; justify-content: space-between; max-width: 1200px; margin: 0 auto; }
        .footer-links a { color: #70757a; text-decoration: none; margin-right: 15px; }
        .footer-links a:hover { color: #333; }
    </style>
</head>
<body>
    {% if not query %}
        <div class="home-wrapper">
            <div class="home-logo"><span class="g1">Bangla</span><span class="r1">Net</span></div>
            <form method="POST" class="home-search-form">
                <div class="search-box-wrapper">
                    <input type="text" name="query" autocomplete="off" required autofocus>
                </div>
                <div class="home-btn-container">
                    <button type="submit" class="g-btn">BanglaNet অনুসন্ধান</button>
                </div>
            </form>
            <div class="home-highlights">
                BanglaNet অফার করছে: 
                <a href="#" onclick="document.getElementsByName('query')[0].value='স্বপ্ন-কলম সাহিত্য পরিবার'; document.forms[0].submit(); return false;">স্বপ্ন-কলম সাহিত্য</a>
                <a href="#" onclick="document.getElementsByName('query')[0].value='আজকের বাংলাদেশ খবর'; document.forms[0].submit(); return false;">আজকের খবর</a>
            </div>
        </div>
    {% else %}
        <div class="search-header">
            <a href="/" class="logo-small"><span class="g1">Bangla</span><span class="r1">Net</span></a>
            <form method="POST">
                <div class="search-box-wrapper" style="max-width: 692px; height: 44px;">
                    <input type="text" name="query" value="{{ query }}" autocomplete="off" required>
                </div>
            </form>
        </div>
        <div class="results-container">
            {% if results %}
                <div class="result-stats">অনুসন্ধানের ফলাফল পাওয়া গেছে (প্রায় {{ results|length }} টি)</div>
                {% for res in results %}
                    <div class="chrome-result-item">
                        <span class="site-url">{{ res.link }}</span>
                        <a class="result-title-link" href="{{ res.link }}" target="_blank">{{ res.title }}</a>
                        <p class="snippet-text">{{ res.text }}</p>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color: #d32f2f; font-size: 16px; margin-top: 20px;">দুঃখিত, কোনো তথ্য লোড করা যায়নি। অনুগ্রহ করে আবার চেষ্টা করুন।</p>
            {% endif %}
        </div>
    {% endif %}
    <footer>
        <div class="footer-content">
            <div>বাংলাদেশ &bull; প্রতিষ্ঠাতা ও পরিচালক: মোঃ কামরুজ্জামান কাজল</div>
            <div class="footer-links">
                পাওয়ার্ড বাই: <a href="https://shopnokolom.kesug.com" target="_blank">স্বপ্ন-কলম সাহিত্য পরিবার</a>
            </div>
        </div>
    </footer>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    query = ""
    search_results = []
    
    if request.method == 'POST':
        query = request.form['query']
        search_results = fetch_live_results(query)
                
    return render_template_string(HTML_TEMPLATE, query=query, results=search_results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
