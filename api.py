from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
import time

app = Flask(__name__)
CORS(app)

def fetch_cricbuzz_data():
    """Cricbuzz se live scores lao with retry"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Multiple URLs try karo
    urls = [
        "https://www.cricbuzz.com/cricket-match/live-scores",
        "https://www.cricbuzz.com/cricket-match/live-scores/1",
        "https://www.cricbuzz.com/"
    ]
    
    for url in urls:
        try:
            print(f"Trying URL: {url}")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            matches = []
            
            # Different possible class names
            match_cards = soup.find_all('div', class_='cb-mtch-lst cb-col cb-col-100 cb-tms-itm')
            
            if not match_cards:
                match_cards = soup.find_all('div', class_='cb-col-100 cb-col cb-mtch-lst')
            
            for card in match_cards[:10]:
                try:
                    # Multiple selectors try karo
                    title_elem = (card.find('a', class_='cb-lv-scrs-well') or 
                                 card.find('a', class_='text-hvr-underline') or
                                 card.find('a', href=True))
                    
                    score_elem = (card.find('div', class_='cb-lv-scrs-col') or
                                 card.find('div', class_='cb-scr-wll-chv') or
                                 card.find('div', class_='cb-font-20'))
                    
                    status_elem = (card.find('div', class_='cb-text-live') or
                                  card.find('div', class_='cb-text-complete') or
                                  card.find('span', class_='cb-text-gray'))
                    
                    title = title_elem.text.strip() if title_elem else 'Match'
                    score = score_elem.text.strip() if score_elem else 'Yet to start'
                    status = status_elem.text.strip() if status_elem else 'Live'
                    
                    matches.append({
                        'title': title,
                        'score': score,
                        'status': status
                    })
                except:
                    continue
            
            if matches:
                return matches
                
        except Exception as e:
            print(f"Error with {url}: {str(e)}")
            continue
    
    # Agar kuch na mile to demo data bhejo
    return get_demo_data()

def get_demo_data():
    """Demo data for testing"""
    return [
        {
            'title': 'Mumbai Indians vs Chennai Super Kings',
            'score': 'MI 187/5 (18.2 ov)',
            'status': 'Live'
        },
        {
            'title': 'Royal Challengers Bangalore vs Kolkata Knight Riders',
            'score': 'RCB 145/3 (15 ov)',
            'status': 'Live'
        }
    ]

@app.route('/')
def home():
    return jsonify({
        'name': 'IPL Live Cricket API',
        'version': '1.0',
        'status': 'running',
        'endpoints': {
            '/live': 'Get all live matches',
            '/match/<id>': 'Get specific match details'
        }
    })

@app.route('/live')
def live_scores():
    try:
        matches = fetch_cricbuzz_data()
        return jsonify({
            'success': True,
            'matches': matches,
            'count': len(matches)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'matches': get_demo_data()  # Error pe demo data bhejo
        })

@app.route('/match/<int:match_id>')
def match_details(match_id):
    return jsonify({
        'success': True,
        'match_id': match_id,
        'message': 'Coming soon'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
