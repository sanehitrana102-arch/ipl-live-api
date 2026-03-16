from flask import Flask, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)
CORS(app)  # Sabhi websites ko access allowed

def fetch_cricbuzz_data():
    """Cricbuzz se live scores lao"""
    try:
        url = "https://www.cricbuzz.com/cricket-match/live-scores"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        
        matches = []
        
        # Cricbuzz ke match cards find karo
        match_cards = soup.find_all('div', class_='cb-mtch-lst cb-col cb-col-100 cb-tms-itm')
        
        for card in match_cards[:10]:  # Top 10 matches
            try:
                # Match title/teams
                title_elem = card.find('a', class_='cb-lv-scrs-well')
                title = title_elem.text.strip() if title_elem else 'Match'
                
                # Live score
                score_elem = card.find('div', class_='cb-lv-scrs-col')
                score = score_elem.text.strip() if score_elem else 'Yet to start'
                
                # Match status
                status_elem = card.find('div', class_='cb-text-live')
                status = status_elem.text.strip() if status_elem else 'Live'
                
                # Match link
                link = 'https://www.cricbuzz.com' + title_elem['href'] if title_elem else '#'
                
                matches.append({
                    'id': len(matches) + 1,
                    'title': title,
                    'score': score,
                    'status': status,
                    'link': link,
                    'source': 'Cricbuzz'
                })
            except:
                continue
        
        return matches
    
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return []

def fetch_match_details(match_id):
    """Specific match ki details lao (future use)"""
    # Isko baad mein implement kar sakte ho
    return {"message": "Coming soon"}

@app.route('/')
def home():
    """API ka home page"""
    return jsonify({
        'name': 'IPL Live Cricket API',
        'version': '1.0',
        'endpoints': {
            '/live': 'Get all live matches',
            '/match/<id>': 'Get specific match details'
        },
        'status': 'running',
        'source': 'Cricbuzz'
    })

@app.route('/live')
def live_scores():
    """Live scores endpoint"""
    try:
        matches = fetch_cricbuzz_data()
        return jsonify({
            'success': True,
            'matches': matches,
            'count': len(matches),
            'timestamp': str(requests.get('http://worldtimeapi.org/api/timezone/Asia/Kolkata').json().get('datetime', ''))[:19]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'matches': []
        }), 500

@app.route('/match/<int:match_id>')
def match_details(match_id):
    """Specific match details"""
    return jsonify({
        'success': True,
        'match_id': match_id,
        'details': fetch_match_details(match_id)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
