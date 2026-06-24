from flask import Flask, render_template_string, request
import requests
import urllib.parse

app = Flask(__name__)

# ইউজার এজেন্ট (ব্রাউজার হিসেবে রিকোয়েস্ট পাঠানোর জন্য)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
}

def fetch_live_results(query):
    search_results = []
    
    # ১. আপনার ওয়েবসাইটের অগ্রাধিকার (Custom Priority)
    # ইউজার যা-ই সার্চ করুক, তা যদি আপনার সাইটের বিষয়ের সাথে সামান্যও মিলে বা ডিরেক্ট সার্চ হয়, তবে আপনার সাইট আগে আসবে
    try:
        my_site_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}+site:shopnokolom.kesug.com"
        res_my = requests.get(my_site_url, headers=HEADERS, timeout=5)
        if res_my.status_code == 200:
            from bs4 import BeautifulSoup
            soup_my = BeautifulSoup(res_my.text, "html.parser")
            for rel in soup_my.find_all("div", class_="result")[:2]: # সর্বোচ্চ ২টি প্রাসঙ্গিক রেজাল্ট আপনার সাইট থেকে নেবে
                t_tag = rel.find("a", class_="result__url")
                s_tag = rel.find("a", class_="result__snippet")
                if t_tag:
                    search_results.append({
                        "title": "✨ [স্বপ্ন-কলম] " + t_tag.get_text(strip=True),
                        "link": "https://" + t_tag["href"].split("//")[-1].strip(),
                        "text": s_tag.get_text(strip=True) if s_tag else "আপনার প্রিয় সাহিত্য প্ল্যাটফর্ম স্বপ্ন-কলম।"
                    })
    except Exception as e:
        print(f"Priority site search error: {e}")

    # ২. সাধারণ ইন্টারনেট সার্চ (DuckDuckGo HTML ব্যাকএন্ড - যা কখনো ব্লক করে না)
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            results_divs = soup.find_all("div", class_="result")
            
            for div in results_divs:
                title_tag = div.find("a", class_="result__url")
                snippet_tag = div.find("a", class_="result__snippet")
                
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    raw_link = title_tag["href"]
                    # লিংক ফরম্যাট ঠিক করা
                    if "uddg=" in raw_link:
                        link = urllib.parse.unquote(raw_link.split("uddg=")[1].split("&")[0])
                    else:
                        link = raw_link
                        
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else "কোনো বিবরণ পাওয়া যায়নি।"
                    
                    # ডুপ্লিকেট লিংক বাদ দেওয়া (যদি আপনার সাইট আগেই এসে থাকে)
                    if not any(item['link'] == link for item in search_results):
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
    <title>BanglaNet - কামরুজ্জামান কাজল</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f9fbf9; color: #333; display: flex; flex-direction: column; min-height: 100vh; }
        .container { flex: 1; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: {{ 'center' if not query else 'flex-start' }}; }
        
        /* বাংলাদেশ পতাকার মেজাজে লোগো */
        .logo { font-size: 55px; font-weight: 900; margin-bottom: 5px; letter-spacing: -1px; filter: drop-shadow(0px 2px 4px rgba(0,0,0,0.1)); }
        .logo .bangla { color: #006a4e; } /* গাঢ় সবুজ */
        .logo .net { color: #f42a41; position: relative; } /* লাল বৃত্তের আমেজ */
        
        .owner-name { font-size: 14px; color: #555; font-weight: bold; margin-bottom: 25px; background: #e8f5e9; padding: 4px 12px; border-radius: 12px; border: 1px solid #c8e6c9; }
        
        form { width: 100%; max-width: 600px; text-align: center; }
        .search-box-container { position: relative; width: 100%; }
        input[type="text"] { width: 100%; padding: 14px 25px; font-size: 16px; border: 2px solid #006a4e; border-radius: 30px; outline: none; box-sizing: border-box; box-shadow: 0 4px 12px rgba(0,106,78,0.15); transition: 0.3s; }
        input[type="text"]:focus { box-shadow: 0 4px 20px rgba(244,42,65,0.25); border-color: #f42a41; }
        
        .btn-container { margin-top: 15px; }
        button { padding: 12px 28px; font-size: 15px; font-weight: bold; background-color: #006a4e; color: white; border: none; border-radius: 25px; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 6px rgba(0,0,0,0.15); }
        button:hover { background-color: #f42a41; }
        
        /* কিছু সার্চ না করা অবস্থায় ট্রেন্ডিং হাইলাইট */
        .highlights { width: 100%; max-width: 550px; margin-top: 40px; text-align: center; background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-top: 4px solid #006a4e; }
        .highlights h4 { margin: 0 0 15px 0; color: #006a4e; font-size: 16px; }
        .tags { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; }
        .tag { background: #f0f2f5; padding: 8px 16px; border-radius: 20px; font-size: 14px; text-decoration: none; color: #444; font-weight: 500; transition: 0.2s; border: 1px solid #e4e6eb; }
        .tag:hover { background: #006a4e; color: white; border-color: #006a4e; }
        
        /* সার্চ রেজাল্ট UI */
        .results { width: 100%; max-width: 650px; margin-top: 30px; }
        .result-item { background: white; padding: 20px; margin-bottom: 15px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); border-left: 4px solid #006a4e; transition: 0.2s; }
        .result-item:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
        .result-title { font-size: 18px; color: #1a0dab; font-weight: bold; text-decoration: none; display: inline-block; margin-bottom: 5px; }
        .result-title:hover { text-decoration: underline; color: #f42a41; }
        .result-link { font-size: 13px; color: #006a4e; margin-bottom: 8px; word-break: break-all; font-weight: 500; }
        .result-text { font-size: 14px; color: #4d5156; line-height: 1.5; }
        
        /* ফুটার */
        footer { text-align: center; padding: 15px; background: white; font-size: 13px; color: #666; border-top: 1px solid #e4e6eb; width: 100%; box-sizing: border-box; }
        footer a { color: #006a4e; font-weight: bold; text-decoration: none; }
        footer a:hover { text-decoration: underline; color: #f42a41; }
    </style>
</head>
<body>

    <div class="container">
        <div class="logo"><span class="bangla">Bangla</span><span class="net">Net</span></div>
        <div class="owner-name">প্রতিষ্ঠাতা ও পরিচালক: মোঃ কামরুজ্জামান কাজল</div>
        
        <form method="POST">
            <div class="search-box-container">
                <input type="text" name="query" placeholder="ইন্টারনেট অথবা স্বপ্ন-কলম থেকে খুঁজুন..." value="{{ query }}" autocomplete="off" required autofocus>
            </div>
            <div class="btn-container">
                <button type="submit">BanglaNet অনুসন্ধান</button>
            </div>
        </form>

        {% if not query %}
            <div class="highlights">
                <h4>🔥 আজকের ট্রেন্ডিং হাইলাইটস</h4>
                <div class="tags">
                    <a href="#" class="tag" onclick="document.getElementsByName('query')[0].value='স্বপ্ন-কলম সাহিত্য পরিবার'; document.forms[0].submit(); return false;">✨ স্বপ্ন-কলম সাহিত্য</a>
                    <a href="#" class="tag" onclick="document.getElementsByName('query')[0].value='মোঃ কামরুজ্জামান কাজল'; document.forms[0].submit(); return false;">✍️ মোঃ কামরুজ্জামান কাজল</a>
                    <a href="#" class="tag" onclick="document.getElementsByName('query')[0].value='আজকের বাংলা খবর'; document.forms[0].submit(); return false;">📰 আজকের খবর</a>
                    <a href="#" class="tag" onclick="document.getElementsByName('query')[0].value='বাংলা কবিতা ও গল্প'; document.forms[0].submit(); return false;">📖 বাংলা কবিতা</a>
                </div>
            </div>
        {% endif %}

        <div class="results">
            {% if results %}
                <p style="color: #70757a; font-size: 14px; margin-bottom: 15px;">অনুসন্ধানের লাইভ ফলাফল:</p>
                {% for res in results %}
                    <div class="result-item" style="{% if '[স্বপ্ন-কলম]' in res.title %}border-left-color: #f42a41; background: #fffde7;{% endif %}">
                        <div class="result-link">{{ res.link }}</div>
                        <a class="result-title" href="{{ res.link }}" target="_blank">{{ res.title }}</a>
                        <div class="result-text">{{ res.text }}</div>
                    </div>
                {% endfor %}
            {% elif query %}
                <p style="text-align:center; color: #d32f2f;">দুঃখিত, কোনো তথ্য লোড করা যায়নি। আবার চেষ্টা করুন।</p>
            {% endif %}
        </div>
    </div>

    <footer>
        পাওয়ার্ড বাই: <a href="https://shopnokolom.kesug.com" target="_blank">স্বপ্ন-কলম সাহিত্য পরিবার</a> | সর্বস্বত্ব সংরক্ষিত © ২০২৬
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
