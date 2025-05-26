from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import json
import os
from datetime import datetime, timedelta
from supabase import create_client, Client
import re
from openai import OpenAI
from functools import wraps
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change this in production

# Configuration - Using GitHub's AI API
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_ENDPOINT = "https://models.github.ai/inference"

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize OpenAI client for GitHub AI
client = OpenAI(
    base_url=GITHUB_ENDPOINT,
    api_key=GITHUB_TOKEN,
)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# User authentication functions
def register_user(username, password, email):
    try:
        # Check if username already exists
        result = supabase.table('users').select('*').eq('username', username).execute()
        if result.data:
            return False, "Username already exists"
        
        # Check if email already exists
        result = supabase.table('users').select('*').eq('email', email).execute()
        if result.data:
            return False, "Email already exists"
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create new user
        user_data = {
            'username': username,
            'password': hashed_password.decode('utf-8'),
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data and len(result.data) > 0:
            return True, result.data[0]['id']
        else:
            return False, "Failed to create user"
            
    except Exception as e:
        print(f"Registration error: {str(e)}")  # Add logging
        return False, str(e)

def verify_user(username, password):
    try:
        # Get user by username
        result = supabase.table('users').select('*').eq('username', username).execute()
        
        if not result.data:
            return False, "User not found"
        
        user = result.data[0]
        
        # Verify password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return True, user
        return False, "Invalid password"
    except Exception as e:
        return False, str(e)

# Routes for authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        success, result = verify_user(username, password)
        
        if success:
            session['user_id'] = result['id']
            session['username'] = result['username']
            return redirect(url_for('index'))
        else:
            flash(result, 'error')
    
    return r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - AI Calorie Tracker</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #f6f8fd 0%, #f1f4f9 100%);
            }
            .glass-effect {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
            }
            .card-hover {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
            }
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body class="min-h-screen gradient-bg flex items-center justify-center p-4">
        <div class="max-w-md w-full">
            <div class="glass-effect rounded-2xl p-8 card-hover fade-in">
                <div class="text-center mb-8">
                    <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4 shadow-lg">
                        <i class="fas fa-utensils"></i>
                    </div>
                    <h1 class="text-3xl font-bold text-gray-800 mb-2">Welcome Back</h1>
                    <p class="text-gray-500">Sign in to continue tracking your nutrition</p>
                </div>
                
                <form method="POST" class="space-y-6">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-user text-gray-400"></i>
                                </div>
                                <input type="text" name="username" required
                                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50"
                                    placeholder="Enter your username">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-lock text-gray-400"></i>
                                </div>
                                <input type="password" name="password" required
                                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50"
                                    placeholder="Enter your password">
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit"
                        class="w-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white font-medium py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-[1.02]">
                        <i class="fas fa-sign-in-alt mr-2"></i>
                        Sign In
                    </button>
                </form>
                
                <div class="mt-8 text-center">
                    <p class="text-gray-500">Don't have an account? 
                        <a href="/register" class="text-blue-500 hover:text-blue-600 font-medium transition-colors duration-200">Create Account</a>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        success, result = register_user(username, password, email)
        
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result, 'error')
    
    return r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Register - AI Calorie Tracker</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #f6f8fd 0%, #f1f4f9 100%);
            }
            .glass-effect {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
            }
            .card-hover {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
            }
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body class="min-h-screen gradient-bg flex items-center justify-center p-4">
        <div class="max-w-md w-full">
            <div class="glass-effect rounded-2xl p-8 card-hover fade-in">
                <div class="text-center mb-8">
                    <div class="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold mx-auto mb-4 shadow-lg">
                        <i class="fas fa-user-plus"></i>
                    </div>
                    <h1 class="text-3xl font-bold text-gray-800 mb-2">Create Account</h1>
                    <p class="text-gray-500">Join our nutrition tracking community</p>
                </div>
                
                <form method="POST" class="space-y-6">
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Username</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-user text-gray-400"></i>
                                </div>
                                <input type="text" name="username" required
                                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50"
                                    placeholder="Choose a username">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Email</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-envelope text-gray-400"></i>
                                </div>
                                <input type="email" name="email" required
                                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50"
                                    placeholder="Enter your email">
                            </div>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Password</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <i class="fas fa-lock text-gray-400"></i>
                                </div>
                                <input type="password" name="password" required
                                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 bg-white/50"
                                    placeholder="Create a password">
                            </div>
                        </div>
                    </div>
                    
                    <button type="submit"
                        class="w-full bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white font-medium py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-[1.02]">
                        <i class="fas fa-user-plus mr-2"></i>
                        Create Account
                    </button>
                </form>
                
                <div class="mt-8 text-center">
                    <p class="text-gray-500">Already have an account? 
                        <a href="/login" class="text-blue-500 hover:text-blue-600 font-medium transition-colors duration-200">Sign In</a>
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Available models
AVAILABLE_MODELS = {
    "microsoft/Phi-4": "Fast Phi-4",
    "mistral-ai/Ministral-3B": "Fastest Ministral-3B",
    "openai/gpt-4.1": "Fast GPT-4.1",
    "deepseek/DeepSeek-R1": "Slowest DeepSeek-R1"
}

def get_model_client(model_name):
    """Get the appropriate client for the selected model"""
    if model_name not in AVAILABLE_MODELS:
        raise ValueError(f"Unsupported model: {model_name}")
    
    return client  # For now, we're using the same client for all models

def extract_json_from_text(text):
    """Extract JSON from text that might contain additional content"""
    try:
        # First try direct JSON parsing
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Try to find JSON after ```json marker
            if '```json' in text:
                json_str = text.split('```json')[1].split('```')[0].strip()
                return json.loads(json_str)
            # Try to find JSON after ``` marker
            elif '```' in text:
                json_str = text.split('```')[1].split('```')[0].strip()
                return json.loads(json_str)
        except:
            pass
        
        try:
            # Try to find JSON array or object in the text
            json_start = text.find('[')
            json_end = text.rfind(']') + 1
            if json_start == -1:
                json_start = text.find('{')
                json_end = text.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return None

def parse_food_entries(response_text):
    """Parse food entries from model response"""
    try:
        # Try to extract JSON from the response
        data = extract_json_from_text(response_text)
        if data and isinstance(data, list):
            # Process each food entry to add multipliers
            processed_entries = []
            for entry in data:
                # Convert quantity to number
                quantity = entry['quantity']
                if isinstance(quantity, str):
                    # Handle common quantity strings
                    if 'bit' in quantity.lower() or 'little' in quantity.lower():
                        quantity = 0.5
                    elif 'half' in quantity.lower():
                        quantity = 0.5
                    elif 'quarter' in quantity.lower():
                        quantity = 0.25
                    else:
                        # Try to extract any numbers from the string
                        numbers = ''.join(filter(str.isdigit, quantity))
                        quantity = float(numbers) if numbers else 1.0
                
                # Calculate total multiplier based on quantity and portion
                portion_multiplier = 1.0
                if entry.get('portion'):
                    portion_multiplier = get_portion_multiplier(entry['portion'])
                
                total_multiplier = float(quantity) * portion_multiplier
                
                processed_entry = {
                    'food': entry['food'],
                    'quantity': float(quantity),
                    'portion': entry.get('portion', 'standard'),
                    'container_multiplier': portion_multiplier,
                    'total_multiplier': total_multiplier,
                    'calories_per_item': float(entry['calories_per_item']),
                    'total_calories': float(entry['total_calories']),
                    'confidence': float(entry.get('confidence', 0.8))
                }
                processed_entries.append(processed_entry)
            return processed_entries
        
        # If JSON parsing fails, try to extract information from text
        food_entries = []
        lines = response_text.split('\n')
        current_food = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for food items
            if '**' in line and ':' in line:
                food_name = line.split('**')[1].split(':')[0].strip()
                if food_name and 'Food Name' in line:
                    current_food = {
                        'food': food_name,
                        'quantity': 1,
                        'portion': 'piece',
                        'calories_per_item': 0,
                        'total_calories': 0,
                        'confidence': 0.8
                    }
                    food_entries.append(current_food)
            
            # Extract quantity
            elif current_food and 'Quantity' in line:
                try:
                    quantity = ''.join(filter(str.isdigit, line))
                    current_food['quantity'] = float(quantity) if quantity else 1.0
                except:
                    pass
            
            # Extract calories
            elif current_food and ('Calories' in line or 'calories' in line):
                try:
                    calories = ''.join(filter(str.isdigit, line))
                    current_food['calories_per_item'] = float(calories) if calories else 0
                    current_food['total_calories'] = current_food['calories_per_item'] * current_food['quantity']
                except:
                    pass
        
        # Process extracted entries to add multipliers
        processed_entries = []
        for entry in food_entries:
            # Calculate total multiplier based on quantity and portion
            portion_multiplier = 1.0
            if entry.get('portion'):
                portion_multiplier = get_portion_multiplier(entry['portion'])
            
            total_multiplier = float(entry['quantity']) * portion_multiplier
            
            processed_entry = {
                'food': entry['food'],
                'quantity': float(entry['quantity']),
                'portion': entry.get('portion', 'standard'),
                'container_multiplier': portion_multiplier,
                'total_multiplier': total_multiplier,
                'calories_per_item': float(entry['calories_per_item']),
                'total_calories': float(entry['total_calories']),
                'confidence': float(entry.get('confidence', 0.8))
            }
            processed_entries.append(processed_entry)
        
        return processed_entries
    except Exception as e:
        print(f"Error parsing food entries: {str(e)}")
        return []

def parse_insights(response_text):
    """Parse insights from model response"""
    try:
        # Try to extract JSON from the response
        data = extract_json_from_text(response_text)
        if data and isinstance(data, dict):
            return data
        
        # If JSON parsing fails, try to extract information from text
        insights = {
            'macro_balance': 'Analyzing your meal composition...',
            'nutrition_gaps': 'Identifying nutritional gaps...',
            'health_score': 75,
            'next_meal': 'Suggesting next meal...'
        }
        
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract health score
            if 'Health Score' in line:
                try:
                    score = int(''.join(filter(str.isdigit, line)))
                    insights['health_score'] = min(max(score, 0), 100)
                except:
                    pass
            
            # Extract macro balance
            elif 'Macro Balance' in line or 'Macro balance' in line:
                insights['macro_balance'] = line.split(':')[-1].strip()
            
            # Extract nutrition gaps
            elif 'Nutrition Gaps' in line or 'Nutrition gaps' in line:
                insights['nutrition_gaps'] = line.split(':')[-1].strip()
            
            # Extract next meal suggestions
            elif 'Next Meal' in line or 'Next meal' in line:
                insights['next_meal'] = line.split(':')[-1].strip()
        
        return insights
    except Exception as e:
        print(f"Error parsing insights: {str(e)}")
        return {
            'macro_balance': 'Analyzing your meal composition...',
            'nutrition_gaps': 'Identifying nutritional gaps...',
            'health_score': 75,
            'next_meal': 'Suggesting next meal...'
        }

def advanced_food_extraction(text, model_client, model_name):
    """AI-powered food and quantity extraction with calorie estimation"""
    logs = []
    logs.append(f"🤖 === AI FOOD DETECTION STARTED WITH {AVAILABLE_MODELS[model_name]} ===")
    logs.append(f"📝 Input text: '{text}'")
    
    try:
        # Prepare the prompt for food detection
        prompt = f"""Analyze this food description and extract all food items with their quantities and estimated calories:
        Description: "{text}"
        
        For each food item, provide:
        1. Food name (in English)
        2. Quantity (number)
        3. Portion size (e.g., bowl, plate, piece)
        4. Estimated calories per item
        
        Consider:
        - Indian and international foods
        - Common portion sizes
        - Typical calorie ranges for each food
        - Multiple items in a single description
        
        Format your response as a JSON array of objects with these keys:
        [
            {{
                "food": "food name",
                "quantity": number,
                "portion": "portion size",
                "calories_per_item": number,
                "total_calories": number,
                "confidence": number (0-1)
            }}
        ]"""
        
        logs.append("\n📝 Generated Prompt for Food Detection:")
        logs.append(f"  {prompt}")
        
        # Call AI API for food detection
        logs.append(f"\n🚀 Sending request to {AVAILABLE_MODELS[model_name]} for food detection...")
        response = model_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in food analysis, specializing in Indian and international cuisine. You can identify food items, estimate portions, and calculate calories accurately."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            top_p=0.95,
            model=model_name
        )
        
        if response and response.choices:
            try:
                generated_text = response.choices[0].message.content
                logs.append("\n✅ AI Response Received:")
                logs.append("  • Raw Response:")
                logs.append(f"    {generated_text}")
                
                # Parse the generated text into structured food entries
                food_entries = parse_food_entries(generated_text)
                
                if food_entries:
                    logs.append("\n📊 Detected Food Items:")
                    for entry in food_entries:
                        logs.append(f"  • {entry['quantity']} {entry['food']} ({entry.get('portion', 'standard')})")
                        logs.append(f"    - Calories per item: {entry['calories_per_item']}")
                        logs.append(f"    - Total calories: {entry['total_calories']}")
                        logs.append(f"    - Confidence: {entry.get('confidence', 0.8):.2f}")
                    
                    logs.append("\n🎯 Food Detection Summary:")
                    logs.append(f"  • Total items detected: {len(food_entries)}")
                    logs.append(f"  • Average confidence: {sum(e.get('confidence', 0.8) for e in food_entries) / len(food_entries):.2f}")
                    
                    return food_entries, logs
                else:
                    logs.append("\n⚠️ No food items detected in response")
                    return [], logs
                    
            except Exception as e:
                logs.append(f"\n⚠️ Response Processing Error: {str(e)}")
                return [], logs
        else:
            logs.append("\n❌ Empty Response Error:")
            logs.append("  • No food items detected")
            return [], logs
            
    except Exception as e:
        logs.append("\n❌ API Error:")
        logs.append(f"  • Error Type: {type(e).__name__}")
        logs.append(f"  • Error Message: {str(e)}")
        return [], logs

def get_portion_multiplier(portion):
    """Convert portion descriptions to calorie multipliers"""
    portion = portion.lower()
    multipliers = {
        'small': 0.7,
        'medium': 1.0,
        'large': 1.3,
        'bowl': 1.5,
        'plate': 2.0,
        'piece': 1.0,
        'slice': 1.0,
        'cup': 1.0,
        'glass': 1.0,
        'serving': 1.0,
        'portion': 1.0,
        'half': 0.5,
        'quarter': 0.25,
        'full': 1.0
    }
    return multipliers.get(portion, 1.0)

def calculate_enhanced_calories(food_entries):
    """Calculate calories with detailed breakdown using AI-detected values"""
    total_calories = 0
    detailed_breakdown = []
    logs = []
    
    logs.append("\n🧮 === CALORIE CALCULATION ===")
    
    for entry in food_entries:
        # Use the AI-provided calories per item
        base_calories = entry['calories_per_item']
        total_multiplier = entry['total_multiplier']
        
        adjusted_calories = int(base_calories * total_multiplier)
        total_calories += adjusted_calories
        
        detailed_breakdown.append({
            'food': entry['food'],
            'base_calories': base_calories,
            'quantity': entry['quantity'],
            'container_multiplier': entry['container_multiplier'],
            'total_multiplier': total_multiplier,
            'total_calories': adjusted_calories,
            'confidence': entry['confidence']
        })
        
        logs.append(f"  • {entry['food']}:")
        logs.append(f"    - Base calories: {base_calories}")
        logs.append(f"    - Multiplier: {total_multiplier:.1f}x")
        logs.append(f"    - Total: {adjusted_calories} cal")
        logs.append(f"    - Confidence: {entry['confidence']:.2f}")
    
    logs.append(f"\n🔥 Total calories: {total_calories}")
    return total_calories, detailed_breakdown, logs

def save_to_database(user_input, food_entries, total_calories, detailed_breakdown):
    """Save calorie entry to Supabase database"""
    logs = []
    
    try:
        data = {
            'user_id': session['user_id'],  # Add user_id to the entry
            'user_input': user_input,
            'food_items': json.dumps([entry['food'] for entry in food_entries]),
            'total_calories': total_calories,
            'detailed_breakdown': json.dumps(detailed_breakdown),
            'created_at': datetime.now().isoformat(),
            'date': datetime.now().date().isoformat()
        }
        
        result = supabase.table('calorie_entries').insert(data).execute()
        logs.append(f"💾 Database save successful: Entry ID {result.data[0]['id']}")
        return True, result.data[0]['id'], logs
    except Exception as e:
        logs.append(f"❌ Database error: {str(e)}")
        return False, None, logs

def delete_entry(entry_id):
    """Delete a calorie entry from database"""
    try:
        # Only delete if the entry belongs to the current user
        result = supabase.table('calorie_entries').delete().eq('id', entry_id).eq('user_id', session['user_id']).execute()
        return True, f"Entry {entry_id} deleted successfully"
    except Exception as e:
        return False, f"Error deleting entry: {str(e)}"

def get_daily_summary(date=None):
    """Get daily calorie summary from database for current user"""
    if not date:
        date = datetime.now().date().isoformat()
    
    try:
        result = supabase.table('calorie_entries').select('*').eq('date', date).eq('user_id', session['user_id']).execute()
        return result.data
    except Exception as e:
        return []

def get_weekly_data():
    """Get weekly calorie data for charts for current user"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)  # Last 7 days
        
        # Get all entries for the week for current user
        result = supabase.table('calorie_entries').select('*').eq('user_id', session['user_id']).gte('date', start_date.isoformat()).lte('date', end_date.isoformat()).execute()
        
        # Group by date and sum calories
        daily_totals = {}
        daily_entries = {}  # Track entries per day
        
        for entry in result.data:
            date = entry['date']
            calories = entry['total_calories']
            daily_totals[date] = daily_totals.get(date, 0) + calories
            daily_entries[date] = daily_entries.get(date, 0) + 1
        
        # Create chart data for last 7 days
        chart_data = []
        total_entries = 0
        for i in range(7):
            date = (start_date + timedelta(days=i)).isoformat()
            chart_data.append({
                'date': date,
                'calories': daily_totals.get(date, 0),
                'entries': daily_entries.get(date, 0),
                'day': (start_date + timedelta(days=i)).strftime('%a')
            })
            total_entries += daily_entries.get(date, 0)
        
        return chart_data, total_entries
    except Exception as e:
        return [], 0

def get_llm_insights(food_entries, total_calories, model_client, model_name):
    """Get AI-powered insights about the food entries using the selected model"""
    logs = []
    logs.append(f"🤖 === AI ANALYSIS STARTED WITH {AVAILABLE_MODELS[model_name]} ===")
    
    try:
        # Log the input data
        logs.append("📊 Input Data:")
        logs.append(f"  • Total Calories: {total_calories}")
        logs.append("  • Food Items:")
        for entry in food_entries:
            logs.append(f"    - {entry['quantity']} {entry['food']} (×{entry['total_multiplier']:.1f} multiplier)")
        
        # Prepare the prompt for the LLM
        food_list = [f"{entry['quantity']} {entry['food']}" for entry in food_entries]
        prompt = f"""Analyze this meal and provide nutrition insights:
        Meal: {', '.join(food_list)}
        Total calories: {total_calories}
        
        Please provide:
        1. Macro balance analysis
        2. Nutrition gaps
        3. Health score (0-100)
        4. Next meal suggestions
        
        Format your response as a JSON object with these keys: macro_balance, nutrition_gaps, health_score, next_meal"""
        
        logs.append("\n📝 Generated Prompt:")
        logs.append(f"  {prompt}")
        
        # Call AI API using the selected model
        logs.append(f"\n🚀 Sending request to {AVAILABLE_MODELS[model_name]}...")
        logs.append(f"  • Model: {model_name}")
        logs.append("  • Parameters:")
        logs.append("    - Temperature: 0.7 (balanced creativity)")
        logs.append("    - Top P: 0.95 (high quality responses)")
        
        response = model_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a nutrition expert AI assistant. Analyze meals and provide detailed nutritional insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            top_p=0.95,
            model=model_name
        )
        
        if response and response.choices:
            try:
                generated_text = response.choices[0].message.content
                logs.append("\n✅ AI Response Received:")
                logs.append("  • Raw Response:")
                logs.append(f"    {generated_text}")
                
                # Parse the generated text into structured insights
                insights = parse_insights(generated_text)
                logs.append("\n📊 Parsed Insights:")
                logs.append(f"  • Macro Balance: {insights.get('macro_balance', 'N/A')}")
                logs.append(f"  • Nutrition Gaps: {insights.get('nutrition_gaps', 'N/A')}")
                logs.append(f"  • Health Score: {insights.get('health_score', 'N/A')}")
                logs.append(f"  • Next Meal: {insights.get('next_meal', 'N/A')}")
                
                # Add analysis summary
                logs.append("\n🎯 Analysis Summary:")
                logs.append(f"  • Health Score: {insights.get('health_score', 75)}/100")
                if insights.get('health_score', 0) >= 80:
                    logs.append("  • Overall Assessment: Excellent meal composition")
                elif insights.get('health_score', 0) >= 60:
                    logs.append("  • Overall Assessment: Good meal composition")
                else:
                    logs.append("  • Overall Assessment: Room for improvement")
                
                return insights, logs
            except Exception as e:
                logs.append(f"\n⚠️ Response Processing Error: {str(e)}")
                return None, logs
        else:
            logs.append("\n❌ Empty Response Error:")
            logs.append("  • No choices returned from AI API")
            logs.append("  • This might indicate an API configuration issue")
            return None, logs
            
    except Exception as e:
        logs.append("\n❌ API Error:")
        logs.append(f"  • Error Type: {type(e).__name__}")
        logs.append(f"  • Error Message: {str(e)}")
        logs.append("  • This might be due to:")
        logs.append("    - Invalid API token")
        logs.append("    - Network connectivity issues")
        logs.append("    - API rate limiting")
        return None, logs

@app.route('/')
@login_required
def index():
    return r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Calorie Tracker Pro</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/js/all.min.js"></script>
        <style>
            .gradient-bg {
                background: linear-gradient(135deg, #f6f8fd 0%, #f1f4f9 100%);
            }
            .glass-effect {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
            }
            .log-container {
                font-family: 'JetBrains Mono', monospace;
                max-height: 400px;
                overflow-y: auto;
            }
            .voice-recording {
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            .card-hover {
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .card-hover:hover {
                transform: translateY(-5px);
                box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.02);
            }
            .fade-in {
                animation: fadeIn 0.5s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .slide-in {
                animation: slideIn 0.5s ease-out;
            }
            @keyframes slideIn {
                from { transform: translateX(-20px); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            .custom-scrollbar::-webkit-scrollbar {
                width: 6px;
            }
            .custom-scrollbar::-webkit-scrollbar-track {
                background: rgba(0, 0, 0, 0.05);
                border-radius: 3px;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 3px;
            }
            .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                background: rgba(0, 0, 0, 0.2);
            }
            .sidebar {
                transition: all 0.3s ease;
                position: sticky;
                top: 0;
                height: 100vh;
                overflow-y: auto;
            }
            .sidebar-tab {
                transition: all 0.2s ease;
                position: relative;
                overflow: hidden;
            }
            .sidebar-tab::before {
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 0;
                background: linear-gradient(90deg, rgba(99, 102, 241, 0.1), rgba(99, 102, 241, 0));
                transition: width 0.3s ease;
            }
            .sidebar-tab:hover::before {
                width: 100%;
            }
            .sidebar-tab.active {
                background: rgba(255, 255, 255, 0.9);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
            }
            .sidebar-tab.active::before {
                width: 100%;
                background: linear-gradient(90deg, rgba(99, 102, 241, 0.2), rgba(99, 102, 241, 0));
            }
            .tab-content {
                display: none;
            }
            .tab-content.active {
                display: block;
                animation: fadeIn 0.3s ease-in;
            }
            .chat-message {
                animation: slideIn 0.3s ease-out;
            }
            .chat-input {
                transition: all 0.2s ease;
            }
            .chat-input:focus {
                box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
            }
            .typing-indicator {
                display: flex;
                align-items: center;
                gap: 4px;
            }
            .typing-indicator span {
                width: 8px;
                height: 8px;
                background: #6366f1;
                border-radius: 50%;
                animation: typing 1s infinite;
            }
            .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
            .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-4px); }
            }
        </style>
    </head>
    <body class="min-h-screen gradient-bg">
        <!-- Header -->
        <div class="bg-white/80 backdrop-blur-md border-b border-white/20 sticky top-0 z-50">
            <div class="max-w-7xl mx-auto px-6 py-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                            <i class="fas fa-utensils"></i>
                        </div>
                        <div>
                            <h1 class="text-2xl font-bold text-gray-800">AI Calorie Tracker</h1>
                            
                        </div>
                    </div>
                    <div class="flex items-center space-x-6">
                        <div class="text-right">
                            <div class="flex items-center justify-end space-x-2 mb-1">
                                <span class="text-sm text-gray-500">Today's Goal</span>
                                <span class="text-sm font-medium text-gray-700" id="todayProgress">0/2000</span>
                            </div>
                            <div class="w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div id="goalProgressBar" class="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500" style="width: 0%"></div>
                            </div>
                        </div>
                        <div class="flex items-center space-x-4">
                            <select id="modelSelect" class="bg-white/50 border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500">
                                <option value="microsoft/Phi-4">Fast Phi-4</option>
                                <option value="mistral-ai/Ministral-3B">Fastest Ministral-3B</option>
                                <option value="openai/gpt-4.1">Fast GPT-4.1</option>
                                <option value="deepseek/DeepSeek-R1">Slowest DeepSeek-R1</option>
                            </select>
                            <button 
                                onclick="resetAllData()"
                                class="bg-red-500/10 hover:bg-red-500/20 text-red-500 px-4 py-2 rounded-lg transition-all duration-200 flex items-center"
                                title="Reset All Data"
                            >
                                <i class="fas fa-trash-alt mr-2"></i>
                                Reset All
                            </button>
                            <a href="/logout" class="w-12 h-12 rounded-full bg-gradient-to-br from-red-400 to-red-500 flex items-center justify-center text-white shadow-lg hover:shadow-xl transition-all duration-200" title="Logout">
                                <i class="fas fa-sign-out-alt"></i>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex">
            <!-- Sidebar -->
            <div class="w-64 glass-effect border-r border-white/20 p-4 sidebar">
                <div class="space-y-2">
                    <button class="sidebar-tab active w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-700 hover:bg-white/50 transition-all duration-200" data-tab="dashboard">
                        <i class="fas fa-chart-line text-blue-500"></i>
                        <span>Dashboard</span>
                    </button>
                    <button class="sidebar-tab w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-700 hover:bg-white/50 transition-all duration-200" data-tab="history">
                        <i class="fas fa-history text-purple-500"></i>
                        <span>History</span>
                    </button>
                    <button class="sidebar-tab w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-gray-700 hover:bg-white/50 transition-all duration-200" data-tab="ai-coach">
                        <i class="fas fa-robot text-green-500"></i>
                        <span>AI Coach</span>
                    </button>
                </div>
            </div>

            <!-- Main Content -->
            <div class="flex-1">
                <!-- Dashboard Tab -->
                <div id="dashboard" class="tab-content active">
                    <div class="max-w-7xl mx-auto px-6 py-8 mb-24">
                        <div class="grid grid-cols-12 gap-6">
                            <!-- Left Column: Input & Analysis -->
                            <div class="col-span-12 lg:col-span-4 space-y-6">
                                <!-- Input Section -->
                                <div class="glass-effect rounded-2xl p-6 card-hover fade-in">
                                    <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <i class="fas fa-microphone-alt mr-2 text-blue-500"></i>
                                        Food Entry
                                    </h2>
                                    
                                    <div class="mb-4">
                                        <textarea 
                                            id="foodInput" 
                                            class="w-full p-4 bg-white/50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all duration-200 resize-none shadow-sm" 
                                            rows="4" 
                                            placeholder="e.g., I had 3 chapati and 2 bowls of dal for lunch..."
                                        ></textarea>
                                    </div>
                                    
                                    <div class="flex gap-3">
                                        <button 
                                            id="processBtn" 
                                            class="flex-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 hover:from-blue-600 hover:via-purple-600 hover:to-pink-600 text-white font-medium py-3 px-6 rounded-xl transition-all duration-300 flex items-center justify-center shadow-lg hover:shadow-xl transform hover:scale-[1.02]"
                                        >
                                            <i class="fas fa-brain mr-2"></i>
                                            Process with AI
                                        </button>
                                        <button 
                                            id="voiceBtn" 
                                            class="bg-gradient-to-r from-green-400 to-blue-500 hover:from-green-500 hover:to-blue-600 text-white font-medium py-3 px-4 rounded-xl transition-all duration-200 shadow-md hover:shadow-lg"
                                            title="Voice Input"
                                        >
                                            <i class="fas fa-microphone"></i>
                                        </button>
                                    </div>
                                </div>

                                <!-- Results Section -->
                                <div id="resultsSection" class="glass-effect rounded-2xl p-6 card-hover slide-in">
                                    <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <i class="fas fa-chart-pie mr-2 text-orange-500"></i>
                                        Analysis Results
                                    </h2>
                                    <div id="resultsContent" class="text-center py-8">
                                        <div class="text-gray-400 mb-2">
                                            <i class="fas fa-utensils text-4xl"></i>
                                        </div>
                                        <p class="text-gray-500">Input your food data to see the analysis</p>
                                    </div>
                                </div>

                                <!-- Health Score -->
                                <div class="glass-effect rounded-2xl p-6 card-hover fade-in">
                                    <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <i class="fas fa-heartbeat mr-2 text-red-500"></i>
                                        Health Score
                                    </h2>
                                    <div id="healthScore" class="text-center">
                                        <div class="relative w-32 h-32 mx-auto mb-4">
                                            <svg class="w-full h-full" viewBox="0 0 100 100">
                                                <circle class="text-gray-200" stroke-width="10" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50"/>
                                                <circle id="healthScoreCircle" class="text-green-500" stroke-width="10" stroke-dasharray="251.2" stroke-dashoffset="125.6" stroke-linecap="round" stroke="currentColor" fill="transparent" r="40" cx="50" cy="50"/>
                                            </svg>
                                            <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
                                                <span class="text-3xl font-bold text-gray-800" id="scoreValue">75</span>
                                                <span class="text-sm text-gray-500">/100</span>
                                            </div>
                                        </div>
                                        <div class="text-sm text-gray-600 mb-4" id="healthScoreDescription">
                                            Your diet is well-balanced with good variety
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Middle Column: Stats & Trends -->
                            <div class="col-span-12 lg:col-span-8 space-y-6">
                                <!-- Quick Stats -->
                                <div class="glass-effect rounded-2xl p-6 card-hover fade-in">
                                    <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <i class="fas fa-chart-line mr-2 text-purple-500"></i>
                                        Quick Stats
                                    </h2>
                                    <div id="quickStats" class="grid grid-cols-3 gap-4">
                                        <div class="bg-gradient-to-br from-blue-50 to-purple-50 p-4 rounded-xl">
                                            <div class="flex items-center justify-between mb-2">
                                                <div class="text-sm text-gray-500">Avg Daily</div>
                                                <i class="fas fa-calendar-day text-blue-500"></i>
                                            </div>
                                            <div class="font-bold text-gray-800 text-xl" id="avgDaily">-</div>
                                            <div class="text-xs text-gray-500 mt-1">calories</div>
                                        </div>
                                        <div class="bg-gradient-to-br from-green-50 to-blue-50 p-4 rounded-xl">
                                            <div class="flex items-center justify-between mb-2">
                                                <div class="text-sm text-gray-500">This Week</div>
                                                <i class="fas fa-chart-line text-green-500"></i>
                                            </div>
                                            <div class="font-bold text-gray-800 text-xl" id="weekTotal">-</div>
                                            <div class="text-xs text-gray-500 mt-1">total calories</div>
                                        </div>
                                        <div class="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-xl">
                                            <div class="flex items-center justify-between mb-2">
                                                <div class="text-sm text-gray-500">Entries</div>
                                                <i class="fas fa-list-check text-purple-500"></i>
                                            </div>
                                            <div class="font-bold text-gray-800 text-xl" id="totalEntries">-</div>
                                            <div class="text-xs text-gray-500 mt-1">this week</div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Weekly Chart -->
                                <div class="glass-effect rounded-2xl p-6 card-hover fade-in">
                                    <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <i class="fas fa-chart-bar mr-2 text-indigo-500"></i>
                                        Weekly Trend
                                    </h2>
                                    <div class="h-80">
                                        <canvas id="weeklyChart" width="800" height="300"></canvas>
                                    </div>
                                </div>

                                <!-- AI Insights & Recommendations -->
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <!-- AI Nutrition Insights -->
                                    <div class="glass-effect rounded-2xl p-6 card-hover fade-in">
                                        <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                            <i class="fas fa-lightbulb mr-2 text-yellow-500"></i>
                                            AI Nutrition Insights
                                        </h2>
                                        <div id="nutritionInsights" class="space-y-3">
                                            <div class="bg-white/50 p-4 rounded-xl">
                                                <div class="flex items-center mb-2">
                                                    <i class="fas fa-seedling text-emerald-500 mr-2"></i>
                                                    <span class="font-medium">Nutrition Gaps</span>
                                                </div>
                                                <div class="text-sm text-gray-600" id="nutritionGaps">Identifying gaps...</div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- AI Meal Recommendations -->
                                    <div class="glass-effect rounded-2xl p-6 card-hover fade-in">
                                        <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                            <i class="fas fa-utensils mr-2 text-pink-500"></i>
                                            AI Meal Recommendations
                                        </h2>
                                        <div id="mealRecommendations" class="space-y-3">
                                            <div class="bg-white/50 p-4 rounded-xl">
                                                <div class="flex items-center mb-2">
                                                    <i class="fas fa-sun text-yellow-500 mr-2"></i>
                                                    <span class="font-medium">Next Meal Suggestion</span>
                                                </div>
                                                <div class="text-sm text-gray-600" id="nextMealSuggestion">Based on your current intake...</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- History Tab -->
                <div id="history" class="tab-content">
                    <div class="max-w-7xl mx-auto px-6 py-8">
                        <div class="glass-effect rounded-2xl p-6">
                            <div class="flex items-center justify-between mb-6">
                                <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                                    <i class="fas fa-history mr-2 text-purple-500"></i>
                                    Recent Entries
                                </h2>
                                <button 
                                    onclick="deleteAllEntries()"
                                    class="bg-red-500/10 hover:bg-red-500/20 text-red-500 px-4 py-2 rounded-lg transition-all duration-200 flex items-center"
                                    title="Delete All Entries"
                                >
                                    <i class="fas fa-trash-alt mr-2"></i>
                                    Delete All
                                </button>
                            </div>
                            <div id="historyContainer" class="relative">
                                <div class="absolute left-4 top-0 bottom-0 w-0.5 bg-gradient-to-b from-blue-500/50 to-purple-500/50"></div>
                                <div class="space-y-4 pl-8">
                                    <div class="animate-pulse space-y-4">
                                        <div class="h-20 bg-gray-200 rounded-lg"></div>
                                        <div class="h-20 bg-gray-200 rounded-lg"></div>
                                        <div class="h-20 bg-gray-200 rounded-lg"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Coach Tab -->
                <div id="ai-coach" class="tab-content">
                    <div class="max-w-7xl mx-auto px-6 py-8">
                        <div class="grid grid-cols-12 gap-6">
                            <!-- Chat Section -->
                            <div class="col-span-12 lg:col-span-8">
                                <div class="glass-effect rounded-2xl p-6">
                                    <div class="flex items-center justify-between mb-6">
                                        <h2 class="text-lg font-semibold text-gray-800 flex items-center">
                                            <i class="fas fa-robot mr-2 text-green-500"></i>
                                            AI Nutrition Coach
                                        </h2>
                                        <button 
                                            onclick="resetChat()"
                                            class="bg-gray-500/10 hover:bg-gray-500/20 text-gray-500 px-4 py-2 rounded-lg transition-all duration-200 flex items-center"
                                            title="Reset Chat"
                                        >
                                            <i class="fas fa-redo mr-2"></i>
                                            Reset Chat
                                        </button>
                                    </div>
                                    
                                    <!-- Chat Messages -->
                                    <div id="chatMessages" class="space-y-4 mb-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
                                        <div class="chat-message flex items-start space-x-3">
                                            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center text-white flex-shrink-0">
                                                <i class="fas fa-robot text-sm"></i>
                                            </div>
                                            <div class="flex-1">
                                                <div class="bg-white/50 rounded-xl p-4">
                                                    <p class="text-gray-700">Hello! I'm your AI Nutrition Coach. I can help you achieve your health and fitness goals. What would you like to work on today?</p>
                                                </div>
                                                <div class="text-xs text-gray-500 mt-1">Just now</div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Chat Input -->
                                    <div class="relative">
                                        <textarea 
                                            id="chatInput" 
                                            class="w-full p-4 pr-12 bg-white/50 border border-gray-100 rounded-xl focus:ring-2 focus:ring-green-500/20 focus:border-green-500 transition-all duration-200 resize-none shadow-sm chat-input" 
                                            rows="2" 
                                            placeholder="Type your message here..."
                                        ></textarea>
                                        <button 
                                            id="sendMessageBtn"
                                            class="absolute right-3 bottom-3 bg-gradient-to-r from-green-400 to-blue-500 hover:from-green-500 hover:to-blue-600 text-white p-2 rounded-lg transition-all duration-200"
                                        >
                                            <i class="fas fa-paper-plane"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Macro Tracking Card -->
                            <div class="col-span-12 lg:col-span-4">
                                <div class="glass-effect rounded-2xl p-6">
                                    <h2 class="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                                        <i class="fas fa-chart-pie mr-2 text-purple-500"></i>
                                        Today's Macros
                                    </h2>
                                    
                                    <!-- Macro Progress -->
                                    <div class="space-y-4">
                                        <!-- Protein -->
                                        <div>
                                            <div class="flex items-center justify-between mb-1">
                                                <span class="text-sm text-gray-600">Protein</span>
                                                <span class="text-sm font-medium text-gray-800" id="proteinValue">0g</span>
                                            </div>
                                            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div id="proteinBar" class="h-full bg-blue-500 transition-all duration-500" style="width: 0%"></div>
                                            </div>
                                        </div>
                                        
                                        <!-- Carbs -->
                                        <div>
                                            <div class="flex items-center justify-between mb-1">
                                                <span class="text-sm text-gray-600">Carbs</span>
                                                <span class="text-sm font-medium text-gray-800" id="carbsValue">0g</span>
                                            </div>
                                            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div id="carbsBar" class="h-full bg-green-500 transition-all duration-500" style="width: 0%"></div>
                                            </div>
                                        </div>
                                        
                                        <!-- Fats -->
                                        <div>
                                            <div class="flex items-center justify-between mb-1">
                                                <span class="text-sm text-gray-600">Fats</span>
                                                <span class="text-sm font-medium text-gray-800" id="fatsValue">0g</span>
                                            </div>
                                            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div id="fatsBar" class="h-full bg-yellow-500 transition-all duration-500" style="width: 0%"></div>
                                            </div>
                                        </div>
                                        
                                        <!-- Calories -->
                                        <div>
                                            <div class="flex items-center justify-between mb-1">
                                                <span class="text-sm text-gray-600">Calories</span>
                                                <span class="text-sm font-medium text-gray-800" id="caloriesValue">0</span>
                                            </div>
                                            <div class="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                                                <div id="caloriesBar" class="h-full bg-red-500 transition-all duration-500" style="width: 0%"></div>
                                            </div>
                                        </div>
                                    </div>

                                    <!-- Macro Goals -->
                                    <div class="mt-6 pt-6 border-t border-gray-200">
                                        <h3 class="text-sm font-medium text-gray-800 mb-3">Daily Goals</h3>
                                        <div class="grid grid-cols-2 gap-4">
                                            <div class="bg-white/50 p-3 rounded-xl">
                                                <div class="text-xs text-gray-500">Protein Goal</div>
                                                <div class="text-lg font-bold text-gray-800" id="proteinGoal">120g</div>
                                            </div>
                                            <div class="bg-white/50 p-3 rounded-xl">
                                                <div class="text-xs text-gray-500">Carbs Goal</div>
                                                <div class="text-lg font-bold text-gray-800" id="carbsGoal">300g</div>
                                            </div>
                                            <div class="bg-white/50 p-3 rounded-xl">
                                                <div class="text-xs text-gray-500">Fats Goal</div>
                                                <div class="text-lg font-bold text-gray-800" id="fatsGoal">65g</div>
                                            </div>
                                            <div class="bg-white/50 p-3 rounded-xl">
                                                <div class="text-xs text-gray-500">Calories Goal</div>
                                                <div class="text-lg font-bold text-gray-800" id="caloriesGoal">2000</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Collapsible AI Processing Logs -->
        <div class="fixed bottom-0 left-0 right-0 bg-gray-900/95 backdrop-blur-lg border-t border-gray-800 transform transition-transform duration-300" id="logsPanel">
            <div class="max-w-7xl mx-auto px-4 py-2">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <i class="fas fa-terminal text-blue-400"></i>
                        <span class="text-sm text-gray-300">AI Processing Logs</span>
                    </div>
                    <button id="toggleLogs" class="text-gray-400 hover:text-white transition-colors p-1">
                        <i class="fas fa-chevron-up text-xs"></i>
                    </button>
                </div>
                <div id="logsContainer" class="text-xs text-gray-400 mt-1 max-h-[50vh] overflow-y-auto custom-scrollbar">
                    <p>🤖 AI Calorie Tracker ready for input...</p>
                </div>
            </div>
        </div>

        <script>
            // Global variables
            let isProcessing = false;
            let isRecording = false;
            let recognition = null;
            let weeklyChart = null;
            let currentModel = 'mistral-ai/Ministral-3B';
            let chatContext = [];  // Store chat context
            let userGoals = null;  // Store user goals

            // DOM elements
            const foodInput = document.getElementById('foodInput');
            const processBtn = document.getElementById('processBtn');
            const voiceBtn = document.getElementById('voiceBtn');
            const modelSelect = document.getElementById('modelSelect');
            const resultsSection = document.getElementById('resultsSection');
            const resultsContent = document.getElementById('resultsContent');
            const logsContainer = document.getElementById('logsContainer');
            const dailySummary = document.getElementById('dailySummary');
            const historyContainer = document.getElementById('historyContainer');
            const chatInput = document.getElementById('chatInput');
            const sendMessageBtn = document.getElementById('sendMessageBtn');
            const chatMessages = document.getElementById('chatMessages');
            const proteinValue = document.getElementById('proteinValue');
            const carbsValue = document.getElementById('carbsValue');
            const fatsValue = document.getElementById('fatsValue');
            const caloriesValue = document.getElementById('caloriesValue');
            const proteinGoal = document.getElementById('proteinGoal');
            const carbsGoal = document.getElementById('carbsGoal');
            const fatsGoal = document.getElementById('fatsGoal');
            const caloriesGoal = document.getElementById('caloriesGoal');
            const proteinBar = document.getElementById('proteinBar');
            const carbsBar = document.getElementById('carbsBar');
            const fatsBar = document.getElementById('fatsBar');
            const caloriesBar = document.getElementById('caloriesBar');

            // Tab switching functionality
            const tabs = document.querySelectorAll('.sidebar-tab');
            const tabContents = document.querySelectorAll('.tab-content');

            tabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    // Remove active class from all tabs and contents
                    tabs.forEach(t => t.classList.remove('active'));
                    tabContents.forEach(c => c.classList.remove('active'));

                    // Add active class to clicked tab and corresponding content
                    tab.classList.add('active');
                    const tabId = tab.getAttribute('data-tab');
                    document.getElementById(tabId).classList.add('active');

                    // If switching to history tab, refresh the history
                    if (tabId === 'history') {
                        loadHistory();
                    }
                });
            });

            // Chat functionality
            function addMessage(content, isUser = false) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'chat-message flex items-start space-x-3';
                
                const icon = isUser ? 'user' : 'robot';
                const iconColor = isUser ? 'from-blue-400 to-purple-500' : 'from-green-400 to-blue-500';
                
                messageDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br ${iconColor} flex items-center justify-center text-white flex-shrink-0">
                        <i class="fas fa-${icon} text-sm"></i>
                    </div>
                    <div class="flex-1">
                        <div class="bg-white/50 rounded-xl p-4">
                            <p class="text-gray-700">${content}</p>
                        </div>
                        <div class="text-xs text-gray-500 mt-1">Just now</div>
                    </div>
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function showTypingIndicator() {
                const indicatorDiv = document.createElement('div');
                indicatorDiv.className = 'chat-message flex items-start space-x-3';
                indicatorDiv.id = 'typingIndicator';
                
                indicatorDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center text-white flex-shrink-0">
                        <i class="fas fa-robot text-sm"></i>
                    </div>
                    <div class="flex-1">
                        <div class="bg-white/50 rounded-xl p-4">
                            <div class="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                `;
                
                chatMessages.appendChild(indicatorDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function removeTypingIndicator() {
                const indicator = document.getElementById('typingIndicator');
                if (indicator) {
                    indicator.remove();
                }
            }

            async function sendMessage() {
                const message = chatInput.value.trim();
                if (!message) return;

                // Add user message
                addMessage(message, true);
                chatInput.value = '';

                // Show typing indicator
                showTypingIndicator();

                try {
                    // Send message to backend with selected model
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            message: message,
                            context: chatContext,
                            model: currentModel
                        })
                    });

                    const data = await response.json();
                    
                    // Remove typing indicator
                    removeTypingIndicator();

                    if (data.success) {
                        // Add AI response with formatted content
                        addMessage(formatMessage(data.response));
                        
                        // Update context
                        chatContext = data.context;
                        
                        // Update macros if available
                        if (data.macros) {
                            updateMacros(data.macros);
                        }
                        
                        // Update goals if changed
                        if (data.goal_changed) {
                            userGoals = data.user_goals;
                            // Refresh macros to update goals
                            if (data.macros) {
                                updateMacros(data.macros);
                            }
                        }
                        
                        // If food was detected, update the dashboard
                        if (data.food_detected) {
                            // Trigger food processing
                            foodInput.value = data.food_input;
                            processBtn.click();
                        }
                    } else {
                        addMessage('Sorry, I encountered an error. Please try again.');
                    }
                } catch (error) {
                    removeTypingIndicator();
                    addMessage('Sorry, I encountered an error. Please try again.');
                }
            }

            function resetChat() {
                if (confirm('Are you sure you want to reset the chat? This will clear our conversation history.')) {
                    chatContext = [];
                    chatMessages.innerHTML = `
                        <div class="chat-message flex items-start space-x-3">
                            <div class="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center text-white flex-shrink-0">
                                <i class="fas fa-robot text-sm"></i>
                            </div>
                            <div class="flex-1">
                                <div class="bg-white/50 rounded-xl p-4">
                                    <p class="text-gray-700">Hello! I'm your AI Nutrition Coach. I can help you achieve your health and fitness goals. What would you like to work on today?</p>
                                </div>
                                <div class="text-xs text-gray-500 mt-1">Just now</div>
                            </div>
                        </div>
                    `;
                }
            }

            // Event listeners
            sendMessageBtn.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            // Auto-resize chat input
            chatInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });

            // Initialize the app
            document.addEventListener('DOMContentLoaded', function() {
                initializeVoiceRecognition();
                loadDailySummary();
                loadHistory();
                loadWeeklyChart();
                updateQuickStats();
            });

            // Initialize voice recognition
            function initializeVoiceRecognition() {
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    recognition = new SpeechRecognition();
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    recognition.lang = 'en-US';

                    recognition.onstart = function() {
                        isRecording = true;
                        voiceBtn.innerHTML = '<i class="fas fa-stop voice-recording"></i>';
                        voiceBtn.classList.add('bg-red-500');
                        voiceBtn.classList.remove('bg-green-500');
                    };

                    recognition.onresult = function(event) {
                        const transcript = event.results[0][0].transcript;
                        foodInput.value = transcript;
                        logsContainer.innerHTML = `<p class="text-blue-400">🎤 Voice input: "${transcript}"</p>`;
                    };

                    recognition.onend = function() {
                        isRecording = false;
                        voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
                        voiceBtn.classList.add('bg-green-500');
                        voiceBtn.classList.remove('bg-red-500');
                    };

                    recognition.onerror = function(event) {
                        console.error('Speech recognition error:', event.error);
                        logsContainer.innerHTML = `<p class="text-red-400">❌ Voice recognition error: ${event.error}</p>`;
                    };
                } else {
                    voiceBtn.style.display = 'none';
                    console.log('Speech recognition not supported');
                }
            }

            // Voice button click handler
            voiceBtn.addEventListener('click', function() {
                if (!recognition) return;

                if (isRecording) {
                    recognition.stop();
                } else {
                    recognition.start();
                    logsContainer.innerHTML = '<p class="text-blue-400">🎤 Listening... Speak now!</p>';
                }
            });

            // Model selection handler
            modelSelect.addEventListener('change', function() {
                currentModel = this.value;
                logsContainer.innerHTML = `<p class="text-blue-400">🔄 Switched to ${this.options[this.selectedIndex].text} model</p>`;
            });

            // Process food entry
            processBtn.addEventListener('click', async function() {
                const userInput = foodInput.value.trim();
                
                if (!userInput) {
                    alert('Please enter what you ate or use voice input!');
                    return;
                }

                if (isProcessing) return;
                
                isProcessing = true;
                processBtn.disabled = true;
                processBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
                
                logsContainer.innerHTML = `<p class="text-yellow-400">🔄 AI is analyzing your food entry using ${modelSelect.options[modelSelect.selectedIndex].text}...</p>`;

                try {
                    const response = await fetch('/process_food', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            user_input: userInput,
                            model: currentModel
                        })
                    });

                    const data = await response.json();
                    
                    if (data.success) {
                        displayResults(data);
                        displayLogs(data.logs);
                        loadDailySummary();
                        loadHistory();
                        loadWeeklyChart();
                        updateQuickStats();
                        updateNutritionInsights(data);
                        updateMealRecommendations(data);
                        updateHealthScore(data);
                        foodInput.value = '';
                    } else {
                        logsContainer.innerHTML = `<p class="text-red-400">❌ Error processing food entry: ${data.error || 'Unknown error'}</p>`;
                    }
                } catch (error) {
                    console.error('Error:', error);
                    logsContainer.innerHTML = `<p class="text-red-400">❌ Network error: ${error.message}</p>`;
                } finally {
                    isProcessing = false;
                    processBtn.disabled = false;
                    processBtn.innerHTML = '<i class="fas fa-brain mr-2"></i>Process with AI';
                }
            });

            // Display results
            function displayResults(data) {
                const resultsHTML = `
                    <div class="space-y-4">
                        <div class="bg-gradient-to-br from-blue-50 to-purple-50 p-4 rounded-xl">
                            <h3 class="font-semibold text-gray-800 mb-3 flex items-center">
                                <i class="fas fa-utensils mr-2 text-blue-500"></i>
                                Detected Food Items
                            </h3>
                            <div class="space-y-2">
                                ${data.detailed_breakdown.map(item => `
                                    <div class="flex justify-between items-center bg-white/50 p-3 rounded-lg group hover:bg-white/80 transition-all duration-200">
                                        <div class="flex items-center space-x-3">
                                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500/10 to-purple-500/10 flex items-center justify-center text-blue-500">
                                                <i class="fas fa-utensils text-sm"></i>
                                            </div>
                                            <span class="font-medium text-gray-800">${item.food}</span>
                                        </div>
                                        <div class="flex items-center space-x-2">
                                            <span class="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
                                                ${item.quantity}x
                                            </span>
                                            <span class="text-sm text-gray-600 bg-gray-100 px-2 py-1 rounded">
                                                ×${item.container_multiplier}x
                                            </span>
                                            <span class="font-medium text-blue-600">
                                                ${item.total_calories} cal
                                            </span>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        
                        <div class="bg-gradient-to-br from-green-50 to-blue-50 p-4 rounded-xl">
                            <div class="flex items-center justify-between mb-3">
                                <h3 class="font-semibold text-gray-800 flex items-center">
                                    <i class="fas fa-fire mr-2 text-orange-500"></i>
                                    Total Calories
                                </h3>
                                <div class="text-sm text-gray-500">
                                    ${data.daily_entries_count} entries today
                                </div>
                            </div>
                            <div class="flex items-center justify-between">
                                <div class="text-3xl font-bold text-green-600">${data.total_calories}</div>
                                <div class="text-sm text-gray-600">
                                    Daily Total: ${data.daily_total} cal
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                resultsContent.innerHTML = resultsHTML;
                resultsSection.classList.remove('hidden');
            }

            // Display processing logs
            function displayLogs(logs) {
                const logsHTML = logs.map(log => {
                    // Add different colors based on log type
                    let colorClass = 'text-gray-400';
                    if (log.includes('❌')) colorClass = 'text-red-400';
                    if (log.includes('✅')) colorClass = 'text-green-400';
                    if (log.includes('🤖')) colorClass = 'text-blue-400';
                    if (log.includes('📊')) colorClass = 'text-purple-400';
                    if (log.includes('💾')) colorClass = 'text-yellow-400';
                    
                    return `<p class="mb-0.5 ${colorClass}">${log}</p>`;
                }).join('');
                
                logsContainer.innerHTML = logsHTML;
                logsContainer.scrollTop = logsContainer.scrollHeight;
            }

            // Delete entry function
            async function deleteEntry(entryId) {
                if (!confirm('Are you sure you want to delete this entry?')) return;

                try {
                    const response = await fetch(`/delete_entry/${entryId}`, { method: 'DELETE' });
                    const data = await response.json();
                    
                    if (data.success) {
                        loadDailySummary();
                        loadHistory();
                        loadWeeklyChart();
                        updateQuickStats();
                        logsContainer.innerHTML = '<p class="text-green-400">✅ Entry deleted successfully</p>';
                    } else {
                        logsContainer.innerHTML = `<p class="text-red-400">❌ Error: ${data.error}</p>`;
                    }
                } catch (error) {
                    logsContainer.innerHTML = `<p class="text-red-400">❌ Error deleting entry</p>`;
                }
            }

            // Load daily summary
            async function loadDailySummary() {
                try {
                    const response = await fetch('/get_daily_summary');
                    const data = await response.json();
                    
                    const percentage = Math.round((data.total_calories / 2000) * 100);
                    const remaining = Math.max(0, 2000 - data.total_calories);
                    
                    // Update header progress
                    document.getElementById('todayProgress').textContent = `${data.total_calories}/2000`;
                    document.getElementById('goalProgressBar').style.width = `${Math.min(percentage, 100)}%`;
                    
                    const summaryHTML = `
                        <div class="space-y-4">
                            <div class="text-center">
                                <div class="text-3xl font-bold text-blue-600">${data.total_calories}</div>
                                <div class="text-gray-600 mb-2">calories today</div>
                                <div class="w-full bg-gray-200 rounded-full h-3">
                                    <div class="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500" 
                                         style="width: ${Math.min(percentage, 100)}%"></div>
                                </div>
                                <div class="text-sm text-gray-500 mt-1">${percentage}% of 2000 cal goal</div>
                                <div class="text-sm font-medium text-green-600 mt-2">${remaining} calories remaining</div>
                            </div>
                            <div class="grid grid-cols-2 gap-4 text-center">
                                <div class="bg-green-50 p-3 rounded-lg">
                                    <div class="text-lg font-bold text-green-600">${data.entries_count}</div>
                                    <div class="text-xs text-gray-600">Entries</div>
                                </div>
                                <div class="bg-purple-50 p-3 rounded-lg">
                                    <div class="text-lg font-bold text-purple-600">${new Date().toLocaleDateString()}</div>
                                    <div class="text-xs text-gray-600">Today</div>
                                </div>
                            </div>
                        </div>
                    `;
                    
                    dailySummary.innerHTML = summaryHTML;
                } catch (error) {
                    dailySummary.innerHTML = '<p class="text-red-600">Error loading daily summary</p>';
                }
            }

            // Load recent history
            async function loadHistory() {
                try {
                    const response = await fetch('/get_history');
                    const data = await response.json();
                    
                    if (data.success && data.entries.length > 0) {
                        const historyHTML = `
                            <div class="space-y-4">
                                ${data.entries.map((entry, index) => `
                                    <div class="relative group">
                                        <div class="absolute -left-8 top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 border-2 border-white shadow-lg"></div>
                                        <div class="bg-gradient-to-r from-blue-50/50 to-purple-50/50 border border-blue-100/50 p-4 rounded-xl group-hover:shadow-lg transition-all duration-200 relative">
                                            <div class="flex flex-col h-full">
                                                <div class="flex items-start justify-between">
                                                    <div class="flex-1">
                                                        <p class="font-medium text-gray-800 mb-2 line-clamp-2">"${entry.user_input}"</p>
                                                        <div class="flex items-center text-sm text-gray-600">
                                                            <i class="fas fa-fire mr-1 text-orange-500"></i>
                                                            <span>${entry.total_calories} calories</span>
                                                        </div>
                                                    </div>
                                                    <button 
                                                        onclick="deleteEntry(${entry.id})"
                                                        class="opacity-0 group-hover:opacity-100 bg-red-500/10 hover:bg-red-500/20 text-red-500 p-2 rounded-lg transition-all duration-200 ml-2"
                                                        title="Delete Entry"
                                                    >
                                                        <i class="fas fa-trash-alt text-xs"></i>
                                                    </button>
                                                </div>
                                                <div class="flex items-center text-xs text-gray-500 mt-2">
                                                    <i class="fas fa-clock mr-1"></i>
                                                    <span>${new Date(entry.created_at).toLocaleString()}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        `;
                        historyContainer.innerHTML = historyHTML;
                    } else {
                        historyContainer.innerHTML = `
                            <div class="text-center py-8 text-gray-500">
                                <i class="fas fa-utensils text-4xl mb-4"></i>
                                <p>No entries yet. Start tracking your calories!</p>
                            </div>
                        `;
                    }
                } catch (error) {
                    historyContainer.innerHTML = '<p class="text-red-600">Error loading history</p>';
                }
            }

            // Load weekly chart
            async function loadWeeklyChart() {
                try {
                    const response = await fetch('/get_weekly_data');
                    const data = await response.json();
                    
                    const ctx = document.getElementById('weeklyChart').getContext('2d');
                    
                    if (weeklyChart) {
                        weeklyChart.destroy();
                    }
                    
                    weeklyChart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: data.data.map(d => d.day),
                            datasets: [{
                                label: 'Daily Calories',
                                data: data.data.map(d => d.calories),
                                borderColor: 'rgb(99, 102, 241)',
                                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                borderWidth: 3,
                                fill: true,
                                tension: 0.4,
                                pointBackgroundColor: 'rgb(99, 102, 241)',
                                pointBorderColor: '#fff',
                                pointBorderWidth: 2,
                                pointRadius: 6
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    grid: {
                                        color: 'rgba(0, 0, 0, 0.1)'
                                    },
                                    ticks: {
                                        callback: function(value) {
                                            return value + ' cal';
                                        }
                                    }
                                },
                                x: {
                                    grid: {
                                        display: false
                                    }
                                }
                            },
                            elements: {
                                point: {
                                    hoverRadius: 8
                                }
                            }
                        }
                    });
                } catch (error) {
                    console.error('Error loading weekly chart:', error);
                }
            }

            // Update quick stats
            async function updateQuickStats() {
                try {
                    const response = await fetch('/get_weekly_data');
                    const data = await response.json();
                    
                    const totalWeekly = data.data.reduce((sum, day) => sum + day.calories, 0);
                    const avgDaily = Math.round(totalWeekly / 7);
                    
                    document.getElementById('avgDaily').textContent = avgDaily.toLocaleString();
                    document.getElementById('weekTotal').textContent = totalWeekly.toLocaleString();
                    document.getElementById('totalEntries').textContent = data.total_entries.toLocaleString();
                } catch (error) {
                    console.error('Error updating quick stats:', error);
                }
            }

            // Allow Enter key to submit
            foodInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    processBtn.click();
                }
            });

            // Auto-resize textarea
            foodInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = this.scrollHeight + 'px';
            });

            // Add new functions for AI features
            function updateNutritionInsights(data) {
                const nutritionGaps = document.getElementById('nutritionGaps');
                
                if (data.ai_insights) {
                    // Format nutrition gaps as a list
                    const nutritionGapsText = Array.isArray(data.ai_insights.nutrition_gaps)
                        ? data.ai_insights.nutrition_gaps.join(', ')
                        : data.ai_insights.nutrition_gaps || 'Identifying gaps...';
                    nutritionGaps.innerHTML = nutritionGapsText;
                }
            }

            function updateMealRecommendations(data) {
                const nextMealSuggestion = document.getElementById('nextMealSuggestion');
                
                if (data.ai_insights) {
                    // Format next meal suggestions as a list
                    const nextMealText = Array.isArray(data.ai_insights.next_meal)
                        ? data.ai_insights.next_meal.join(', ')
                        : data.ai_insights.next_meal || 'Based on your current intake...';
                    nextMealSuggestion.innerHTML = nextMealText;
                }
            }

            function updateHealthScore(data) {
                const scoreValue = document.getElementById('scoreValue');
                const healthScoreDescription = document.getElementById('healthScoreDescription');
                const healthScoreCircle = document.getElementById('healthScoreCircle');
                
                if (data.ai_insights) {
                    const score = data.ai_insights.health_score || 75;
                    
                    // Update description based on score
                    let description = '';
                    if (score >= 80) {
                        description = 'Excellent diet balance with optimal nutrition';
                    } else if (score >= 70) {
                        description = 'Good diet with minor improvements needed';
                    } else if (score >= 60) {
                        description = 'Moderate diet, consider adding more variety';
                    } else {
                        description = 'Diet needs improvement, focus on balanced nutrition';
                    }
                    
                    // Update score
                    scoreValue.textContent = score;
                    
                    // Update description
                    healthScoreDescription.textContent = description;
                    
                    // Update circle color and animation
                    const offset = 251.2 - (251.2 * (score / 100));
                    healthScoreCircle.style.strokeDashoffset = offset;
                    
                    // Update circle color based on score
                    if (score >= 80) {
                        healthScoreCircle.classList.remove('text-yellow-500', 'text-red-500');
                        healthScoreCircle.classList.add('text-green-500');
                    } else if (score >= 60) {
                        healthScoreCircle.classList.remove('text-green-500', 'text-red-500');
                        healthScoreCircle.classList.add('text-yellow-500');
                    } else {
                        healthScoreCircle.classList.remove('text-green-500', 'text-yellow-500');
                        healthScoreCircle.classList.add('text-red-500');
                    }
                }
            }

            // Toggle logs panel
            const logsPanel = document.getElementById('logsPanel');
            const toggleLogs = document.getElementById('toggleLogs');
            let isLogsExpanded = true;

            toggleLogs.addEventListener('click', () => {
                isLogsExpanded = !isLogsExpanded;
                if (isLogsExpanded) {
                    logsPanel.style.transform = 'translateY(0)';
                    document.getElementById('logsContainer').style.maxHeight = '50vh';
                    toggleLogs.innerHTML = '<i class="fas fa-chevron-up text-xs"></i>';
                } else {
                    logsPanel.style.transform = 'translateY(calc(100% - 2.5rem))';
                    document.getElementById('logsContainer').style.maxHeight = '100px';
                    toggleLogs.innerHTML = '<i class="fas fa-chevron-down text-xs"></i>';
                }
            });

            // Add the deleteAllEntries function
            async function deleteAllEntries() {
                if (!confirm('Are you sure you want to delete ALL entries? This action cannot be undone.')) return;

                try {
                    const response = await fetch('/delete_all_entries', { method: 'DELETE' });
                    const data = await response.json();
                    
                    if (data.success) {
                        loadDailySummary();
                        loadHistory();
                        loadWeeklyChart();
                        updateQuickStats();
                        logsContainer.innerHTML = '<p class="text-green-400">✅ All entries deleted successfully</p>';
                    } else {
                        logsContainer.innerHTML = `<p class="text-red-400">❌ Error: ${data.error}</p>`;
                    }
                } catch (error) {
                    logsContainer.innerHTML = `<p class="text-red-400">❌ Error deleting entries</p>`;
                }
            }

            // Update macros display
            function updateMacros(macros) {
                if (!macros) return;
                
                // Get current goals based on user's goal type
                const goalType = userGoals?.goal_type || 'maintenance';
                let goals = {
                    protein: 120,
                    carbs: 300,
                    fats: 65,
                    calories: 2000
                };
                
                // Adjust goals based on goal type
                if (goalType === 'weight_loss') {
                    goals = {
                        protein: 150,  // Higher protein for weight loss
                        carbs: 200,    // Lower carbs
                        fats: 50,      // Lower fats
                        calories: 1800 // Lower calories
                    };
                } else if (goalType === 'weight_gain') {
                    goals = {
                        protein: 180,  // Higher protein for muscle gain
                        carbs: 400,    // Higher carbs
                        fats: 80,      // Higher fats
                        calories: 2500 // Higher calories
                    };
                }
                
                // Update goal displays
                document.getElementById('proteinGoal').textContent = `${goals.protein}g`;
                document.getElementById('carbsGoal').textContent = `${goals.carbs}g`;
                document.getElementById('fatsGoal').textContent = `${goals.fats}g`;
                document.getElementById('caloriesGoal').textContent = goals.calories;
                
                // Update current values
                document.getElementById('proteinValue').textContent = `${Math.round(macros.protein)}g`;
                document.getElementById('carbsValue').textContent = `${Math.round(macros.carbs)}g`;
                document.getElementById('fatsValue').textContent = `${Math.round(macros.fats)}g`;
                document.getElementById('caloriesValue').textContent = Math.round(macros.calories);
                
                // Calculate percentages (can exceed 100%)
                const proteinPercent = (macros.protein / goals.protein) * 100;
                const carbsPercent = (macros.carbs / goals.carbs) * 100;
                const fatsPercent = (macros.fats / goals.fats) * 100;
                const caloriesPercent = (macros.calories / goals.calories) * 100;
                
                // Update progress bars with animation
                updateProgressBar('proteinBar', proteinPercent);
                updateProgressBar('carbsBar', carbsPercent);
                updateProgressBar('fatsBar', fatsPercent);
                updateProgressBar('caloriesBar', caloriesPercent);
            }

            function updateProgressBar(id, percent) {
                const bar = document.getElementById(id);
                const currentWidth = parseFloat(bar.style.width) || 0;
                const targetWidth = Math.min(percent, 100);
                
                // Animate the progress bar
                bar.style.transition = 'width 0.5s ease-out';
                bar.style.width = `${targetWidth}%`;
                
                // Change color based on percentage
                if (percent > 100) {
                    bar.style.backgroundColor = '#ef4444'; // Red for exceeding
                } else if (percent > 80) {
                    bar.style.backgroundColor = '#22c55e'; // Green for good progress
                } else {
                    bar.style.backgroundColor = '#3b82f6'; // Blue for normal progress
                }
            }

            // Add resetAllData function
            async function resetAllData() {
                if (!confirm('Are you sure you want to reset ALL your data? This will delete all your history, goals, macros, and chat history. This action cannot be undone.')) return;

                try {
                    const response = await fetch('/reset_all_data', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.success) {
                        // Reset all UI elements
                        loadDailySummary();
                        loadHistory();
                        loadWeeklyChart();
                        updateQuickStats();
                        resetChat();
                        updateMacros(null);
                        
                        // Show success message
                        logsContainer.innerHTML = '<p class="text-green-400">✅ All data reset successfully</p>';
                    } else {
                        logsContainer.innerHTML = `<p class="text-red-400">❌ Error: ${data.error}</p>`;
                    }
                } catch (error) {
                    logsContainer.innerHTML = `<p class="text-red-400">❌ Error resetting data</p>`;
                }
            }

            // Update the formatMessage function to better format AI responses
            function formatMessage(content) {
                // Convert markdown headers to styled headers
                content = content.replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold text-gray-800 mt-4 mb-2">$1</h3>');
                content = content.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-gray-800 mt-6 mb-3">$1</h2>');
                content = content.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-gray-800 mt-8 mb-4">$1</h1>');
                
                // Convert bullet points with better styling
                content = content.replace(/^\* (.*$)/gm, '<li class="ml-4 mb-2">$1</li>');
                content = content.replace(/(<li class="ml-4 mb-2">.*<\/li>)/gm, '<ul class="list-disc space-y-2 my-4 bg-white/30 p-4 rounded-lg">$1</ul>');
                
                // Convert numbered lists
                content = content.replace(/^\d+\. (.*$)/gm, '<li class="ml-4 mb-2">$1</li>');
                content = content.replace(/(<li class="ml-4 mb-2">.*<\/li>)/gm, '<ol class="list-decimal space-y-2 my-4 bg-white/30 p-4 rounded-lg">$1</ol>');
                
                // Convert bold and italic with better styling
                content = content.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-gray-800">$1</strong>');
                content = content.replace(/\*(.*?)\*/g, '<em class="italic text-gray-700">$1</em>');
                
                // Add action buttons for common responses
                if (content.includes('Would you like me to create a diet plan?')) {
                    content += `
                        <div class="mt-4 flex space-x-2">
                            <button onclick="sendMessage('Yes, please create a diet plan')" class="bg-green-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-600 transition-colors">
                                Yes, create plan
                            </button>
                            <button onclick="sendMessage('No, not yet')" class="bg-gray-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-600 transition-colors">
                                Not yet
                            </button>
                        </div>
                    `;
                }
                
                return content;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/process_food', methods=['POST'])
@login_required
def process_food():
    user_input = request.json.get('user_input', '')
    model_name = request.json.get('model', 'mistral-ai/Ministral-3B')
    all_logs = []
    
    try:
        # Get the appropriate client for the selected model
        model_client = get_model_client(model_name)
        all_logs.append(f"🤖 === AI FOOD ANALYSIS STARTED WITH {AVAILABLE_MODELS[model_name]} ===")
        
        # Step 1: Enhanced food extraction with AI
        food_entries, extraction_logs = advanced_food_extraction(user_input, model_client, model_name)
        all_logs.extend(extraction_logs)
        
        # Step 2: Calculate calories with enhanced breakdown
        all_logs.append("🧮 === CALORIE CALCULATION ===")
        total_calories, detailed_breakdown, calc_logs = calculate_enhanced_calories(food_entries)
        all_logs.extend(calc_logs)
        
        # Step 3: Get AI insights
        all_logs.append("🧠 === GETTING AI INSIGHTS ===")
        insights, insight_logs = get_llm_insights(food_entries, total_calories, model_client, model_name)
        all_logs.extend(insight_logs)
        
        # Step 4: Save to database with user_id
        all_logs.append("💾 === SAVING TO DATABASE ===")
        db_success, entry_id, db_logs = save_to_database(user_input, food_entries, total_calories, detailed_breakdown)
        all_logs.extend(db_logs)
        
        # Step 5: Get daily summary for current user
        all_logs.append("📊 === DAILY SUMMARY ===")
        daily_entries = get_daily_summary()
        daily_total = sum(entry['total_calories'] for entry in daily_entries)
        all_logs.append(f"📈 Updated daily total: {daily_total} calories")
        
        return jsonify({
            'success': True,
            'user_input': user_input,
            'food_entries': [entry['food'] for entry in food_entries],
            'total_calories': total_calories,
            'detailed_breakdown': detailed_breakdown,
            'daily_total': daily_total,
            'daily_entries_count': len(daily_entries),
            'logs': all_logs,
            'entry_id': entry_id,
            'ai_insights': insights,
            'model_used': AVAILABLE_MODELS[model_name]
        })
    except Exception as e:
        error_message = str(e)
        all_logs.append(f"❌ Error: {error_message}")
        return jsonify({
            'success': False,
            'error': error_message,
            'logs': all_logs
        })

@app.route('/delete_entry/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry_route(entry_id):
    success, message = delete_entry(entry_id)
    return jsonify({
        'success': success,
        'error': message if not success else None,
        'message': message if success else None
    })

@app.route('/get_daily_summary')
def daily_summary():
    date = request.args.get('date', datetime.now().date().isoformat())
    entries = get_daily_summary(date)
    total_calories = sum(entry['total_calories'] for entry in entries)
    
    return jsonify({
        'date': date,
        'entries': entries,
        'total_calories': total_calories,
        'entries_count': len(entries)
    })

@app.route('/get_history')
@login_required
def get_history():
    try:
        result = supabase.table('calorie_entries').select('*').eq('user_id', session['user_id']).order('created_at', desc=True).limit(15).execute()
        return jsonify({
            'success': True,
            'entries': result.data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/get_weekly_data')
@login_required
def get_weekly_data_route():
    try:
        data, total_entries = get_weekly_data()
        return jsonify({
            'data': data,
            'total_entries': total_entries
        })
    except Exception as e:
        return jsonify({
            'data': [],
            'total_entries': 0
        })

def get_weekly_data():
    """Get weekly calorie data for charts for current user"""
    try:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=6)  # Last 7 days
        
        # Get all entries for the week for current user
        result = supabase.table('calorie_entries').select('*').eq('user_id', session['user_id']).gte('date', start_date.isoformat()).lte('date', end_date.isoformat()).execute()
        
        # Group by date and sum calories
        daily_totals = {}
        daily_entries = {}  # Track entries per day
        
        for entry in result.data:
            date = entry['date']
            calories = entry['total_calories']
            daily_totals[date] = daily_totals.get(date, 0) + calories
            daily_entries[date] = daily_entries.get(date, 0) + 1
        
        # Create chart data for last 7 days
        chart_data = []
        total_entries = 0
        for i in range(7):
            date = (start_date + timedelta(days=i)).isoformat()
            chart_data.append({
                'date': date,
                'calories': daily_totals.get(date, 0),
                'entries': daily_entries.get(date, 0),
                'day': (start_date + timedelta(days=i)).strftime('%a')
            })
            total_entries += daily_entries.get(date, 0)
        
        return chart_data, total_entries
    except Exception as e:
        return [], 0

@app.route('/delete_all_entries', methods=['DELETE'])
@login_required
def delete_all_entries():
    try:
        # Delete all entries for the current user
        result = supabase.table('calorie_entries').delete().eq('user_id', session['user_id']).execute()
        
        if result.data:
            return jsonify({
                'success': True,
                'message': 'All entries deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No entries were deleted'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        message = request.json.get('message', '')
        context = request.json.get('context', [])
        model_name = request.json.get('model', 'microsoft/Phi-4')  # Changed default model
        user_id = session['user_id']
        
        # Save user message to history
        save_chat_message(user_id, message, True)
        
        # Get user's goals and macros
        user_goals = get_user_goals(user_id)
        user_macros = get_user_macros(user_id)
        
        # Get the appropriate client for the selected model
        model_client = get_model_client(model_name)
        
        # Prepare the prompt with context and user data
        context_str = '\n'.join([f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}" for i, msg in enumerate(context)])
        
        # Add user's goals and macros to the context
        user_context = ""
        if user_goals:
            user_context += f"\nUser's current goal: {user_goals['goal_type']}\n"
            user_context += f"Target weight: {user_goals['target_weight']} kg\n"
            user_context += f"Timeline: {user_goals['timeline_weeks']} weeks\n"
        
        if user_macros:
            user_context += "\nToday's macros:\n"
            for macro in user_macros:
                user_context += f"- Protein: {macro['protein']}g\n"
                user_context += f"- Carbs: {macro['carbs']}g\n"
                user_context += f"- Fats: {macro['fats']}g\n"
                user_context += f"- Calories: {macro['calories']}\n"
        
        prompt = f"""Previous conversation:
{context_str}

User's Context:
{user_context}

User: {message}

You are a friendly and supportive nutrition coach. Keep your responses:
1. Short and sweet - aim for 2-3 sentences max
2. Casual and conversational - like a friend chatting
3. Positive and motivating - use encouraging language
4. Specific and actionable - give clear, simple advice
5. Personal - reference their goals and food choices

Important Guidelines:
- If asked "who are you?", respond with: "I'm your friendly nutrition coach! I'm here to help you eat better and reach your health goals. Think of me as your supportive friend who knows a lot about food and nutrition. 😊"
- Never repeat the same response twice
- If user asks to stop using their name, acknowledge and remember this preference
- If user mentions a goal (weight loss/gain), update their goals in the system
- Always track food mentioned in the conversation
- Keep track of macros and update them accordingly
- Use emojis occasionally to make responses more friendly
- Give specific portion size recommendations
- Suggest healthy alternatives when appropriate
- Provide quick tips for meal prep and planning
- Share simple recipe ideas when relevant
- Encourage water intake and hydration
- Remind about the importance of sleep and rest
- Suggest simple exercises when appropriate

Avoid:
- Long paragraphs or complex explanations
- Technical jargon or scientific terms
- Formal or robotic language
- Multiple suggestions at once
- Unnecessary details
- Repeating the same responses

If they mention food:
- Acknowledge their choice
- Give a quick tip or suggestion
- Keep it light and fun
- Update their macros
- Suggest healthy alternatives if needed
- Mention portion control if relevant

If they ask about goals:
- Ask one simple question
- Focus on their motivation
- Keep it encouraging
- Update their goals
- Suggest small, achievable steps
- Celebrate their progress

Remember: You're a friend helping them eat better, not a textbook or robot.

Assistant:"""
        
        try:
            # Get AI response
            response = model_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a friendly and supportive nutrition coach. Keep responses short, casual, and motivating. Focus on being helpful without being overwhelming. Always track food and update macros. Use emojis occasionally to make responses more friendly."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                top_p=0.95,
                model=model_name
            )
            
            ai_response = response.choices[0].message.content
            
            # Save AI response to history
            save_chat_message(user_id, ai_response, False)
            
            # Enhanced food detection with macro estimation
            food_detected = False
            food_input = None
            macro_data = None
            
            # Get current macros for today
            current_macros = get_user_macros(user_id)
            current_total = {
                'protein': sum(m['protein'] for m in current_macros) if current_macros else 0,
                'carbs': sum(m['carbs'] for m in current_macros) if current_macros else 0,
                'fats': sum(m['fats'] for m in current_macros) if current_macros else 0,
                'calories': sum(m['calories'] for m in current_macros) if current_macros else 0
            }
            
            # Enhanced food database with quantities and more foods
            common_foods = {
                'samosa': {'protein': 3, 'carbs': 15, 'fats': 8, 'calories': 150},
                'idli': {'protein': 2, 'carbs': 15, 'fats': 0.5, 'calories': 70},
                'sambar': {'protein': 3, 'carbs': 10, 'fats': 1, 'calories': 60},
                'rice': {'protein': 2, 'carbs': 45, 'fats': 0.5, 'calories': 200},
                'chapati': {'protein': 3, 'carbs': 15, 'fats': 1, 'calories': 100},
                'dal': {'protein': 6, 'carbs': 20, 'fats': 1, 'calories': 120},
                'bread': {'protein': 3, 'carbs': 15, 'fats': 1, 'calories': 80},
                'pasta': {'protein': 5, 'carbs': 30, 'fats': 1, 'calories': 150},
                'pizza': {'protein': 10, 'carbs': 30, 'fats': 12, 'calories': 300},
                'burger': {'protein': 15, 'carbs': 30, 'fats': 20, 'calories': 350},
                'salad': {'protein': 2, 'carbs': 5, 'fats': 0.5, 'calories': 30},
                'paneer': {'protein': 18, 'carbs': 2, 'fats': 20, 'calories': 265},
                'curd': {'protein': 3, 'carbs': 4, 'fats': 2, 'calories': 60},
                'milk': {'protein': 8, 'carbs': 12, 'fats': 8, 'calories': 150},
                'banana': {'protein': 1, 'carbs': 27, 'fats': 0.3, 'calories': 105},
                'apple': {'protein': 0.5, 'carbs': 25, 'fats': 0.3, 'calories': 95},
                'orange': {'protein': 1, 'carbs': 12, 'fats': 0.1, 'calories': 47},
                'mango': {'protein': 1, 'carbs': 15, 'fats': 0.4, 'calories': 60},
                'chicken': {'protein': 31, 'carbs': 0, 'fats': 3.6, 'calories': 165},
                'fish': {'protein': 22, 'carbs': 0, 'fats': 3.5, 'calories': 120},
                'egg': {'protein': 6, 'carbs': 0.6, 'fats': 5, 'calories': 68},
                'boiled egg': {'protein': 6, 'carbs': 0.6, 'fats': 5, 'calories': 68},
                'dosa': {'protein': 3, 'carbs': 20, 'fats': 2, 'calories': 133},
                'upma': {'protein': 4, 'carbs': 25, 'fats': 3, 'calories': 150},
                'poha': {'protein': 3, 'carbs': 22, 'fats': 2, 'calories': 120},
                'paratha': {'protein': 5, 'carbs': 30, 'fats': 8, 'calories': 200},
                'biryani': {'protein': 15, 'carbs': 45, 'fats': 12, 'calories': 350},
                'noodles': {'protein': 4, 'carbs': 35, 'fats': 2, 'calories': 180},
                'sandwich': {'protein': 8, 'carbs': 25, 'fats': 5, 'calories': 180},
                'soup': {'protein': 2, 'carbs': 8, 'fats': 1, 'calories': 50},
                'juice': {'protein': 0, 'carbs': 25, 'fats': 0, 'calories': 100},
                'coffee': {'protein': 0, 'carbs': 0, 'fats': 0, 'calories': 2},
                'tea': {'protein': 0, 'carbs': 0, 'fats': 0, 'calories': 7},
                'water': {'protein': 0, 'carbs': 0, 'fats': 0, 'calories': 0}
            }
            
            # Enhanced food detection with quantity and containers
            detected_foods = []
            message_lower = message.lower()
            
            # Common container sizes and their multipliers
            containers = {
                'bowl': 1.5,
                'plate': 2.0,
                'cup': 1.0,
                'glass': 1.0,
                'piece': 1.0,
                'slice': 1.0,
                'serving': 1.0,
                'portion': 1.0,
                'small': 0.7,
                'medium': 1.0,
                'large': 1.3,
                'half': 0.5,
                'quarter': 0.25,
                'full': 1.0
            }
            
            for food, macros in common_foods.items():
                if food in message_lower:
                    # Look for quantity and container before the food name
                    quantity = 1
                    container_multiplier = 1.0
                    words = message_lower.split()
                    food_index = words.index(food)
                    
                    if food_index > 0:
                        # Check for numbers
                        try:
                            quantity = float(words[food_index - 1])
                        except (ValueError, IndexError):
                            # Check for common quantity words
                            if words[food_index - 1] in ['a', 'an', 'one']:
                                quantity = 1
                            elif words[food_index - 1] in ['two', '2']:
                                quantity = 2
                            elif words[food_index - 1] in ['three', '3']:
                                quantity = 3
                            elif words[food_index - 1] in ['four', '4']:
                                quantity = 4
                            elif words[food_index - 1] in ['five', '5']:
                                quantity = 5
                            
                            # Check for container sizes
                            for container, multiplier in containers.items():
                                if container in words[food_index - 1]:
                                    container_multiplier = multiplier
                                    break
                    
                    food_detected = True
                    detected_foods.append(food)
                    
                    # Calculate macros with quantity and container
                    total_multiplier = quantity * container_multiplier
                    if not macro_data:
                        macro_data = {k: v * total_multiplier for k, v in macros.items()}
                    else:
                        for key in macro_data:
                            macro_data[key] += macros[key] * total_multiplier
            
            # Update macros if food was detected
            if food_detected:
                food_input = message
                if macro_data:
                    # Add to existing macros
                    for key in macro_data:
                        macro_data[key] += current_total[key]
                    save_user_macros(user_id, macro_data)
            
            # Check for goal changes
            goal_changed = False
            if 'lose weight' in message_lower or 'weight loss' in message_lower:
                goal_data = {
                    'goal_type': 'weight_loss',
                    'target_weight': user_goals['target_weight'] if user_goals else 70,
                    'timeline_weeks': user_goals['timeline_weeks'] if user_goals else 12
                }
                save_user_goal(user_id, goal_data)
                goal_changed = True
            elif 'gain weight' in message_lower or 'weight gain' in message_lower or 'increase weight' in message_lower:
                goal_data = {
                    'goal_type': 'weight_gain',
                    'target_weight': user_goals['target_weight'] if user_goals else 80,
                    'timeline_weeks': user_goals['timeline_weeks'] if user_goals else 12
                }
                save_user_goal(user_id, goal_data)
                goal_changed = True
            
            # Update context
            context.append(message)
            context.append(ai_response)
            
            return jsonify({
                'success': True,
                'response': ai_response,
                'context': context,
                'food_detected': food_detected,
                'food_input': food_input,
                'macros': macro_data,
                'user_goals': user_goals,
                'goal_changed': goal_changed
            })
            
        except Exception as e:
            print(f"Error in AI response: {str(e)}")
            return jsonify({
                'success': False,
                'error': "I'm having trouble processing your request right now. Please try again in a moment."
            })
            
    except Exception as e:
        print(f"Error in chat route: {str(e)}")
        return jsonify({
            'success': False,
            'error': "I'm having trouble processing your request right now. Please try again in a moment."
        })

def get_user_goals(user_id):
    """Get user's current goals"""
    try:
        result = supabase.table('user_goals').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error getting user goals: {str(e)}")
        return None

def save_user_goal(user_id, goal_data):
    """Save or update user's goals"""
    try:
        # Check if user already has a goal
        existing_goal = get_user_goals(user_id)
        
        if existing_goal:
            # Update existing goal
            result = supabase.table('user_goals').update(goal_data).eq('id', existing_goal['id']).execute()
        else:
            # Create new goal
            goal_data['user_id'] = user_id
            result = supabase.table('user_goals').insert(goal_data).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error saving user goal: {str(e)}")
        return None

def save_user_macros(user_id, macro_data):
    """Save user's daily macros"""
    try:
        macro_data['user_id'] = user_id
        macro_data['date'] = datetime.now().date().isoformat()
        result = supabase.table('user_macros').insert(macro_data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error saving user macros: {str(e)}")
        return None

def get_user_macros(user_id, date=None):
    """Get user's macros for a specific date"""
    if not date:
        date = datetime.now().date().isoformat()
    
    try:
        result = supabase.table('user_macros').select('*').eq('user_id', user_id).eq('date', date).execute()
        return result.data
    except Exception as e:
        print(f"Error getting user macros: {str(e)}")
        return []

def save_chat_message(user_id, message, is_user):
    """Save chat message to history"""
    try:
        data = {
            'user_id': user_id,
            'message': message,
            'is_user': is_user
        }
        result = supabase.table('chat_history').insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error saving chat message: {str(e)}")
        return None

def get_chat_history(user_id, limit=10):
    """Get recent chat history"""
    try:
        result = supabase.table('chat_history').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
        return result.data
    except Exception as e:
        print(f"Error getting chat history: {str(e)}")
        return []

@app.route('/reset_all_data', methods=['POST'])
@login_required
def reset_all_data():
    try:
        user_id = session['user_id']
        
        # Delete all data for the user from all tables
        supabase.table('calorie_entries').delete().eq('user_id', user_id).execute()
        supabase.table('user_goals').delete().eq('user_id', user_id).execute()
        supabase.table('user_macros').delete().eq('user_id', user_id).execute()
        supabase.table('chat_history').delete().eq('user_id', user_id).execute()
        
        return jsonify({
            'success': True,
            'message': 'All user data has been reset successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Change the run configuration at the bottom
if __name__ == '__main__':
    # For local development
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        # For production (Vercel)
        app.run()

# Enhanced Requirements.txt:
# flask==2.3.3
# supabase==1.0.4
# requests==2.31.0

# Enhanced Supabase table schema:
# CREATE TABLE calorie_entries (
#     id SERIAL PRIMARY KEY,
#     user_input TEXT NOT NULL,
#     food_items TEXT NOT NULL,
#     total_calories INTEGER NOT NULL,
#     detailed_breakdown TEXT NOT NULL,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
#     date DATE NOT NULL
# );

# New tables for AI Coach:
# CREATE TABLE user_goals (
#     id SERIAL PRIMARY KEY,
#     user_id TEXT NOT NULL,
#     goal_type TEXT NOT NULL,  -- 'weight_gain', 'weight_loss', 'maintenance'
#     target_weight DECIMAL,
#     current_weight DECIMAL,
#     timeline_weeks INTEGER,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
#     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );

# CREATE TABLE user_macros (
#     id SERIAL PRIMARY KEY,
#     user_id TEXT NOT NULL,
#     date DATE NOT NULL,
#     protein DECIMAL,
#     carbs DECIMAL,
#     fats DECIMAL,
#     fiber DECIMAL,
#     calories INTEGER,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );

# CREATE TABLE chat_history (
#     id SERIAL PRIMARY KEY,
#     user_id TEXT NOT NULL,
#     message TEXT NOT NULL,
#     is_user BOOLEAN NOT NULL,
#     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
# );

# Key Improvements Made:
# 1. ✅ Enhanced AI calorie detection - now properly detects "3 chapati" as 3x chapati calories
# 2. ✅ Voice input functionality with speech recognition
# 3. ✅ Delete button for each entry in Recent Entries section
# 4. ✅ Modern, responsive UI using full screen space with glassmorphism effects
# 5. ✅ Interactive weekly chart showing calorie trends
# 6. ✅ Better quantity detection (handles numbers, containers, serving sizes)
# 7. ✅ Enhanced food database with more Indian and international foods
# 8. ✅ Real-time processing logs with emojis and better formatting
# 9. ✅ Quick stats dashboard with weekly summaries
# 10. ✅ Improved error handling and user feedback