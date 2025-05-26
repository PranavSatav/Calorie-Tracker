# Calorie-Tracker

Push your code to a GitHub repository

Go to Vercel Dashboard

Click "New Project"

Import your GitHub repository

Configure the project:

Framework Preset: Other

Build Command: Leave empty

Output Directory: Leave empty

Add your environment variables

Click "Deploy"

------------------------------------

setting up variables - 

Go to Vercel Dashboard
Create a new project
In the project settings, go to "Environment Variables"
Add the following environment variables

     SECRET_KEY=your-secure-secret-key
     GITHUB_TOKEN=your-github-token
     SUPABASE_URL=your-supabase-url
     SUPABASE_KEY=your-supabase-key

🔍 Project Overview
Name (Inferred): AI Calorie Tracker Pro
Tech Stack:

Backend: Flask (Python)

Database: Supabase

AI: GitHub-hosted models via OpenAI SDK

Deployment: Vercel

Frontend: HTML + Tailwind CSS + JavaScript

Authentication: Session-based login with bcrypt

Voice Input: Web Speech API

Logging: Interactive AI logs panel

🌟 Key Features
1. User Authentication
Registration & Login: Secure signup/login using Supabase.

Session Management: User sessions are stored in Flask sessions.

Password Encryption: Uses bcrypt for hashing.

2. AI Food Analysis
Natural Language Input: Type or speak descriptions like “2 bowls of rice, 1 samosa”.

AI Models Supported:

microsoft/Phi-4

openai/gpt-4.1

mistral-ai/Ministral-3B

deepseek/DeepSeek-R1

Dynamic Parsing:

Extracts food names, quantities, portion sizes, calories.

Assigns confidence scores.

Handles messy or ambiguous input using fallback parsing.

3. Calorie & Nutrient Insights
Calorie Calculator: Computes total calories with multipliers for portion size and quantity.

AI Nutrition Coach:

Returns insights like macro balance, nutrition gaps, health score (0–100), and next meal suggestions.

Detailed Logs: All AI processing is logged with emoji-coded steps in a collapsible terminal UI.

4. Weekly Visualization
Daily Summary: Tracks daily total calorie consumption.

Weekly Chart: Uses Chart.js to visualize weekly trends in calorie intake.

Quick Stats: Shows average daily intake, weekly total, and number of entries.

5. History Management
View Past Entries: Organized by date, fetched from Supabase.

Delete Functionality: Remove individual entries or reset all.

6. Voice Input Support
Uses Web Speech API to transcribe spoken food entries and process them with AI.

UI Feedback: Voice input button animates while recording.

7. AI Nutrition Chatbot
Located under the “AI Coach” tab.

Accepts free-form chat queries like:

“What should I eat for dinner?”

“Help me plan a high-protein vegetarian meal.”

Remembers context and can adjust user goals.

8. Macros Tracker
Tracks:

Protein

Carbs

Fats

Calories

Shows progress bars and compares them with preset daily goals.

📦 Project Structure
app.py – Full Flask app with routes, logic, and UI in one file.

.gitignore – Ignores secrets, environment, cache, etc.

requirements.txt – All Python dependencies for deployment
.

vercel.json – Configuration for deploying the app on Vercel
.

✅ Dependencies
plaintext
Copy
Edit
flask           - Web framework
supabase        - Database integration
requests        - HTTP API calls
openai          - AI interaction via GitHub-hosted models
bcrypt          - Password hashing
python-dotenv   - Environment variable loader
💡 Unique Aspects
Model flexibility: User can switch AI models on-the-fly.

Voice-enabled logging: Captures and logs all processing with interactive feedback.

AI nutrition coaching: AI not only analyzes but guides user choices interactively.

Visual analytics: Combines charts + logs + macros in an intuitive dashboard.


this is SQL command that is to be ran directly in supabase to automatically create tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Calorie entries table for tracking food intake
CREATE TABLE calorie_entries (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    user_input TEXT NOT NULL,
    food_items TEXT NOT NULL,
    total_calories INTEGER NOT NULL,
    detailed_breakdown TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date DATE NOT NULL
);

-- User goals table for tracking fitness goals
CREATE TABLE user_goals (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    goal_type TEXT NOT NULL,  -- 'weight_gain', 'weight_loss', 'maintenance'
    target_weight DECIMAL,
    current_weight DECIMAL,
    timeline_weeks INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User macros table for tracking daily nutrition
CREATE TABLE user_macros (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    date DATE NOT NULL,
    protein DECIMAL,
    carbs DECIMAL,
    fats DECIMAL,
    fiber DECIMAL,
    calories INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat history table for AI coach conversations
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    message TEXT NOT NULL,
    is_user BOOLEAN NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for better query performance
CREATE INDEX idx_calorie_entries_user_id ON calorie_entries(user_id);
CREATE INDEX idx_calorie_entries_date ON calorie_entries(date);
CREATE INDEX idx_user_goals_user_id ON user_goals(user_id);
CREATE INDEX idx_user_macros_user_id_date ON user_macros(user_id, date);
CREATE INDEX idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX idx_chat_history_created_at ON chat_history(created_at);

-- Add foreign key constraints
ALTER TABLE calorie_entries
ADD CONSTRAINT fk_calorie_entries_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;

ALTER TABLE user_goals
ADD CONSTRAINT fk_user_goals_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;

ALTER TABLE user_macros
ADD CONSTRAINT fk_user_macros_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;

ALTER TABLE chat_history
ADD CONSTRAINT fk_chat_history_user
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
