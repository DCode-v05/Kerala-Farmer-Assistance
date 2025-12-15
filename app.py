from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import os
import datetime
import json
from threading import Lock
import hashlib
import secrets
import uuid
import tempfile
from typing import Dict, Any, Optional, List
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

# Import enhanced AI services
try:
    from farm_profile_service import FarmProfileService
    from smart_activity_tracker import SmartActivityTracker, ActivityType, ActivityStatus
    ENHANCED_SERVICES_AVAILABLE = True
    print("✅ Enhanced AI services loaded successfully")
except ImportError as e:
    print(f"⚠️ Enhanced services not available: {e}")
    ENHANCED_SERVICES_AVAILABLE = False


# -----------------------------
# Environment & Flask setup
# -----------------------------
load_dotenv()
app = Flask(__name__)
CORS(app, 
     origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5000", "http://127.0.0.1:5000", "null"], 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "OPTIONS"], 
     supports_credentials=True)
limiter = Limiter(key_func=get_remote_address, app=app, default_limits=["200 per hour"])
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Initialize translation service at startup
translation_service = None
try:
    from translation_service import get_translation_service
    logging.info("Initializing translation service at startup...")
    translation_service = get_translation_service()
    logging.info("Translation service initialized successfully")
except ImportError:
    logging.warning("Translation service dependencies not installed. Voice features will be unavailable.")
except Exception as e:
    logging.error(f"Failed to initialize translation service: {e}")
    translation_service = None


# -----------------------------
# Gemini initialization (updated)
# -----------------------------
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
model = None
try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        logging.info("Gemini initialized successfully")
    else:
        logging.warning("GEMINI_API_KEY not set; AI disabled")
except Exception as e:
    logging.exception(f"Error initializing Gemini: {e}")
    model = None


# -----------------------------
# JSON Database setup
# -----------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
OFFICER_QUERIES_FILE = os.path.join(DATA_DIR, 'officer_queries.json')
ACTIVITIES_FILE = os.path.join(DATA_DIR, 'activities.json')

# AIMS Database files
FARMERS_FILE = os.path.join(DATA_DIR, 'farmers.json')
LAND_DETAILS_FILE = os.path.join(DATA_DIR, 'land_details.json')
WEATHER_SNAPSHOT_FILE = os.path.join(DATA_DIR, 'weather_snapshot.json')
MARKET_PRICES_FILE = os.path.join(DATA_DIR, 'market_prices.json')

# Session configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=1)

file_lock = Lock()


def ensure_data_dir():
    """Ensure the data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def read_json_file(file_path):
    """Read data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def write_json_file(file_path, data):
    """Write data to JSON file"""
    ensure_data_dir()
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_id(data_list):
    """Get the next available ID"""
    if not data_list:
        return 1
    return max(item.get('id', 0) for item in data_list) + 1


def add_officer_query(farmer_id, topic, question, contact_phone=None, contact_email=None):
    """Add a new officer query"""
    with file_lock:
        queries = read_json_file(OFFICER_QUERIES_FILE)
        new_query = {
            'id': get_next_id(queries),
            'farmer_id': farmer_id,
            'topic': topic,
            'question': question,
            'contact_phone': contact_phone,
            'contact_email': contact_email,
            'status': 'submitted',
            'created_at': datetime.datetime.now().isoformat()
        }
        queries.append(new_query)
        write_json_file(OFFICER_QUERIES_FILE, queries)
        return new_query['id']


def get_officer_queries(farmer_id=None):
    """Get officer queries, optionally filtered by farmer_id"""
    queries = read_json_file(OFFICER_QUERIES_FILE)
    if farmer_id:
        queries = [q for q in queries if q.get('farmer_id') == farmer_id]
    return sorted(queries, key=lambda x: x.get('created_at', ''), reverse=True)


def add_activity(farmer_id, activity_type, notes=None):
    """Add a new activity"""
    with file_lock:
        activities = read_json_file(ACTIVITIES_FILE)
        new_activity = {
            'id': get_next_id(activities),
            'farmer_id': farmer_id,
            'activity_type': activity_type,
            'notes': notes or '',
            'created_at': datetime.datetime.now().isoformat()
        }
        activities.append(new_activity)
        write_json_file(ACTIVITIES_FILE, activities)
        return new_activity['id']


# -----------------------------
# AIMS Authentication Functions
# -----------------------------
def generate_farmer_id():
    """Generate a new unique farmer ID"""
    farmers = read_json_file(FARMERS_FILE)
    existing_ids = [f.get('id', '') for f in farmers]
    
    # Generate new ID in format KL### where ### is incremental
    counter = len(existing_ids) + 1
    while True:
        new_id = f"KL{counter:03d}"
        if new_id not in existing_ids:
            return new_id
        counter += 1

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_password(name, farmer_id):
    """Generate password in format: NameFarmerID@123"""
    # Remove spaces and take first name
    first_name = name.split()[0] if name else "Farmer"
    return f"{first_name}{farmer_id}@123"

def authenticate_farmer(farmer_id, password):
    """Authenticate farmer with ID and password"""
    farmers = read_json_file(FARMERS_FILE)
    
    for farmer in farmers:
        if farmer.get('id') == farmer_id:
            expected_password = generate_password(farmer.get('name', ''), farmer_id)
            if password == expected_password:
                return farmer
    return None

def get_farmer_by_id(farmer_id):
    """Get farmer details by ID"""
    farmers = read_json_file(FARMERS_FILE)
    
    for farmer in farmers:
        if farmer.get('id') == farmer_id:
            return farmer
    return None

def get_farmer_land_details(farmer_id):
    """Get land details for a farmer"""
    land_details = read_json_file(LAND_DETAILS_FILE)
    return [land for land in land_details if land.get('farmer_id') == farmer_id]

def get_farmer_weather(farmer_id):
    """Get weather data for a farmer"""
    weather_data = read_json_file(WEATHER_SNAPSHOT_FILE)
    
    for weather in weather_data:
        if weather.get('farmer_id') == farmer_id:
            return weather
    return None

def get_market_prices_for_location(district=None):
    """Get market prices, optionally filtered by district"""
    market_prices = read_json_file(MARKET_PRICES_FILE)
    
    if district:
        return [price for price in market_prices if price.get('district', '').lower() == district.lower()]
    
    # Return latest 10 prices if no district specified
    return sorted(market_prices, key=lambda x: x.get('fetched_at', ''), reverse=True)[:10]

def register_new_farmer(farmer_data):
    """Register a new farmer in AIMS database"""
    with file_lock:
        farmers = read_json_file(FARMERS_FILE)
        
        # Generate new farmer ID
        farmer_id = generate_farmer_id()
        
        # Create farmer record
        new_farmer = {
            'id': farmer_id,
            'registration_number': f"REG{len(farmers) + 1:03d}",
            'kerala_farmer_id': f"KFL{len(farmers) + 1:03d}",
            'name': farmer_data.get('name'),
            'mobile_no': farmer_data.get('mobile_no'),
            'gender': farmer_data.get('gender'),
            'dob': farmer_data.get('dob'),
            'category': farmer_data.get('category', 'General'),
            'address': farmer_data.get('address'),
            'post_office': farmer_data.get('post_office'),
            'pin_code': farmer_data.get('pin_code'),
            'education_level': farmer_data.get('education_level'),
            'area_acres': farmer_data.get('area_acres', 0.0),
            'created_at': datetime.datetime.now().isoformat(),
            # Optional fields with defaults
            'aadhaar_no': farmer_data.get('aadhaar_no'),
            'marketing_interest': farmer_data.get('marketing_interest', 0),
            'processing_interest': farmer_data.get('processing_interest', 0),
            'ration_card_no': farmer_data.get('ration_card_no'),
            'ifsc': farmer_data.get('ifsc'),
            'bank_account_no': farmer_data.get('bank_account_no'),
            'farmhouse_krishibhavan': farmer_data.get('farmhouse_krishibhavan'),
            'lat': farmer_data.get('lat'),
            'lon': farmer_data.get('lon')
        }
        
        farmers.append(new_farmer)
        write_json_file(FARMERS_FILE, farmers)
        
        return new_farmer

def get_farmer_profile_complete(farmer_id):
    """Get complete farmer profile with all related data"""
    farmer = get_farmer_by_id(farmer_id)
    if not farmer:
        return None
    
    # Get related data
    land_details = get_farmer_land_details(farmer_id)
    weather_data = get_farmer_weather(farmer_id)
    
    # Get district from address for market prices
    district = None
    if farmer.get('address'):
        # Simple district extraction - can be improved
        address_parts = farmer['address'].split(', ')
        if len(address_parts) >= 2:
            district = address_parts[-1]  # Assume last part is district
    
    market_prices = get_market_prices_for_location(district)
    
    return {
        'farmer': farmer,
        'land_details': land_details,
        'weather': weather_data,
        'market_prices': market_prices
    }

# Initialize data directory
ensure_data_dir()

# Initialize enhanced services if available
if ENHANCED_SERVICES_AVAILABLE:
    farm_profile_service = FarmProfileService()
    smart_activity_tracker = SmartActivityTracker()
    print("🚀 AI-powered farming assistant services initialized")
else:
    farm_profile_service = None
    smart_activity_tracker = None
    print("📝 Running with basic services only")


# -----------------------------
# Knowledge helpers (mocked)
# -----------------------------
def get_current_market_data():
    return {
        'date': datetime.datetime.now().strftime('%Y-%m-%d'),
        'market': 'Kochi & Palakkad Mandis',
        'crops': {
            'rubber': {'price': '₹178 - ₹182/kg (RSS-4)', 'trend': 'up'},
            'coconut': {'price': '₹30 - ₹34/piece', 'trend': 'stable'},
            'paddy': {'price': '₹2200 - ₹2350/quintal (Uma)', 'trend': 'stable'},
            'black_pepper': {'price': '₹550 - ₹570/kg (ungarbled)', 'trend': 'down'},
            'banana': {'price': '₹35 - ₹42/kg (Nendran)', 'trend': 'up'}
        }
    }


def get_weather_forecast():
    return {
        'location': 'Central Kerala',
        'today': {'temp': '29°C', 'condition': 'Cloudy with afternoon showers', 'rainfall_mm': 15},
        'forecast_3_day': [
            {'day': 'Tomorrow', 'condition': 'Heavy rain expected', 'rainfall_mm': 40},
            {'day': 'Day after', 'condition': 'Light showers', 'rainfall_mm': 10}
        ],
        'advisory': 'Heavy rain expected tomorrow. Avoid spraying pesticides or fertilizers. Ensure fields have proper drainage.'
    }


def detect_crop_from_query(message: str) -> str:
    """Return canonical crop key found in the query or empty string if not found."""
    text = (message or "").lower()
    synonyms = {
        'paddy': ['paddy', 'rice', 'uma', 'nel', 'nellu'],
        'coconut': ['coconut', 'thenga', 'tenga', 'copra'],
        'rubber': ['rubber'],
        'black_pepper': ['black pepper', 'pepper', 'kurumulak', 'kurumulaku', 'milagu'],
        'banana': ['banana', 'plantain', 'nendran', 'nenthran']
    }
    for key, words in synonyms.items():
        for w in words:
            if w in text:
                return key
    return ''


def format_market_response(crop_key: str, language: str) -> str:
    data = get_current_market_data()
    crops = data['crops']
    date = data['date']
    if crop_key and crop_key in crops:
        price = crops[crop_key].get('price', 'N/A')
        trend = crops[crop_key].get('trend', '-')
        if language == 'ml':
            names = {
                'paddy': 'നെല്ല് (ഉമ)',
                'coconut': 'തേങ്ങ',
                'rubber': 'റബ്ബർ',
                'black_pepper': 'കുരുമുളക്',
                'banana': 'വാഴ (നെന്ത്രൻ)'
            }
            name_ml = names.get(crop_key, crop_key)
            return f"ഇന്ന് ({date}) കേരള വിപണിയിൽ {name_ml} വില ഏകദേശം {price}."
        else:
            pretty = {
                'paddy': 'paddy (Uma)',
                'coconut': 'coconut',
                'rubber': 'rubber',
                'black_pepper': 'black pepper',
                'banana': 'banana (Nendran)'
            }
            name_en = pretty.get(crop_key, crop_key)
            return f"As of {date} in Kerala markets, {name_en} trades around {price}."
    # If no crop specified, show snapshot summary
    if language == 'ml':
        lines = [f"ഇന്ന് ({date}) കേരള വിപണി വിലകൾ:"]
    else:
        lines = [f"Kerala market prices as of {date}:"]
    for key, info in crops.items():
        label = key.replace('_', ' ').title()
        lines.append(f"- {label}: {info.get('price', 'N/A')}")
    return "\n".join(lines)


def get_detailed_kerala_crop_calendar():
    # Minimal month example; extend as needed
    return {
        9: {
            'month_name': 'September',
            'malayalam_name': 'സെപ്റ്റംബർ',
            'season': 'Late Monsoon / Second Inter-monsoon',
            'weather': 'Decreasing rainfall, higher humidity (100-200mm rainfall)',
            'temperature': '24-30°C',
            'humidity': '75-85%',
            'major_activities': {
                'sowing': [{'crop': 'Vegetables (Rabi)', 'varieties': ['Cowpea', 'Bhindi', 'Amaranthus']}],
                'harvesting': [{'crop': 'Paddy (Kharif - First Crop)', 'varieties': ['Jyothi', 'Uma']}],
                'maintenance': [{'activity': 'Land preparation for Rabi season', 'focus': 'Ploughing and adding organic manure'}]
            },
            'weather_advisory': 'Prepare fields for the next season. Ensure proper drainage for harvested paddy.',
            'government_schemes': ['Rashtriya Krishi Vikas Yojana'],
            'market_trends': 'Paddy prices are stable. High demand for fresh vegetables.'
        }
    }


def create_expert_farming_prompt(user_message: str, language: str = 'en') -> str:
    now = datetime.datetime.now()
    current_month = get_detailed_kerala_crop_calendar().get(now.month, {})
    market_data = get_current_market_data()
    weather_data = get_weather_forecast()

    system_prompt = "You are Krishi Sakhi, an expert Kerala farming assistant. Provide precise, safe, actionable guidance grounded in Kerala context. If you are unsure, ask clarifying questions. Use lists and short paragraphs. Prefer Malayalam if requested."

    context = f"""
CURRENT CONTEXT FOR KERALA DATED: {now.strftime('%d %B %Y')}

1) Current Month's Agricultural Calendar ({current_month.get('month_name', 'N/A')}):
   - Season: {current_month.get('season', 'N/A')}
   - Sowing: {json.dumps(current_month.get('major_activities', {}).get('sowing', []))}
   - Harvesting: {json.dumps(current_month.get('major_activities', {}).get('harvesting', []))}
   - Advisory: {current_month.get('weather_advisory', 'N/A')}

2) Real-time Market Data:
   - Date: {market_data['date']}
   - Prices: {json.dumps(market_data['crops'])}

3) Weather Forecast:
   - Location: {weather_data['location']}
   - Today: {json.dumps(weather_data['today'])}
   - Next 3 Days: {json.dumps(weather_data['forecast_3_day'])}
   - Advisory: {weather_data['advisory']}
"""

    final = f"""{system_prompt}

{context}

---
FARMER'S QUERY: "{user_message}"
---

Respond in English. Include bullet points and specific next steps. Keep it concise and practical.
(Note: For voice features, the response will be automatically converted to Malayalam speech)
"""
    return final


# -----------------------------
# Schemes & Officers (static for demo; replace with real APIs)
# -----------------------------
KERALA_SCHEMES = [
    {
        'id': 'pm-kisan',
        'name': 'PM-KISAN Samman Nidhi',
        'amount': '₹6,000/year',
        'eligibility': 'Small & marginal farmers with cultivable land',
        'apply_url': 'https://pmkisan.gov.in/',
        'contact': 'Call 155261 / 011-24300606'
    },
    {
        'id': 'pmfby',
        'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
        'amount': 'Subsidized crop insurance premiums',
        'eligibility': 'All farmers growing notified crops in notified areas',
        'apply_url': 'https://pmfby.gov.in/',
        'contact': 'Toll-free 1800-180-1111'
    },
    {
        'id': 'rkvv',
        'name': 'Rashtriya Krishi Vikas Yojana',
        'amount': 'Support for agri infrastructure and innovations',
        'eligibility': 'As per specific projects via Dept. of Agriculture, Kerala',
        'apply_url': 'https://rkvynema.icar.gov.in/',
        'contact': 'Kerala DoA local offices'
    },
    {
        'id': 'kfas',
        'name': 'Kerala Farm Mechanization Assistance',
        'amount': 'Subsidy for farm machinery and tools',
        'eligibility': 'Registered farmers in Kerala',
        'apply_url': 'https://www.aims.kerala.gov.in/',
        'contact': 'AIMS Helpline 0471-2575523'
    }
]


LOCAL_OFFICERS = [
    {'id': 1, 'name': 'Agricultural Officer - Kuttanad', 'phone': '+91-9447XXXXXX', 'email': 'ao.kuttanad@example.gov.in'},
    {'id': 2, 'name': 'Krishi Bhavan - Alappuzha', 'phone': '+91-9495XXXXXX', 'email': 'krishi.alappuzha@example.gov.in'}
]


# -----------------------------
# Routes
# -----------------------------
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.datetime.now().isoformat()})


@app.route('/', methods=['GET'])
def root_index():
    """Serve the main application HTML file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        logging.error(f"Error serving index.html: {e}")
        return f"Error loading application: {e}", 500


@app.route('/api', methods=['GET'])
def api_index():
    return jsonify({
        'endpoints': [
            'GET /api/health',
            'POST /api/login',
            'POST /api/register',
            'GET /api/farmer-profile',
            'POST /api/logout',
            'GET /api/check-session',
            'POST /api/chat',
            'GET /api/schemes',
            'GET /api/officers',
            'POST /api/officer/query',
            'GET /api/officer/queries?farmer_id=1',
            'POST /api/activities'
        ]
    })


@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    return jsonify({'success': True, 'schemes': KERALA_SCHEMES})


@app.route('/api/officers', methods=['GET'])
def get_officers():
    return jsonify({'success': True, 'officers': LOCAL_OFFICERS})


@app.route('/api/officer/query', methods=['POST', 'OPTIONS'])
def officer_query():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.json or {}
    farmer_id = data.get('farmer_id')
    topic = data.get('topic')
    question = data.get('question')
    contact_phone = data.get('contact_phone')
    contact_email = data.get('contact_email')

    if not topic or not question:
        return jsonify({'success': False, 'error': 'Topic and question are required'}), 400

    query_id = add_officer_query(farmer_id, topic, question, contact_phone, contact_email)

    # Optional: forward via SendGrid if configured
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        sg_key = os.getenv('SENDGRID_API_KEY')
        forward_to = os.getenv('OFFICER_FORWARD_EMAIL')
        if sg_key and forward_to:
            message = Mail(
                from_email=os.getenv('FROM_EMAIL', 'noreply@krishisakhi.local'),
                to_emails=forward_to,
                subject=f"New Farmer Query ({topic})",
                html_content=f"<p><b>Farmer ID:</b> {farmer_id or '-'}<br><b>Topic:</b> {topic}<br><b>Question:</b> {question}<br><b>Phone:</b> {contact_phone or '-'}<br><b>Email:</b> {contact_email or '-'}<br><b>Query ID:</b> {query_id}</p>"
            )
            sg = SendGridAPIClient(sg_key)
            sg.send(message)
    except Exception as e:
        logging.warning(f"SendGrid forward skipped/failed: {e}")

    return jsonify({'success': True, 'query_id': query_id})


@app.route('/api/officer/queries', methods=['GET'])
def officer_queries_list():
    farmer_id = request.args.get('farmer_id')
    if farmer_id:
        try:
            farmer_id = int(farmer_id)
        except ValueError:
            farmer_id = None
    
    queries = get_officer_queries(farmer_id)
    return jsonify({'success': True, 'queries': queries})


@app.route('/api/activities', methods=['POST'])
def log_activity():
    try:
        data = request.json or {}
        farmer_id = session.get('farmer_id') or data.get('farmer_id')
        
        if not farmer_id:
            return jsonify({
                'success': False, 
                'error': 'Authentication required'
            }), 401
        
        activity_type = data.get('activity_type')
        if not activity_type:
            return jsonify({
                'success': False, 
                'error': 'activity_type is required'
            }), 400
        
        # Use smart activity tracker for enhanced logging
        enhanced_activity = smart_activity_tracker.log_activity(farmer_id, data)
        
        # Also save to the basic activities file for compatibility
        activity_id = add_activity(farmer_id, activity_type, data.get('notes', ''))
        enhanced_activity['basic_activity_id'] = activity_id
        
        return jsonify({
            'success': True, 
            'activity': enhanced_activity
        })
        
    except Exception as e:
        logging.exception(f"Log activity error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to log activity'
        }), 500


# -----------------------------
# Authentication Endpoints
# -----------------------------
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json or {}
        farmer_id = data.get('farmer_id', '').strip()
        password = data.get('password', '').strip()
        
        if not farmer_id or not password:
            return jsonify({
                'success': False, 
                'error': 'Farmer ID and password are required'
            }), 400
        
        # Authenticate farmer
        farmer = authenticate_farmer(farmer_id, password)
        
        if farmer:
            # Set permanent session
            session.permanent = True
            session['farmer_id'] = farmer_id
            session['farmer_name'] = farmer.get('name')
            
            # Debug logging
            logging.info(f"Login successful - Setting session for farmer_id: {farmer_id}")
            logging.info(f"Session keys after login: {list(session.keys())}")
            logging.info(f"Session data after login: {dict(session)}")
            logging.info(f"Session permanent after login: {session.permanent}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'farmer': {
                    'farmer_id': farmer['id'],
                    'name': farmer['name'],
                    'mobile_number': farmer.get('mobile_no'),
                    'gender': farmer.get('gender'),
                    'date_of_birth': farmer.get('dob'),
                    'address': farmer.get('address'),
                    'post_office': farmer.get('post_office'),
                    'pin_code': farmer.get('pin_code'),
                    'education_level': farmer.get('education_level'),
                    'total_farm_area': farmer.get('area_acres'),
                    'registration_date': farmer.get('created_at')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid Farmer ID or password'
            }), 401
            
    except Exception as e:
        logging.exception(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json or {}
        
        # Required fields
        required_fields = ['name', 'mobile_no', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'{field.replace("_", " ").title()} is required'
                }), 400
        
        # Check if mobile number already exists
        farmers = read_json_file(FARMERS_FILE)
        mobile_no = data.get('mobile_no').strip()
        
        for farmer in farmers:
            if farmer.get('mobile_no') == mobile_no:
                return jsonify({
                    'success': False,
                    'error': 'A farmer with this mobile number already exists'
                }), 400
        
        # Register new farmer
        new_farmer = register_new_farmer(data)
        
        # Generate password
        password = generate_password(new_farmer['name'], new_farmer['id'])
        
        # Set session
        session['farmer_id'] = new_farmer['id']
        session['farmer_name'] = new_farmer['name']
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'farmer': {
                'id': new_farmer['id'],
                'name': new_farmer['name'],
                'mobile_no': new_farmer['mobile_no'],
                'password': password  # Show password once for the user to note down
            }
        })
        
    except Exception as e:
        logging.exception(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/farmer-profile', methods=['GET'])
def get_farmer_profile():
    try:
        # Check if user is logged in via session
        farmer_id = session.get('farmer_id')
        
        # Also check for farmer_id in query params (for API access)
        if not farmer_id:
            farmer_id = request.args.get('farmer_id')
        
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required. Please login first.'
            }), 401
        
        # Get basic farmer data
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get enhanced profile using the farm profile service
        enhanced_profile = farm_profile_service.get_detailed_farmer_profile(farmer)
        
        return jsonify({
            'success': True,
            'profile': enhanced_profile
        })
        
    except Exception as e:
        logging.exception(f"Get profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get authenticated farmer profile - simpler endpoint for frontend"""
    try:
        # Debug logging
        logging.info(f"Profile request from origin: {request.headers.get('Origin', 'No Origin')}")
        logging.info(f"Profile request - Session keys: {list(session.keys())}")
        logging.info(f"Profile request - Session permanent: {session.permanent}")
        logging.info(f"Profile request - Session data: {dict(session)}")
        logging.info(f"Profile request - Request cookies: {dict(request.cookies)}")
        
        # Check if user is logged in via session
        farmer_id = session.get('farmer_id')
        logging.info(f"Profile request - farmer_id from session: {farmer_id}")
        
        if not farmer_id:
            logging.warning("Profile request denied - No farmer_id in session")
            return jsonify({
                'success': False,
                'error': 'Authentication required. Please login first.'
            }), 401
        
        # Get farmer data
        farmer = get_farmer_by_id(farmer_id)
        
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Map fields from farmers.json structure to frontend expected format
        farmer_data = {
            'farmer_id': farmer.get('id'),
            'name': farmer.get('name'),
            'mobile_number': farmer.get('mobile_no'),  # Map mobile_no to mobile_number
            'gender': farmer.get('gender'),
            'date_of_birth': farmer.get('dob'),  # Map dob to date_of_birth
            'address': farmer.get('address'),
            'post_office': farmer.get('post_office'),
            'pin_code': farmer.get('pin_code'),
            'education_level': farmer.get('education_level'),
            'total_farm_area': farmer.get('area_acres'),  # Map area_acres to total_farm_area
            'registration_date': farmer.get('created_at')
        }
        
        return jsonify({
            'success': True,
            'farmer': farmer_data
        })
        
    except Exception as e:
        logging.exception(f"Get profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Clear session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
        
    except Exception as e:
        logging.exception(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/api/check-session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    farmer_id = session.get('farmer_id')
    farmer_name = session.get('farmer_name')
    
    if farmer_id:
        return jsonify({
            'success': True,
            'logged_in': True,
            'farmer': {
                'id': farmer_id,
                'name': farmer_name
            }
        })
    else:
        return jsonify({
            'success': True,
            'logged_in': False
        })


@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json or {}
        user_message = data.get('message', '')
        language = data.get('language', 'en')

        if not user_message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        # If AI is unavailable, provide a rule-based fallback for common queries
        if not model:
            lower_q = user_message.lower()
            if any(k in lower_q for k in ['market', 'price', 'rate', 'mandi']):
                crop_key = detect_crop_from_query(user_message)
                text = format_market_response(crop_key, language)
                return jsonify({'success': True, 'response': {'text': text, 'type': 'fallback'}})
            msg = "AI service is currently unavailable. Please try again later." if language != 'ml' else "AI സേവനം നിലവിൽ ലഭ്യമല്ല. കുറച്ച് സമയം കഴിഞ്ഞ് വീണ്ടും ശ്രമിക്കുക."
            return jsonify({'success': True, 'response': {'text': msg, 'type': 'fallback'}})

        prompt = create_expert_farming_prompt(user_message, 'en')  # Always use English for AI responses
        generation_config = genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=1024,
            top_p=0.9,
            top_k=35
        )
        try:
            logging.info(f"Sending prompt to Gemini: {prompt[:100]}...")
            response = model.generate_content(prompt, generation_config=generation_config)
            logging.info(f"Gemini response received: {response.text[:100]}...")
            structured_response = {'text': response.text, 'type': 'general_ai_response'}
        except Exception as e:
            logging.exception(f"Gemini API error: {e}")
            # AI failed mid-call; respond with market-price fallback if applicable
            lower_q = user_message.lower()
            if any(k in lower_q for k in ['market', 'price', 'rate', 'mandi']):
                crop_key = detect_crop_from_query(user_message)
                text = format_market_response(crop_key, language)
            else:
                text = "AI temporarily unavailable. Please try again." if language != 'ml' else "AI താൽക്കാലികമായി ലഭ്യമല്ല. ദയവായി വീണ്ടും ശ്രമിക്കുക."
            structured_response = {'text': text, 'type': 'fallback'}
        return jsonify({'success': True, 'response': structured_response, 'timestamp': datetime.datetime.now().isoformat()})
    except Exception as e:
        logging.exception(f"Chat endpoint error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error', 'details': str(e)}), 500


# -----------------------------
# Data API Endpoints
# -----------------------------
@app.route('/api/market-prices', methods=['GET'])
def get_market_prices_api():
    """Get current market prices for Kerala"""
    try:
        from market_service import get_kerala_market_prices
        
        crop_name = request.args.get('crop')
        limit = int(request.args.get('limit', 50))
        
        prices = get_kerala_market_prices(crop_name, limit)
        
        return jsonify({
            'success': True,
            'prices': prices,
            'total_records': len(prices),
            'crop_filter': crop_name
        })
    except Exception as e:
        logging.exception(f"Market prices error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch market prices'
        }), 500


@app.route('/api/market-prices/trends', methods=['GET'])
def get_price_trends_api():
    """Get price trends for a specific crop"""
    try:
        from market_service import get_price_trends
        
        crop_name = request.args.get('crop')
        days = int(request.args.get('days', 7))
        
        if not crop_name:
            return jsonify({
                'success': False,
                'error': 'Crop name is required'
            }), 400
        
        trends = get_price_trends(crop_name, days)
        
        return jsonify({
            'success': True,
            'trends': trends
        })
    except Exception as e:
        logging.exception(f"Price trends error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch price trends'
        }), 500


@app.route('/api/market-prices/advisory', methods=['GET'])
def get_market_advisory_api():
    """Get market advisory based on current prices"""
    try:
        from market_service import get_kerala_market_prices, get_market_advisory
        
        # Get recent market data
        market_data = get_kerala_market_prices(limit=100)
        advisory = get_market_advisory(market_data)
        
        return jsonify({
            'success': True,
            'advisory': advisory,
            'market_data_summary': {
                'total_records': len(market_data),
                'crops_covered': len(set(item.get('commodity', '') for item in market_data))
            }
        })
    except Exception as e:
        logging.exception(f"Market advisory error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate market advisory'
        }), 500


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get current weather data for Kerala"""
    try:
        from weather_service import get_current_weather
        weather_data = get_current_weather()
        
        return jsonify({
            'success': True,
            'weather': weather_data
        })
    except Exception as e:
        logging.exception(f"Weather data error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch weather data'
        }), 500


@app.route('/api/weather/forecast', methods=['GET'])
def get_weather_forecast_api():
    """Get 7-day weather forecast for Kerala"""
    try:
        from weather_service import get_weather_forecast
        forecast_data = get_weather_forecast()
        
        return jsonify({
            'success': True,
            'forecast': forecast_data
        })
    except Exception as e:
        logging.exception(f"Weather forecast error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch weather forecast'
        }), 500


@app.route('/api/weather/advisory', methods=['GET'])
def get_weather_advisory_api():
    """Get weather-based farming advisory"""
    try:
        from weather_service import get_current_weather, get_weather_forecast, get_weather_advisory
        
        current_weather = get_current_weather()
        forecast = get_weather_forecast()
        advisory = get_weather_advisory(current_weather, forecast)
        
        return jsonify({
            'success': True,
            'current_weather': current_weather,
            'forecast': forecast,
            'advisory': advisory
        })
    except Exception as e:
        logging.exception(f"Weather advisory error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate weather advisory'
        }), 500


@app.route('/api/activities', methods=['GET'])
def get_activities():
    """Get farmer activities"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        activities = read_json_file(ACTIVITIES_FILE)
        farmer_activities = [a for a in activities if a.get('farmer_id') == farmer_id]
        
        return jsonify({
            'success': True,
            'activities': sorted(farmer_activities, key=lambda x: x.get('created_at', ''), reverse=True)
        })
    except Exception as e:
        logging.exception(f"Get activities error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch activities'
        }), 500


# -----------------------------
# Dashboard Data Endpoint
# -----------------------------
@app.route('/api/dashboard-data', methods=['GET'])
def get_dashboard_data():
    """Get comprehensive dashboard data including weather, market prices, and advisory"""
    try:
        from weather_service import get_current_weather, get_weather_forecast, get_weather_advisory
        from market_service import get_kerala_market_prices, get_market_advisory
        
        # Get weather data
        current_weather = get_current_weather()
        forecast = get_weather_forecast()
        weather_advisory = get_weather_advisory(current_weather, forecast)
        
        # Get market data
        market_prices = get_kerala_market_prices(limit=20)  # Top 20 for dashboard
        market_advisory = get_market_advisory(market_prices)
        
        # Get farmer activities if logged in
        farmer_id = session.get('farmer_id')
        recent_activities = []
        if farmer_id:
            activities = read_json_file(ACTIVITIES_FILE)
            recent_activities = [a for a in activities if a.get('farmer_id') == farmer_id][-5:]  # Last 5 activities
        
        return jsonify({
            'success': True,
            'dashboard': {
                'weather': {
                    'current': current_weather,
                    'forecast': forecast['forecast'][:3] if forecast.get('forecast') else [],  # Next 3 days
                    'advisory': weather_advisory
                },
                'market': {
                    'prices': market_prices[:10],  # Top 10 for dashboard
                    'advisory': market_advisory
                },
                'activities': recent_activities,
                'generated_at': datetime.datetime.now().isoformat()
            }
        })
    except Exception as e:
        logging.exception(f"Dashboard data error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch dashboard data'
        }), 500


# -----------------------------
# AI-Powered Farming Assistant Endpoints
# -----------------------------
@app.route('/api/activity-suggestions', methods=['GET'])
def get_activity_suggestions():
    """Get intelligent activity suggestions based on farmer context"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get enhanced profile
        farmer_profile = farm_profile_service.get_detailed_farmer_profile(farmer)
        
        # Get current weather for context
        try:
            from weather_service import get_current_weather
            current_weather = get_current_weather()
        except:
            current_weather = None
        
        # Get intelligent suggestions
        suggestions = smart_activity_tracker.get_activity_suggestions(
            farmer_id, farmer_profile, current_weather
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logging.exception(f"Activity suggestions error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get activity suggestions'
        }), 500


@app.route('/api/upcoming-activities', methods=['GET'])
def get_upcoming_activities():
    """Get upcoming recommended activities for the farmer"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get enhanced profile
        farmer_profile = farm_profile_service.get_detailed_farmer_profile(farmer)
        
        # Get days ahead parameter
        days_ahead = int(request.args.get('days', 30))
        
        # Get upcoming activities
        upcoming = smart_activity_tracker.get_upcoming_activities(
            farmer_id, farmer_profile, days_ahead
        )
        
        return jsonify({
            'success': True,
            'upcoming_activities': upcoming,
            'planning_horizon_days': days_ahead
        })
        
    except Exception as e:
        logging.exception(f"Upcoming activities error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get upcoming activities'
        }), 500


@app.route('/api/activity-plan', methods=['GET', 'POST'])
def manage_activity_plan():
    """Create or get comprehensive activity plan for farmer"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get enhanced profile
        farmer_profile = farm_profile_service.get_detailed_farmer_profile(farmer)
        
        if request.method == 'POST':
            # Create new activity plan
            data = request.json or {}
            planning_horizon = data.get('planning_horizon_days', 90)
            
            activity_plan = smart_activity_tracker.create_activity_plan(
                farmer_id, farmer_profile, planning_horizon
            )
            
            return jsonify({
                'success': True,
                'activity_plan': activity_plan
            })
        
        else:
            # Get existing or generate default plan
            activity_plan = smart_activity_tracker.create_activity_plan(
                farmer_id, farmer_profile, 30  # Default 30 days
            )
            
            return jsonify({
                'success': True,
                'activity_plan': activity_plan
            })
        
    except Exception as e:
        logging.exception(f"Activity plan error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to manage activity plan'
        }), 500


@app.route('/api/crop-recommendations', methods=['GET'])
def get_crop_recommendations():
    """Get personalized crop recommendations for the farmer"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get season parameter
        season = request.args.get('season')
        
        # Get crop recommendations
        recommendations = farm_profile_service.get_crop_recommendations(farmer, season)
        
        return jsonify({
            'success': True,
            'crop_recommendations': recommendations,
            'season': season or 'current'
        })
        
    except Exception as e:
        logging.exception(f"Crop recommendations error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get crop recommendations'
        }), 500


@app.route('/api/activity-analysis', methods=['GET'])
def get_activity_analysis():
    """Get analysis of farmer's past activities for insights"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer's activities
        activities = read_json_file(ACTIVITIES_FILE)
        farmer_activities = [a for a in activities if a.get('farmer_id') == farmer_id]
        
        if not farmer_activities:
            return jsonify({
                'success': True,
                'analysis': {'message': 'No activities recorded yet'},
                'recommendations': [{
                    'type': 'getting_started',
                    'message': 'Start by logging your daily farming activities to get personalized insights',
                    'malayalam': 'വ്യക്തിഗത ഉൾക്കാഴ്ചകൾ ലഭിക്കുന്നതിന് നിങ്ങളുടെ ദൈനംദിന കൃഷി പ്രവർത്തനങ്ങൾ രേഖപ്പെടുത്താൻ ആരംഭിക്കുക'
                }]
            })
        
        # Analyze patterns
        analysis = smart_activity_tracker.analyze_farmer_patterns(
            farmer_id, farmer_activities
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        logging.exception(f"Activity analysis error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze activities'
        }), 500


# -----------------------------
# AI-Powered Farming Assistant Endpoints
# -----------------------------

@app.route('/api/enhanced-farmer-profile', methods=['GET'])
def get_enhanced_farmer_profile():
    """Get comprehensive farmer profile with AI insights"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get basic farmer data
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        if not farm_profile_service:
            # Return basic profile if enhanced services not available
            return jsonify({
                'success': True,
                'profile': farmer,
                'enhanced': False,
                'message': 'Basic profile only - enhanced AI services not available'
            })
        
        # Get enhanced profile with AI insights
        enhanced_profile = farm_profile_service.get_detailed_farmer_profile(farmer)
        
        return jsonify({
            'success': True,
            'profile': enhanced_profile,
            'enhanced': True
        })
        
    except Exception as e:
        logging.exception(f"Enhanced profile error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get enhanced profile'
        }), 500


@app.route('/api/smart-activity-suggestions', methods=['GET'])
def get_smart_activity_suggestions():
    """Get AI-powered activity suggestions based on farmer context"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        if not smart_activity_tracker:
            return jsonify({
                'success': False,
                'error': 'Enhanced activity tracking not available'
            }), 503
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        # Get enhanced profile for context
        farmer_profile = farm_profile_service.get_detailed_farmer_profile(farmer) if farm_profile_service else farmer
        
        # Get current weather for suggestions
        try:
            from weather_service import get_current_weather
            current_weather = get_current_weather()
        except:
            current_weather = None
        
        # Get intelligent activity suggestions
        suggestions = smart_activity_tracker.get_activity_suggestions(
            farmer_id, farmer_profile, current_weather
        )
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'context': {
                'weather_considered': current_weather is not None,
                'profile_enhanced': farm_profile_service is not None
            }
        })
        
    except Exception as e:
        logging.exception(f"Activity suggestions error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get activity suggestions'
        }), 500


@app.route('/api/personalized-recommendations', methods=['GET'])
def get_personalized_recommendations():
    """Get personalized farming recommendations based on farmer profile and context"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        recommendations = {
            'crop_recommendations': [],
            'activity_suggestions': [],
            'market_insights': [],
            'weather_alerts': [],
            'seasonal_tips': []
        }
        
        if farm_profile_service:
            # Get crop recommendations
            season = request.args.get('season')
            recommendations['crop_recommendations'] = farm_profile_service.get_crop_recommendations(farmer, season)
            
            # Add seasonal tips based on current month
            import datetime
            current_month = datetime.datetime.now().month
            if current_month in [6, 7, 8, 9]:  # Monsoon season
                recommendations['seasonal_tips'].append({
                    'title': 'Monsoon Season Care',
                    'message': 'Focus on drainage, pest control, and disease prevention during monsoon',
                    'malayalam': 'മഴക്കാലത്ത് ഡ്രെയിനേജ്, കീടനിയന്ത്രണം, രോഗപ്രതിരോധം എന്നിവയിൽ ശ്രദ്ധിക്കുക',
                    'priority': 'high'
                })
        
        if smart_activity_tracker:
            # Get activity suggestions
            farmer_profile = farm_profile_service.get_detailed_farmer_profile(farmer) if farm_profile_service else farmer
            
            try:
                from weather_service import get_current_weather
                current_weather = get_current_weather()
            except:
                current_weather = None
            
            activity_suggestions = smart_activity_tracker.get_activity_suggestions(
                farmer_id, farmer_profile, current_weather
            )
            recommendations['activity_suggestions'] = activity_suggestions[:5]  # Top 5
        
        # Add market insights
        try:
            from market_service import get_kerala_market_prices
            market_data = get_kerala_market_prices(limit=5)
            if market_data:
                recommendations['market_insights'] = [{
                    'type': 'price_update',
                    'message': f'Current market prices available for {len(market_data)} crops',
                    'action': 'Check marketplace for detailed pricing'
                }]
        except:
            pass
        
        # Add weather alerts
        try:
            from weather_service import get_weather_forecast
            forecast = get_weather_forecast()
            if forecast and forecast.get('forecast'):
                tomorrow = forecast['forecast'][0] if forecast['forecast'] else {}
                if 'rain' in tomorrow.get('condition', '').lower():
                    recommendations['weather_alerts'].append({
                        'type': 'rain_alert',
                        'message': 'Rain expected tomorrow. Plan indoor activities.',
                        'malayalam': 'നാളെ മഴ പ്രതീക്ഷിക്കുന്നു. ഇൻഡോർ പ്രവർത്തനങ്ങൾ ആസൂത്രണം ചെയ്യുക.',
                        'priority': 'medium'
                    })
        except:
            pass
        
        # Count total recommendations
        total_count = sum(len(v) if isinstance(v, list) else 1 for v in recommendations.values())
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total_count': total_count,
            'enhanced_services': {
                'profile_service': farm_profile_service is not None,
                'activity_tracker': smart_activity_tracker is not None
            }
        })
        
    except Exception as e:
        logging.exception(f"Personalized recommendations error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate recommendations'
        }), 500


@app.route('/api/smart-reminders', methods=['GET'])
def get_smart_reminders():
    """Get comprehensive smart reminders and alerts for the farmer"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get farmer profile
        farmer = get_farmer_by_id(farmer_id)
        if not farmer:
            return jsonify({
                'success': False,
                'error': 'Farmer not found'
            }), 404
        
        current_date = datetime.datetime.now()
        all_reminders = {
            'urgent': [],
            'important': [],
            'general': [],
            'weather_alerts': [],
            'market_alerts': [],
            'seasonal_reminders': [],
            'activity_reminders': []
        }
        
        # Weather-based reminders
        try:
            from weather_service import get_current_weather, get_weather_forecast
            current_weather = get_current_weather()
            forecast = get_weather_forecast()
            
            if current_weather:
                temp = current_weather.get('temperature', 0)
                condition = current_weather.get('condition', '').lower()
                
                # High temperature alerts
                if temp > 35:
                    all_reminders['weather_alerts'].append({
                        'id': 'high_temp',
                        'title': 'Extreme Heat Alert',
                        'message': f'Temperature is {temp}°C. Increase irrigation frequency and provide shade to crops.',
                        'malayalam': f'താപനില {temp}°C ആണ്. ജലസേചനം വർദ്ധിപ്പിക്കുകയും വിളകൾക്ക് തണൽ നൽകുകയും ചെയ്യുക.',
                        'priority': 'urgent',
                        'type': 'weather',
                        'action_required': True,
                        'expires_at': (current_date + datetime.timedelta(hours=6)).isoformat()
                    })
                
                # Rain alerts
                if 'rain' in condition or 'storm' in condition:
                    all_reminders['weather_alerts'].append({
                        'id': 'rain_alert',
                        'title': 'Rain/Storm Alert',
                        'message': 'Rainy conditions detected. Avoid spraying and ensure proper drainage.',
                        'malayalam': 'മഴയുള്ള അവസ്ഥ കണ്ടെത്തി. തളിക്കുന്നത് ഒഴിവാക്കുകയും ഉചിതമായ ഡ്രെയിനേജ് ഉറപ്പാക്കുകയും ചെയ്യുക.',
                        'priority': 'important',
                        'type': 'weather',
                        'action_required': True
                    })
            
            # Forecast-based alerts
            if forecast and forecast.get('forecast'):
                tomorrow = forecast['forecast'][0] if forecast['forecast'] else {}
                if 'rain' in tomorrow.get('condition', '').lower():
                    all_reminders['weather_alerts'].append({
                        'id': 'rain_tomorrow',
                        'title': 'Rain Expected Tomorrow',
                        'message': 'Plan indoor activities. Postpone fertilizer application and spraying.',
                        'malayalam': 'നാളെ മഴ പ്രതീക്ഷിക്കുന്നു. ഇൻഡോർ പ്രവർത്തനങ്ങൾ ആസൂത്രണം ചെയ്യുക. രാസവള പ്രയോഗവും തളിക്കലും മാറ്റിവയ്ക്കുക.',
                        'priority': 'important',
                        'type': 'weather_forecast',
                        'scheduled_for': (current_date + datetime.timedelta(days=1)).isoformat()
                    })
        except Exception as e:
            logging.warning(f"Weather reminders error: {e}")
        
        # Market-based reminders
        try:
            from market_service import get_kerala_market_prices
            market_data = get_kerala_market_prices(limit=20)
            
            if market_data:
                # Check for farmer's crop prices
                farmer_crops = farmer.get('crops', ['rice', 'coconut'])
                relevant_prices = [item for item in market_data if any(crop.lower() in item.get('crop', '').lower() for crop in farmer_crops)]
                
                if relevant_prices:
                    high_price_crops = [item for item in relevant_prices if item.get('price', 0) > item.get('average_price', 0) * 1.1]
                    
                    if high_price_crops:
                        crop_names = ', '.join([item['crop'] for item in high_price_crops[:3]])
                        all_reminders['market_alerts'].append({
                            'id': 'high_prices',
                            'title': 'Favorable Market Prices',
                            'message': f'Good selling opportunity for {crop_names}. Prices are above average.',
                            'malayalam': f'{crop_names} വിൽക്കാനുള്ള നല്ല അവസരം. വിലകൾ ശരാശരിയിൽ കൂടുതലാണ്.',
                            'priority': 'important',
                            'type': 'market_opportunity',
                            'action_required': True
                        })
        except Exception as e:
            logging.warning(f"Market reminders error: {e}")
        
        # Seasonal reminders based on current month
        current_month = current_date.month
        seasonal_activities = {
            1: ('Winter crop care', 'ശീതകാല വിള പരിചരണം'),  # January
            2: ('Land preparation for summer crops', 'വേനൽക്കാല വിളകൾക്കായുള്ള ഭൂമി തയ്യാറാക്കൽ'),  # February
            3: ('Summer irrigation planning', 'വേനൽക്കാല ജലസേചന ആസൂത്രണം'),  # March
            4: ('Pre-monsoon preparations', 'മഴക്കാലത്തിനു മുമ്പുള്ള തയ്യാറെടുപ്പുകൾ'),  # April
            5: ('Monsoon crop planning', 'മഴക്കാല വിള ആസൂത്രണം'),  # May
            6: ('Kharif season begins', 'ഖരീഫ് സീസൺ ആരംഭം'),  # June
            7: ('Monsoon management', 'മഴക്കാല പരിപാലനം'),  # July
            8: ('Pest monitoring during monsoon', 'മഴക്കാലത്തെ കീട നിരീക്ഷണം'),  # August
            9: ('Post-monsoon activities', 'മഴക്കാലത്തിനു ശേഷമുള്ള പ്രവർത്തനങ്ങൾ'),  # September
            10: ('Rabi season preparation', 'റാബി സീസൺ തയ്യാറെടുപ്പ്'),  # October
            11: ('Harvest season activities', 'വിളവെടുപ്പ് കാല പ്രവർത്തനങ്ങൾ'),  # November
            12: ('Year-end planning', 'വർഷാവസാന ആസൂത്രണം')  # December
        }
        
        if current_month in seasonal_activities:
            activity, malayalam = seasonal_activities[current_month]
            all_reminders['seasonal_reminders'].append({
                'id': f'seasonal_{current_month}',
                'title': f'Seasonal Activity: {activity}',
                'message': f'Focus on {activity.lower()} activities this month.',
                'malayalam': f'ഈ മാസം {malayalam} പ്രവർത്തനങ്ങളിൽ ശ്രദ്ധ കേന്ദ്രീകരിക്കുക.',
                'priority': 'general',
                'type': 'seasonal',
                'month': current_month
            })
        
        # Activity-based reminders from farmer's history
        try:
            activities = read_json_file(ACTIVITIES_FILE)
            farmer_activities = [a for a in activities if a.get('farmer_id') == farmer_id]
            
            if farmer_activities:
                # Check for overdue activities
                last_activity_date = max(activity.get('created_at', '0') for activity in farmer_activities)
                last_date = datetime.datetime.fromisoformat(last_activity_date.replace('Z', ''))
                days_since = (current_date - last_date).days
                
                if days_since > 7:
                    all_reminders['activity_reminders'].append({
                        'id': 'activity_logging',
                        'title': 'Activity Logging Reminder',
                        'message': f'It\'s been {days_since} days since your last recorded activity. Keep your farming log updated.',
                        'malayalam': f'നിങ്ങളുടെ അവസാന രേഖപ്പെടുത്തിയ പ്രവർത്തനം മുതൽ {days_since} ദിവസങ്ങൾ കഴിഞ്ഞു. നിങ്ങളുടെ കൃഷി രേഖ അപ്ഡേറ്റ് ചെയ്യുക.',
                        'priority': 'general',
                        'type': 'activity_logging'
                    })
                
                # Analyze activity patterns for suggestions
                activity_types = [a.get('activity_type') for a in farmer_activities[-10:]]  # Last 10 activities
                if 'irrigation' not in activity_types and len(activity_types) > 5:
                    all_reminders['activity_reminders'].append({
                        'id': 'irrigation_reminder',
                        'title': 'Irrigation Check Reminder', 
                        'message': 'Consider checking irrigation needs. No irrigation activities recorded recently.',
                        'malayalam': 'ജലസേചന ആവശ്യങ്ങൾ പരിശോധിക്കുന്നത് പരിഗണിക്കുക. സമീപകാലത്ത് ജലസേചന പ്രവർത്തനങ്ങൾ രേഖപ്പെടുത്തിയിട്ടില്ല.',
                        'priority': 'important',
                        'type': 'irrigation_check'
                    })
                    
        except Exception as e:
            logging.warning(f"Activity reminders error: {e}")
        
        # Government scheme reminders (mock data - in real implementation, integrate with scheme APIs)
        scheme_reminders = [
            {
                'id': 'pm_kisan',
                'title': 'PM-KISAN Registration',
                'message': 'Ensure your PM-KISAN registration is up to date for benefit payments.',
                'malayalam': 'ആനുകൂല്യ പേയ്‌മെന്റുകൾക്കായി നിങ്ങളുടെ PM-KISAN രജിസ്ട്രേഷൻ അപ്ഡേറ്റ് ചെയ്തിട്ടുണ്ടെന്ന് ഉറപ്പാക്കുക.',
                'priority': 'important',
                'type': 'scheme',
                'scheme_name': 'PM-KISAN',
                'deadline': '2024-03-31'
            },
            {
                'id': 'crop_insurance',
                'title': 'Crop Insurance Reminder',
                'message': 'Consider enrolling in crop insurance for protection against natural calamities.',
                'malayalam': 'പ്രകൃതി ദുരന്തങ്ങളിൽ നിന്നുള്ള സംരക്ഷണത്തിനായി വിള ഇൻഷുറൻസിൽ ചേരുന്നത് പരിഗണിക്കുക.',
                'priority': 'general',
                'type': 'insurance',
                'scheme_name': 'PMFBY'
            }
        ]
        
        all_reminders['general'].extend(scheme_reminders)
        
        # Categorize reminders by priority
        for category, reminders in all_reminders.items():
            if category not in ['urgent', 'important', 'general']:
                for reminder in reminders:
                    priority = reminder.get('priority', 'general')
                    if priority == 'urgent':
                        all_reminders['urgent'].append(reminder)
                    elif priority == 'important':
                        all_reminders['important'].append(reminder)
                    else:
                        all_reminders['general'].append(reminder)
        
        # Calculate summary stats
        total_reminders = sum(len(reminders) for reminders in all_reminders.values())
        urgent_count = len(all_reminders['urgent'])
        important_count = len(all_reminders['important'])
        
        return jsonify({
            'success': True,
            'reminders': all_reminders,
            'summary': {
                'total_count': total_reminders,
                'urgent_count': urgent_count,
                'important_count': important_count,
                'categories': {
                    'weather': len(all_reminders['weather_alerts']),
                    'market': len(all_reminders['market_alerts']),
                    'seasonal': len(all_reminders['seasonal_reminders']),
                    'activity': len(all_reminders['activity_reminders'])
                }
            },
            'last_updated': current_date.isoformat()
        })
        
    except Exception as e:
        logging.exception(f"Smart reminders error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get reminders'
        }), 500


@app.route('/api/dismiss-reminder', methods=['POST'])
def dismiss_reminder():
    """Mark a reminder as dismissed"""
    try:
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.json or {}
        reminder_id = data.get('reminder_id')
        
        if not reminder_id:
            return jsonify({
                'success': False,
                'error': 'reminder_id is required'
            }), 400
        
        # In a real implementation, save dismissed reminders to prevent repeated notifications
        # For now, just return success
        
        return jsonify({
            'success': True,
            'message': 'Reminder dismissed successfully'
        })
        
    except Exception as e:
        logging.exception(f"Dismiss reminder error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to dismiss reminder'
        }), 500


# -----------------------------
# System Health Check Endpoint
# -----------------------------
@app.route('/api/health-check', methods=['GET'])
def system_health_check():
    """System health and service status check"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'services': {
            'enhanced_farm_profiling': farm_profile_service is not None,
            'smart_activity_tracking': smart_activity_tracker is not None,
            'ai_services': ENHANCED_SERVICES_AVAILABLE
        },
        'timestamp': datetime.datetime.now().isoformat()
    })


# -----------------------------
# Plant Disease Detection Endpoint
# -----------------------------
@app.route('/api/detect-plant-disease', methods=['POST', 'OPTIONS'])
def detect_plant_disease():
    """Enhanced plant disease detection with Gemini AI analysis"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check if user is authenticated
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Get language preference
        language = request.form.get('language', 'en')  # 'en' or 'ml'
        
        # Check if image file was uploaded
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No image file selected'
            }), 400
        
        try:
            # Import here to avoid startup errors if transformers not installed
            from transformers import pipeline
            from PIL import Image
            import io
            import base64
            
            # Load the model pipeline
            pipe = pipeline(
                "image-classification", 
                model="linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"
            )
            
            # Load and process image
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Run classification
            results = pipe(image)
            
            # Get top result for detailed analysis
            top_result = results[0] if results else None
            
            if not top_result:
                return jsonify({
                    'success': False,
                    'error': 'Unable to analyze the image'
                }), 400
            
            # Enhanced analysis with Gemini AI
            disease_analysis = get_enhanced_disease_analysis(
                top_result['label'], 
                top_result['score'], 
                language
            )
            
            # Format results
            formatted_results = []
            for result in results[:3]:  # Top 3 results
                formatted_results.append({
                    'name': result['label'],
                    'confidence': round(result['score'] * 100, 2),
                    'description': f"Detected {result['label']} with {round(result['score'] * 100, 1)}% confidence"
                })
            
            # Store image for PDF generation
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Generate comprehensive response
            response_data = {
                'primary_detection': {
                    'name': top_result['label'],
                    'confidence': round(top_result['score'] * 100, 2),
                    'scientific_name': disease_analysis.get('scientific_name', ''),
                    'severity': disease_analysis.get('severity', 'Unknown')
                },
                'all_results': formatted_results,
                'detailed_analysis': disease_analysis.get('detailed_analysis', ''),
                'symptoms': disease_analysis.get('symptoms', []),
                'causes': disease_analysis.get('causes', []),
                'treatment': disease_analysis.get('treatment', {}),
                'pesticide_recommendations': disease_analysis.get('pesticides', []),
                'prevention_tips': disease_analysis.get('prevention', []),
                'organic_solutions': disease_analysis.get('organic_solutions', []),
                'when_to_treat': disease_analysis.get('when_to_treat', ''),
                'follow_up_care': disease_analysis.get('follow_up_care', ''),
                'language': language,
                'image_data': image_base64  # For PDF generation
            }
            
            return jsonify({
                'success': True,
                'results': response_data
            })
            
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'Plant disease detection service not available. Please install required packages.'
            }), 503
            
    except Exception as e:
        logging.exception(f"Plant disease detection error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze image'
        }), 500


def get_enhanced_disease_analysis(disease_name: str, confidence: float, language: str = 'en') -> Dict[str, Any]:
    """Get enhanced disease analysis using Gemini AI"""
    try:
        if not model:
            return get_fallback_disease_analysis(disease_name, language)
        
        # Create comprehensive prompt for disease analysis
        prompt = create_disease_analysis_prompt(disease_name, confidence, language)
        
        generation_config = genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=2048,
            top_p=0.8,
            top_k=40
        )
        
        response = model.generate_content(prompt, generation_config=generation_config)
        
        # Parse the structured response
        analysis = parse_disease_analysis_response(response.text, language)
        return analysis
        
    except Exception as e:
        logging.exception(f"Gemini disease analysis error: {e}")
        return get_fallback_disease_analysis(disease_name, language)


def create_disease_analysis_prompt(disease_name: str, confidence: float, language: str) -> str:
    """Create a comprehensive prompt for disease analysis"""
    lang_instruction = "Respond in Malayalam" if language == 'ml' else "Respond in English"
    
    return f"""
You are an expert plant pathologist and agricultural advisor specializing in crop diseases in Kerala, India. 
Analyze the detected plant disease and provide comprehensive information.

DETECTED DISEASE: {disease_name}
CONFIDENCE: {confidence:.2f}

{lang_instruction}. Provide your response in the following JSON structure:

{{
    "scientific_name": "Scientific name of the disease/pathogen",
    "severity": "Low/Medium/High based on the detection",
    "detailed_analysis": "Detailed explanation of the disease (2-3 sentences)",
    "symptoms": ["List of visible symptoms", "Another symptom"],
    "causes": ["Environmental factors", "Pathogen information", "Contributing conditions"],
    "treatment": {{
        "immediate_action": "What to do immediately",
        "short_term": "Treatment for next 1-2 weeks", 
        "long_term": "Long-term management strategy"
    }},
    "pesticides": [
        {{
            "name": "Pesticide name",
            "type": "Fungicide/Bactericide/Insecticide",
            "dosage": "Application rate",
            "method": "How to apply",
            "timing": "When to apply",
            "precautions": "Safety measures"
        }}
    ],
    "organic_solutions": ["Neem oil application", "Copper sulfate spray", "Other organic treatments"],
    "prevention": ["Prevention tip 1", "Prevention tip 2"],
    "when_to_treat": "Best time of day/weather for treatment",
    "follow_up_care": "What to monitor after treatment"
}}

Focus on treatments and pesticides commonly available in Kerala. Include both chemical and organic solutions.
Be specific about dosages, application methods, and safety precautions.
"""


def parse_disease_analysis_response(response_text: str, language: str) -> Dict[str, Any]:
    """Parse Gemini response into structured format"""
    try:
        # Try to extract JSON from the response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            analysis = json.loads(json_str)
            return analysis
    except Exception as e:
        logging.warning(f"Failed to parse JSON response: {e}")
    
    # Fallback to text parsing if JSON fails
    return parse_text_response(response_text, language)


def parse_text_response(response_text: str, language: str) -> Dict[str, Any]:
    """Parse plain text response into structured format"""
    # Basic text parsing - extract key information
    lines = response_text.split('\n')
    
    return {
        'scientific_name': 'Analysis from AI',
        'severity': 'Medium',
        'detailed_analysis': response_text[:200] + '...' if len(response_text) > 200 else response_text,
        'symptoms': ['Check the detailed analysis for symptoms'],
        'causes': ['Environmental factors', 'Pathogen infection'],
        'treatment': {
            'immediate_action': 'Remove affected parts',
            'short_term': 'Apply recommended treatments',
            'long_term': 'Monitor and prevent reoccurrence'
        },
        'pesticides': [{
            'name': 'Copper-based fungicide',
            'type': 'Fungicide',
            'dosage': '2-3ml per liter',
            'method': 'Foliar spray',
            'timing': 'Early morning or evening',
            'precautions': 'Wear protective equipment'
        }],
        'organic_solutions': ['Neem oil spray', 'Baking soda solution'],
        'prevention': ['Improve air circulation', 'Avoid overhead watering'],
        'when_to_treat': 'Early morning or late evening',
        'follow_up_care': 'Monitor for 7-10 days and repeat if necessary'
    }


def get_fallback_disease_analysis(disease_name: str, language: str) -> Dict[str, Any]:
    """Fallback analysis when Gemini is not available"""
    is_malayalam = language == 'ml'
    
    fallback_data = {
        'en': {
            'scientific_name': f'{disease_name} (AI Detection)',
            'severity': 'Medium',
            'detailed_analysis': f'The AI has detected {disease_name} in your plant. This requires immediate attention to prevent spread.',
            'symptoms': ['Visible lesions or spots', 'Discoloration of leaves', 'Wilting or stunted growth'],
            'causes': ['Fungal/bacterial infection', 'Poor air circulation', 'Excess moisture'],
            'treatment': {
                'immediate_action': 'Remove and destroy affected plant parts',
                'short_term': 'Apply copper-based fungicide spray',
                'long_term': 'Improve growing conditions and monitor regularly'
            },
            'pesticides': [{
                'name': 'Copper Oxychloride',
                'type': 'Fungicide',
                'dosage': '2-3 grams per liter',
                'method': 'Foliar spray',
                'timing': 'Early morning or evening',
                'precautions': 'Wear gloves and mask during application'
            }],
            'organic_solutions': ['Neem oil spray (5ml/L)', 'Baking soda solution (5g/L)', 'Garlic-chili spray'],
            'prevention': ['Ensure good air circulation', 'Avoid overhead watering', 'Remove plant debris'],
            'when_to_treat': 'Early morning (6-8 AM) or late evening (5-7 PM)',
            'follow_up_care': 'Monitor daily for 7-10 days and repeat treatment if necessary'
        },
        'ml': {
            'scientific_name': f'{disease_name} (AI കണ്ടെത്തൽ)',
            'severity': 'ഇടത്തരം',
            'detailed_analysis': f'AI നിങ്ങളുടെ ചെടിയിൽ {disease_name} കണ്ടെത്തിയിട്ടുണ്ട്. വ്യാപനം തടയാൻ ഉടനടി ശ്രദ്ധ ആവശ്യമാണ്.',
            'symptoms': ['ദൃശ്യമായ പാടുകൾ', 'ഇലകളുടെ നിറവ്യത്യാസം', 'വാടൽ അല്ലെങ്കിൽ വളർച്ച മുരടിപ്പ്'],
            'causes': ['ഫംഗസ്/ബാക്ടീരിയ അണുബാധ', 'മോശം വായു സഞ്ചാരം', 'അധിക ഈർപ്പം'],
            'treatment': {
                'immediate_action': 'ബാധിച്ച ഭാഗങ്ങൾ നീക്കം ചെയ്ത് നശിപ്പിക്കുക',
                'short_term': 'കോപ്പർ അടിസ്ഥാനത്തിലുള്ള ഫംഗിസൈഡ് സ്പ്രേ ചെയ്യുക',
                'long_term': 'വളർത്തൽ സാഹചര്യങ്ങൾ മെച്ചപ്പെടുത്തി പതിവായി നിരീക്ഷിക്കുക'
            },
            'pesticides': [{
                'name': 'കോപ്പർ ഓക്സിക്ലോറൈഡ്',
                'type': 'ഫംഗിസൈഡ്',
                'dosage': 'ലിറ്ററിന് 2-3 ഗ്രാം',
                'method': 'ഇല സ്പ്രേ',
                'timing': 'അതിരാവിലെ അല്ലെങ്കിൽ വൈകുന്നേരം',
                'precautions': 'പ്രയോഗസമയത്ത് കയ്യുറയും മാസ്കും ധരിക്കുക'
            }],
            'organic_solutions': ['വേപ്പെണ്ണ സ്പ്രേ (5ml/L)', 'ബേക്കിംഗ് സോഡ ലായനി (5g/L)', 'വെളുത്തുള്ളി-മുളക് സ്പ്രേ'],
            'prevention': ['നല്ല വായു സഞ്ചാരം ഉറപ്പാക്കുക', 'മുകളിൽ നിന്ന് വെള്ളം ഒഴിക്കുന്നത് ഒഴിവാക്കുക', 'ചെടിയുടെ അവശിഷ്ടങ്ങൾ നീക്കം ചെയ്യുക'],
            'when_to_treat': 'അതിരാവിലെ (6-8 AM) അല്ലെങ്കിൽ വൈകുന്നേരം (5-7 PM)',
            'follow_up_care': '7-10 ദിവസം ദിവസേന നിരീക്ഷിക്കുക, ആവശ്യമെങ്കിൽ ചികിത്സ ആവർത്തിക്കുക'
        }
    }
    
    return fallback_data[language] if is_malayalam else fallback_data['en']


# -----------------------------
# PDF Report Generation Endpoint
# -----------------------------
@app.route('/api/generate-disease-report', methods=['POST', 'OPTIONS'])
def generate_disease_report():
    """Generate PDF report for plant disease analysis"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check if user is authenticated
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.json or {}
        analysis_data = data.get('analysis_data', {})
        language = data.get('language', 'en')
        
        if not analysis_data:
            return jsonify({
                'success': False,
                'error': 'Analysis data required'
            }), 400
        
        # Generate PDF
        pdf_buffer = generate_disease_pdf_report(analysis_data, language, farmer_id)
        
        # Return PDF file
        filename = f"plant_disease_report_{farmer_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        return send_file(
            BytesIO(pdf_buffer.getvalue()),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        logging.exception(f"PDF generation error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate PDF report'
        }), 500


def generate_disease_pdf_report(analysis_data: Dict[str, Any], language: str, farmer_id: str) -> BytesIO:
    """Generate PDF report for plant disease analysis"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_text = "Plant Disease Analysis Report" if language == 'en' else "സസ്യരോഗ വിശകലന റിപ്പോർട്ട്"
    title = Paragraph(title_text, styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Farmer info
    farmer_info = f"Farmer ID: {farmer_id}\nDate: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    if language == 'ml':
        farmer_info = f"കർഷക ID: {farmer_id}\nതീയതി: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    story.append(Paragraph(farmer_info, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Detection results
    detection = analysis_data.get('primary_detection', {})
    if detection:
        header = "Disease Detection Results" if language == 'en' else "രോഗ കണ്ടെത്തൽ ഫലങ്ങൾ"
        story.append(Paragraph(header, styles['Heading2']))
        
        detection_text = f"Disease: {detection.get('name', 'Unknown')}\n"
        detection_text += f"Confidence: {detection.get('confidence', 0)}%\n"
        detection_text += f"Scientific Name: {detection.get('scientific_name', 'N/A')}\n"
        detection_text += f"Severity: {detection.get('severity', 'Unknown')}"
        
        if language == 'ml':
            detection_text = f"രോഗം: {detection.get('name', 'അജ്ഞാതം')}\n"
            detection_text += f"ആത്മവിശ്വാസം: {detection.get('confidence', 0)}%\n"
            detection_text += f"ശാസ്ത്രീയ നാമം: {detection.get('scientific_name', 'ലഭ്യമല്ല')}\n"
            detection_text += f"തീവ്രത: {detection.get('severity', 'അജ്ഞാതം')}"
        
        story.append(Paragraph(detection_text, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Detailed analysis
    detailed_analysis = analysis_data.get('detailed_analysis', '')
    if detailed_analysis:
        header = "Detailed Analysis" if language == 'en' else "വിശദമായ വിശകലനം"
        story.append(Paragraph(header, styles['Heading2']))
        story.append(Paragraph(detailed_analysis, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Symptoms
    symptoms = analysis_data.get('symptoms', [])
    if symptoms:
        header = "Symptoms" if language == 'en' else "ലക്ഷണങ്ങൾ"
        story.append(Paragraph(header, styles['Heading2']))
        for symptom in symptoms:
            story.append(Paragraph(f"• {symptom}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Treatment recommendations
    treatment = analysis_data.get('treatment', {})
    if treatment:
        header = "Treatment Recommendations" if language == 'en' else "ചികിത്സാ ശുപാർശകൾ"
        story.append(Paragraph(header, styles['Heading2']))
        
        if treatment.get('immediate_action'):
            subheader = "Immediate Action" if language == 'en' else "ഉടനടി നടപടി"
            story.append(Paragraph(subheader, styles['Heading3']))
            story.append(Paragraph(treatment['immediate_action'], styles['Normal']))
        
        if treatment.get('short_term'):
            subheader = "Short-term Treatment" if language == 'en' else "ഹ്രസ്വകാല ചികിത്സ"
            story.append(Paragraph(subheader, styles['Heading3']))
            story.append(Paragraph(treatment['short_term'], styles['Normal']))
        
        if treatment.get('long_term'):
            subheader = "Long-term Management" if language == 'en' else "ദീർഘകാല പരിപാലനം"
            story.append(Paragraph(subheader, styles['Heading3']))
            story.append(Paragraph(treatment['long_term'], styles['Normal']))
        
        story.append(Spacer(1, 12))
    
    # Pesticide recommendations
    pesticides = analysis_data.get('pesticide_recommendations', [])
    if pesticides:
        header = "Pesticide Recommendations" if language == 'en' else "കീടനാശിനി ശുപാർശകൾ"
        story.append(Paragraph(header, styles['Heading2']))
        
        for pesticide in pesticides:
            pest_text = f"Name: {pesticide.get('name', 'N/A')}\n"
            pest_text += f"Type: {pesticide.get('type', 'N/A')}\n"
            pest_text += f"Dosage: {pesticide.get('dosage', 'N/A')}\n"
            pest_text += f"Method: {pesticide.get('method', 'N/A')}\n"
            pest_text += f"Timing: {pesticide.get('timing', 'N/A')}\n"
            pest_text += f"Precautions: {pesticide.get('precautions', 'N/A')}"
            
            story.append(Paragraph(pest_text, styles['Normal']))
            story.append(Spacer(1, 6))
        
        story.append(Spacer(1, 12))
    
    # Organic solutions
    organic = analysis_data.get('organic_solutions', [])
    if organic:
        header = "Organic Solutions" if language == 'en' else "ജൈവ പരിഹാരങ്ങൾ"
        story.append(Paragraph(header, styles['Heading2']))
        for solution in organic:
            story.append(Paragraph(f"• {solution}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Prevention tips
    prevention = analysis_data.get('prevention_tips', [])
    if prevention:
        header = "Prevention Tips" if language == 'en' else "പ്രതിരോധ നുറുങ്ങുകൾ"
        story.append(Paragraph(header, styles['Heading2']))
        for tip in prevention:
            story.append(Paragraph(f"• {tip}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Follow-up care
    follow_up = analysis_data.get('follow_up_care', '')
    if follow_up:
        header = "Follow-up Care" if language == 'en' else "തുടർ പരിചരണം"
        story.append(Paragraph(header, styles['Heading2']))
        story.append(Paragraph(follow_up, styles['Normal']))
    
    # Footer
    footer_text = "Generated by Krishi Sakhi - Kerala Farmer Assistance Platform"
    if language == 'ml':
        footer_text = "കൃഷി സഖി - കേരള കർഷക സഹായ പ്ലാറ്റ്ഫോം സൃഷ്ടിച്ചത്"
    
    story.append(Spacer(1, 24))
    story.append(Paragraph(footer_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


# -----------------------------
# Enhanced Voice Integration Endpoints
# -----------------------------

@app.route('/api/voice/malayalam-speech-to-text', methods=['POST', 'OPTIONS'])
def malayalam_speech_to_malayalam_text_endpoint():
    """Convert Malayalam speech directly to Malayalam text using specialized model"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check authentication
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Check translation service
        global translation_service
        if translation_service is None:
            return jsonify({
                'success': False,
                'error': 'Translation service not available'
            }), 503
        
        # Validate audio file
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Save uploaded file temporarily
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        audio_file.save(temp_audio_path)
        
        try:
            # Convert Malayalam speech to Malayalam text
            malayalam_text = translation_service.malayalam_speech_to_malayalam_text(temp_audio_path)
            
            if malayalam_text:
                return jsonify({
                    'success': True,
                    'malayalam_text': malayalam_text,
                    'method': 'specialized_model'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to convert speech to Malayalam text'
                }), 500
            
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
            except Exception as cleanup_error:
                logging.warning(f"Could not delete temp file: {temp_audio_path}, {cleanup_error}")
            
    except Exception as e:
        logging.exception(f"Malayalam speech to text error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to process Malayalam speech'
        }), 500


@app.route('/api/voice/complete-pipeline', methods=['POST', 'OPTIONS'])
def complete_voice_pipeline():
    """
    Complete voice pipeline: Malayalam speech → English text → Gemini response → Malayalam speech
    This endpoint handles the full voice interaction workflow
    """
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check authentication
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Check translation service
        global translation_service
        if translation_service is None:
            return jsonify({
                'success': False,
                'error': 'Translation service not available'
            }), 503
        
        # Validate audio file
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Save uploaded file temporarily
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_audio_path = temp_audio.name
        temp_audio.close()
        audio_file.save(temp_audio_path)
        
        response_audio_path = None
        
        try:
            # Step 1: Malayalam speech → English text (enhanced)
            english_text = translation_service.speech_to_text(temp_audio_path)
            
            if not english_text:
                return jsonify({
                    'success': False,
                    'error': 'Failed to convert speech to text'
                }), 500
            
            # Step 2: Get Gemini response using existing chat logic
            try:
                if not model:
                    gemini_response = "AI service is currently unavailable. Please try again later."
                else:
                    prompt = create_expert_farming_prompt(english_text, 'en')
                    generation_config = genai.types.GenerationConfig(
                        temperature=0.4,
                        max_output_tokens=1024,
                        top_p=0.9,
                        top_k=35
                    )
                    
                    response = model.generate_content(prompt, generation_config=generation_config)
                    gemini_response = response.text
                
            except Exception as gemini_error:
                logging.error(f"Gemini API error: {gemini_error}")
                return jsonify({
                    'success': False,
                    'error': 'AI service temporarily unavailable',
                    'english_text': english_text
                }), 503
            
            # Step 3: Convert Gemini response to Malayalam speech
            try:
                response_audio_path = translation_service.text_to_speech(gemini_response)
                
                if response_audio_path and os.path.exists(response_audio_path):
                    # Return complete response with audio file
                    return jsonify({
                        'success': True,
                        'farmer_input': english_text,
                        'gemini_response': gemini_response,
                        'audio_response': True,
                        'pipeline_complete': True
                    })
                else:
                    # Return text response only if audio generation fails
                    return jsonify({
                        'success': True,
                        'farmer_input': english_text,
                        'gemini_response': gemini_response,
                        'audio_response': False,
                        'pipeline_complete': False,
                        'note': 'Text-to-speech conversion failed'
                    })
                
            except Exception as tts_error:
                logging.error(f"Text-to-speech error: {tts_error}")
                return jsonify({
                    'success': True,
                    'farmer_input': english_text,
                    'gemini_response': gemini_response,
                    'audio_response': False,
                    'pipeline_complete': False,
                    'note': 'Audio generation failed'
                })
            
        finally:
            # Clean up input temp file
            try:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
            except Exception as cleanup_error:
                logging.warning(f"Could not delete input temp file: {temp_audio_path}, {cleanup_error}")
            
    except Exception as e:
        logging.exception(f"Complete voice pipeline error: {e}")
        return jsonify({
            'success': False,
            'error': 'Voice pipeline processing failed'
        }), 500


@app.route('/api/voice/get-response-audio', methods=['GET'])
def get_response_audio():
    """Get the latest generated Malayalam audio response"""
    try:
        # Check authentication
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # This endpoint would need session management to track the latest audio file
        # For now, we'll integrate this into the complete pipeline endpoint
        return jsonify({
            'success': False,
            'error': 'Use complete-pipeline endpoint for audio responses'
        }), 400
        
    except Exception as e:
        logging.exception(f"Get response audio error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve audio response'
        }), 500


# -----------------------------
# Original Translation Endpoints (Enhanced)
# -----------------------------
@app.route('/api/translate-speech-to-text', methods=['POST', 'OPTIONS'])
def translate_speech_to_text():
    """Convert Malayalam speech to English text"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check if user is authenticated
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Check if translation service is available
        global translation_service
        if translation_service is None:
            return jsonify({
                'success': False,
                'error': 'Translation service not available. Please install required packages.'
            }), 503
        
        # Check if audio file was uploaded
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No audio file selected'
            }), 400
        
        # Save uploaded file temporarily - use webm format which is common for browser recordings
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        temp_audio_path = temp_audio.name
        temp_audio.close()  # Close file handle before saving
        audio_file.save(temp_audio_path)
        
        try:
            # Convert speech to text
            english_text = translation_service.speech_to_text(temp_audio_path)
            
            return jsonify({
                'success': True,
                'english_text': english_text
            })
            
        finally:
            # Clean up temp file - use try/except for Windows file locking issues
            try:
                if os.path.exists(temp_audio_path):
                    os.unlink(temp_audio_path)
            except PermissionError:
                # On Windows, file might still be locked, try again after a short delay
                import time
                time.sleep(0.1)
                try:
                    os.unlink(temp_audio_path)
                except:
                    logging.warning(f"Could not delete temp file: {temp_audio_path}")
            
    except Exception as e:
        logging.exception(f"Speech to text error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to convert speech to text'
        }), 500


@app.route('/api/translate-text-to-speech', methods=['POST', 'OPTIONS'])
def translate_text_to_speech():
    """Convert English text to Malayalam speech"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Check if user is authenticated
        farmer_id = session.get('farmer_id')
        if not farmer_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        # Check if translation service is available
        global translation_service
        if translation_service is None:
            return jsonify({
                'success': False,
                'error': 'Translation service not available. Please install required packages.'
            }), 503
        
        data = request.json or {}
        english_text = data.get('text', '').strip()
        
        if not english_text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        try:
            # Convert text to speech
            audio_file_path = translation_service.text_to_speech(english_text)
            
            # Return audio file
            return send_file(
                audio_file_path,
                as_attachment=True,
                download_name='malayalam_speech.mp3',
                mimetype='audio/mpeg'
            )
            
        except Exception as e:
            logging.exception(f"Text to speech conversion failed: {e}")
            # Clean up any temp files
            try:
                translation_service.cleanup_temp_file(audio_file_path)
            except:
                pass
            raise
            
    except Exception as e:
        logging.exception(f"Text to speech error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to convert text to speech'
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)