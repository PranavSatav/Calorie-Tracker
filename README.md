# 🍎 AI Calorie Tracker Pro

> *"I ate pizza for breakfast, and my AI coach didn't judge me... much."* 🍕

Welcome to the future of nutrition tracking! This isn't your grandma's calorie counter - it's powered by cutting-edge AI that understands when you say "I devoured a mountain of nachos" and somehow knows that equals 847 calories. Magic? No. AI? YES! ✨

TRY IT HERE --> https://calorie-tracker-lyart.vercel.app/login

Screens!!


![image](https://github.com/user-attachments/assets/3881ec65-4ecc-4f61-93d9-0a32fb89874c)

![image](https://github.com/user-attachments/assets/b1dbf5c7-9ecc-4a70-b973-48dbce0e75ad)

![image](https://github.com/user-attachments/assets/c25e5364-f4fe-4a51-9128-64c5dde05ea7)

![image](https://github.com/user-attachments/assets/a2775a99-da47-42a7-80ba-90714155a59c)

![image](https://github.com/user-attachments/assets/60af51d2-5679-4269-a1a4-6739af532684)

![image](https://github.com/user-attachments/assets/a0708c23-619c-4d96-9e08-a6eeac29ca65)

![image](https://github.com/user-attachments/assets/33df433a-fae0-45a0-9761-0af20bd7cadf)


## 🚀 What Makes This Special?

- **🎤 Voice-Powered**: Just speak your food into existence! "Two donuts and regret" → Boom, tracked!
- **🤖 Multiple AI Models**: Choose your AI companion - from Microsoft's Phi-4 to OpenAI's GPT-4.1
- **🍔 Smart Food Recognition**: Type "burger and fries" and watch AI break it down like a nutrition detective
- **📊 Beautiful Analytics**: Weekly charts that make your eating habits look almost artistic
- **💬 AI Nutrition Coach**: Ask "What should I eat?" and get personalized suggestions (spoiler: probably not pizza)
- **🎯 Macro Tracking**: Protein, carbs, fats - all visualized with satisfying progress bars

## 🛠️ Tech Stack That Slaps

- **Backend**: Flask (Python) - Because life's too short for complicated frameworks
- **Database**: Supabase - PostgreSQL but make it ✨fancy✨
- **AI**: GitHub Models API - Multiple AI personalities in one app
- **Frontend**: HTML + Tailwind CSS + Vanilla JavaScript - Old school cool
- **Deployment**: Vercel - Deploy faster than you can say "quinoa"
- **Auth**: bcrypt + Sessions - Secure like Fort Knox, smooth like butter

## 🎯 Features That'll Make You Go "Wow"

### 🔐 User Authentication
- Sign up/Login with military-grade security (bcrypt hashing)
- Session management that actually works
- Your data stays YOUR data

### 🧠 AI Food Analysis
Natural language processing that gets you:
```
Input: "2 bowls of rice, 1 samosa, and my dignity"
Output: 
- Basmati Rice (2 bowls): 440 calories
- Samosa (1 piece): 150 calories
- Dignity: Priceless (0 calories)
```

### 📈 Smart Analytics
- Daily calorie summaries
- Weekly trend visualization
- Health scores (0-100, try not to cry)
- Macro breakdowns prettier than your Instagram feed

### 🎙️ Voice Recognition
Speak your sins directly into the app. Web Speech API captures every "I had ice cream for dinner" moment.

### 💬 AI Nutrition Coach
Ask anything:
- "Plan my meals for tomorrow"
- "Is cereal a soup?"
- "Help me eat less pizza" (Good luck with that one)

## 🚀 Getting Started (The Fun Part!)

### Step 1: Fork This Bad Boy 🍴

1. Click that shiny **Fork** button at the top right
2. Name your fork something creative (or just keep it boring, we don't judge)
3. Clone your fork to your local machine

### Step 2: Set Up Your Secret Ingredients 🔐

You'll need these API keys (don't worry, most are free):

#### 2.1 Supabase Setup (Your Database BFF)
1. Go to [supabase.com](https://supabase.com) and create an account
2. Create a new project (pick a region close to you for speed)
3. Go to **Settings** → **API** and grab:
   - `Project URL` (your SUPABASE_URL)
   - `anon public` key (your SUPABASE_KEY)
4. Go to **SQL Editor** and run the magic table creation script from the docs - CODE is there in the REPO itself as SQL.TXT just copy and paste code in supabase.

#### 2.2 GitHub Models API (Your AI Brain)
1. Visit [GitHub Models](https://github.com/marketplace/models)
2. Generate a personal access token with model access
3. That's your `GITHUB_TOKEN`

#### 2.3 Create Your Environment File
Create a `.env` file in your project root:

```bash
SECRET_KEY=your-super-secret-flask-key-make-it-random
GITHUB_TOKEN=your-github-models-token
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

### Step 3: Test Locally (The Moment of Truth) 🧪

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open your browser to http://localhost:5000
# If it works, do a little dance 💃
```

### Step 4: Deploy to Vercel (Make It Live!) 🚀

#### 4.1 Connect to Vercel
1. Push your code to GitHub:
```bash
git add .
git commit -m "🚀 Ready for deployment!"
git push origin main
```

2. Go to [vercel.com](https://vercel.com) and sign up with GitHub
3. Click **"New Project"**
4. Import your GitHub repository

#### 4.2 Configure Your Deployment
- **Framework Preset**: `Other` (we're special like that)
- **Build Command**: Leave empty (Flask handles it)
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

#### 4.3 Add Environment Variables
In Vercel project settings → Environment Variables, add:
- `SECRET_KEY` = your-super-secret-flask-key
- `GITHUB_TOKEN` = your-github-models-token  
- `SUPABASE_URL` = your-supabase-url
- `SUPABASE_KEY` = your-supabase-key

#### 4.4 Deploy! 
Click **Deploy** and watch the magic happen ✨

Your app will be live at `https://your-project-name.vercel.app`!

## 🎮 How to Use This Beast

### 1. Sign Up & Login
Create your account and dive into the calorie-counting cosmos!

### 2. Log Your Food
- **Type**: "chicken sandwich and chips"
- **Speak**: Click the mic and say your food sins out loud
- **Watch**: AI breaks it down with scary accuracy

### 3. Explore the Dashboard
- **Today**: See your daily intake and macro breakdown
- **History**: Review your food journey (prepare for emotions)
- **Analytics**: Weekly charts that reveal your eating patterns
- **AI Coach**: Chat with your digital nutrition guru

### 4. Set Goals & Track Macros
Define your targets and watch those progress bars fill up!

## 🏗️ Project Structure

```
ai-calorie-tracker-pro/
├── app.py              # The main Flask application (where magic happens)
├── requirements.txt    # Python dependencies
├── vercel.json        # Vercel deployment config
├── .env               # Your secret keys (don't commit this!)
├── .gitignore         # Files to ignore
└── README.md          # This beautiful document
```

## 🐛 Troubleshooting (When Things Go Wrong)

### "My AI isn't working!"
- Check your `GITHUB_TOKEN` is valid
- Verify you have access to GitHub Models
- Try switching AI models in the dropdown

### "Database errors everywhere!"
- Confirm your Supabase URL and key are correct
- Make sure you ran the SQL table creation script
- Check if your Supabase project is active

### "Vercel deployment failed!"
- Ensure all environment variables are set
- Check the build logs for specific errors
- Try redeploying after fixing issues

### "Voice input not working!"
- Use HTTPS (required for Web Speech API)
- Allow microphone permissions
- Try a different browser (Chrome works best)

## 🤝 Contributing

Found a bug? Want to add a feature? Here's how to contribute:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Final Words

Congratulations! You've just deployed an AI-powered calorie tracker that's smarter than most humans when it comes to nutrition. Use it wisely, track responsibly, and remember - the AI is watching your food choices (but in a helpful way, not a creepy way).

Now go forth and track those calories like the nutrition ninja you were meant to be! 🥷

---

*Made with ❤️, lots of ☕, and probably too much 🍕*

## 🌟 Star This Repo!

If this project helped you track your way to better health (or at least made you more aware of your pizza consumption), give it a star! ⭐

**Happy Tracking!** 🎯
