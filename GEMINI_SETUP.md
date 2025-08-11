# 🧠 Gemini AI Integration Setup Guide

## 📋 **Overview**
Your Flask backend now supports AI-powered detailed explanations for 3D mathematical models using Google's Gemini API.

## 🔑 **Step 1: Get Gemini API Key**

1. Go to [Google AI Studio](https://makersuite.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" 
4. Create a new project or use existing one
5. Generate your API key
6. Copy the API key (keep it secure!)

## ⚙️ **Step 2: Install Dependencies**

```bash
pip install google-generativeai
```

Or install all requirements:
```bash
pip install -r backend/requirements.txt
```

## 🔧 **Step 3: Set Environment Variable**

### Option A: Command Line (Temporary)
```bash
export GEMINI_API_KEY="your_api_key_here"
python3 backend/app.py
```

### Option B: Create .env File (Recommended)
Create a `.env` file in your project root:
```bash
# .env file
GEMINI_API_KEY=your_actual_api_key_here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

### Option C: Direct in Terminal
```bash
GEMINI_API_KEY="your_api_key_here" python3 backend/app.py
```

## 🚀 **Step 4: Test AI Features**

1. Start your Flask backend
2. Generate any 3D model (e.g., `r = 2*cos(4θ)`)
3. Check the response for the new `ai_explanation` field

## 📊 **AI Explanation Features**

The AI will provide:

- **📖 Mathematical Foundation**: What the equation represents
- **🎨 3D Visualization**: Why the model looks the way it does  
- **🔍 Key Properties**: Symmetry, periodicity, etc.
- **🌍 Real-World Applications**: Where you'd find this in nature/engineering
- **💡 Interesting Facts**: Fascinating mathematical insights

## 🔍 **Example API Response**

```json
{
  "status": "success",
  "type": "3D",
  "data": {
    "image": "data:image/png;base64,iVBOR...",
    "expression": "r = 2*cos(4θ)",
    "analysis": {
      "type": "3D Surface of Revolution from Polar Curve",
      "petals": "8 petals",
      "max_radius": "2.00"
    },
    "ai_explanation": {
      "full_explanation": "Detailed mathematical explanation...",
      "mathematical_foundation": "This is a rose curve equation...",
      "visualization_description": "The 3D surface shows...",
      "key_properties": "This curve exhibits...",
      "real_world_applications": "Rose curves appear in...",
      "interesting_facts": "Fascinating properties include...",
      "ai_powered": true
    }
  }
}
```

## 🛠️ **Troubleshooting**

### No AI Explanations?
- Check if GEMINI_API_KEY is set correctly
- Verify API key is valid at Google AI Studio
- Check console for error messages

### API Quota Exceeded?
- Gemini has free tier limits
- Monitor your usage at Google AI Studio
- Consider upgrading if needed

### Import Errors?
```bash
pip install --upgrade google-generativeai
```

## 🎯 **Usage Tips**

1. **API Key Security**: Never commit your API key to version control
2. **Rate Limits**: Gemini has usage limits - cache responses if needed
3. **Error Handling**: The system gracefully falls back if AI is unavailable
4. **Customization**: Modify the prompts in `generate_ai_explanation()` for different explanation styles

## 🔄 **Restart Your Server**

After setting up the API key:
```bash
cd "/home/just-hakku/Desktop/MCA/SEM 3/Mini Project/Base project/full-graph-ui-react-app"
GEMINI_API_KEY="your_key_here" python3 backend/app.py
```

Now your 3D models will include detailed AI-powered mathematical explanations! 🎉
