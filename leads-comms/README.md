# Lead Communications Agent

An intelligent cold messaging system that uses Gemini AI to have conversations with potential customers and identify interested leads.

## Features

- 🤖 AI-powered conversations using Google's Gemini API
- 💬 Sequential client engagement with intelligent responses
- ✅ Automatic potential lead identification
- 📊 Real-time dashboard with conversation tracking
- 📁 Demo data included for quick testing
- 📝 Exports potential leads to text file

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. Add your API key to the `.env` file:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## How to Use

### Step 1: Set Sales Context
- Provide context about your product/service to help the AI agent conduct relevant conversations
- Example: "We are selling an AI-powered CRM solution that helps businesses automate their sales process..."

### Step 2: Load Clients
- Click "Load Demo Clients" to use the provided sample data (5 clients)
- Or upload your own JSON file with client information

### Step 3: Start Conversations
- Click "Start Conversations" to begin
- The agent will:
  1. Ask each client if they want to CONTINUE or STOP
  2. If CONTINUE, engage in conversation to assess interest
  3. Identify potential leads automatically
  4. Move to the next client sequentially

### Features During Conversation:
- Quick reply buttons for CONTINUE/STOP
- Real-time chat interface
- Skip client option
- Automatic progression to next client
- Potential lead highlighting

## Client JSON Format

```json
{
  "clients": [
    {
      "client_id": "CLIENT_001",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1-555-0101",
      "company": "Example Corp",
      "industry": "Technology",
      "role": "CTO"
    }
  ]
}
```

## Output

After processing all clients, the system generates a text file named `potential_leads_YYYYMMDD_HHMMSS.txt` containing:
- Client ID
- Name
- Email
- Phone
- Company
- Industry
- Conversation summary

## Tech Stack

- **Backend**: Flask (Python)
- **AI**: Google Gemini API
- **Frontend**: HTML, CSS, JavaScript
- **API**: RESTful endpoints

## API Endpoints

- `POST /api/set-context` - Set sales agent context
- `POST /api/load-demo` - Load demo clients
- `POST /api/load-clients` - Load custom client data
- `POST /api/start-conversation` - Start conversation with current client
- `POST /api/send-message` - Send message and get AI response
- `POST /api/skip-client` - Skip current client
- `GET /api/status` - Get current system status

## Notes

- The system uses unique client IDs instead of actual phone numbers
- Conversations are processed sequentially, one client at a time
- All potential leads are automatically saved to a text file
- The AI agent is trained to be professional and assess customer interest naturally
