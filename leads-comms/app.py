import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables!")
else:
    print("✓ Gemini API Key loaded successfully")
genai.configure(api_key=GEMINI_API_KEY)

# Global state
current_state = {
    'clients': [],
    'current_index': 0,
    'sales_context': '',
    'conversation_history': {},
    'potential_leads': []
}

def save_potential_leads():
    """Save potential leads to a text file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"potential_leads_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("POTENTIAL CONSUMERS\n")
        f.write("=" * 60 + "\n\n")
        
        if not current_state['potential_leads']:
            f.write("No potential consumers identified.\n")
        else:
            for lead in current_state['potential_leads']:
                f.write(f"Client ID: {lead['client_id']}\n")
                f.write(f"Name: {lead['name']}\n")
                f.write(f"Email: {lead['email']}\n")
                f.write(f"Phone: {lead['phone']}\n")
                f.write(f"Company: {lead['company']}\n")
                f.write(f"Industry: {lead['industry']}\n")
                f.write(f"Conversation Summary: {lead.get('summary', 'N/A')}\n")
                f.write("-" * 60 + "\n\n")
    
    return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/set-context', methods=['POST'])
def set_context():
    """Set the sales context for the agent"""
    data = request.json
    current_state['sales_context'] = data.get('context', '')
    return jsonify({'success': True, 'message': 'Context set successfully'})

@app.route('/api/load-clients', methods=['POST'])
def load_clients():
    """Load clients from uploaded JSON file"""
    try:
        data = request.json
        clients = data.get('clients', [])
        
        if not clients:
            return jsonify({'success': False, 'message': 'No clients found in file'})
        
        current_state['clients'] = clients
        current_state['current_index'] = 0
        current_state['conversation_history'] = {}
        current_state['potential_leads'] = []
        
        return jsonify({
            'success': True,
            'message': f'Loaded {len(clients)} clients',
            'total_clients': len(clients)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/load-demo', methods=['POST'])
def load_demo():
    """Load demo clients from file"""
    try:
        with open('demo_clients.json', 'r') as f:
            data = json.load(f)
            clients = data.get('clients', [])
        
        current_state['clients'] = clients
        current_state['current_index'] = 0
        current_state['conversation_history'] = {}
        current_state['potential_leads'] = []
        
        return jsonify({
            'success': True,
            'message': f'Loaded {len(clients)} demo clients',
            'total_clients': len(clients)
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/start-conversation', methods=['POST'])
def start_conversation():
    """Start conversation with current client"""
    if not current_state['sales_context']:
        return jsonify({'success': False, 'message': 'Please set sales context first'})
    
    if not current_state['clients']:
        return jsonify({'success': False, 'message': 'No clients loaded'})
    
    if current_state['current_index'] >= len(current_state['clients']):
        # Save potential leads and finish
        filename = save_potential_leads()
        return jsonify({
            'success': True,
            'finished': True,
            'message': f'All clients processed. Results saved to {filename}',
            'total_potential_leads': len(current_state['potential_leads'])
        })
    
    client = current_state['clients'][current_state['current_index']]
    client_id = client['client_id']
    
    # Initialize conversation for this client
    initial_message = f"""Hello! I'm reaching out to discuss an opportunity that might interest you. 
    
Would you like to continue this conversation or would you prefer I don't contact you further? 
Please reply with 'CONTINUE' to proceed or 'STOP' to end this conversation."""
    
    current_state['conversation_history'][client_id] = [
        {'role': 'agent', 'content': initial_message}
    ]
    
    return jsonify({
        'success': True,
        'client': client,
        'message': initial_message,
        'current_index': current_state['current_index'],
        'total_clients': len(current_state['clients'])
    })

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Send a message and get AI response"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        client_id = data.get('client_id')
        
        if not client_id or client_id not in current_state['conversation_history']:
            return jsonify({'success': False, 'message': 'Invalid conversation'})
        
        # Add user message to history
        current_state['conversation_history'][client_id].append({
            'role': 'user',
            'content': user_message
        })
        
        # Check if user wants to stop
        if 'STOP' in user_message.upper():
            current_state['current_index'] += 1
            return jsonify({
                'success': True,
                'stopped': True,
                'message': 'Thank you for your time. Have a great day!',
                'next_client': current_state['current_index'] < len(current_state['clients'])
            })
        
        # Check if this is the first response (CONTINUE)
        if len(current_state['conversation_history'][client_id]) == 2:
            if 'CONTINUE' not in user_message.upper():
                # If they didn't say continue, treat it as stop
                current_state['current_index'] += 1
                return jsonify({
                    'success': True,
                    'stopped': True,
                    'message': 'Thank you for your time. Have a great day!',
                    'next_client': current_state['current_index'] < len(current_state['clients'])
                })
        
        # Get current client
        client = current_state['clients'][current_state['current_index']]
        
        # Create context for Gemini
        conversation_context = f"""You are a sales agent. Your context: {current_state['sales_context']}

You are talking to:
Name: {client['name']}
Company: {client['company']}
Industry: {client['industry']}

Conversation history:
"""
        for msg in current_state['conversation_history'][client_id]:
            role = "Agent" if msg['role'] == 'agent' else "Client"
            conversation_context += f"{role}: {msg['content']}\n"
        
        conversation_context += f"""\nInstructions:
1. Engage in a natural conversation to understand if they might be interested in our offering
2. Be professional but friendly
3. Ask relevant questions to gauge their interest
4. Keep responses concise (2-3 sentences max)
5. If you determine they are a potential customer (showing interest, asking questions, wanting more info), respond with your message followed by [POTENTIAL_YES]
6. If you determine they are not interested or not a good fit, respond with your message followed by [POTENTIAL_NO]
7. Don't include the tags in your visible response, they're for system use only

Client's response: {user_message}

Your response:"""
        
        # Get response from Gemini
        try:
            print(f"\n{'='*60}")
            print("Sending request to Gemini API...")
            print(f"Client: {client['name']}")
            print(f"User message: {user_message}")
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(conversation_context)
            ai_response = response.text
            
            print(f"Gemini response received: {ai_response[:100]}...")
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"\n❌ ERROR calling Gemini API: {str(e)}\n")
            return jsonify({
                'success': False, 
                'message': f'Error calling AI: {str(e)}'
            })
        
        # Check for potential tags
        is_potential = False
        should_end = False
        
        if '[POTENTIAL_YES]' in ai_response:
            is_potential = True
            should_end = True
            ai_response = ai_response.replace('[POTENTIAL_YES]', '').strip()
            # Add to potential leads
            current_state['potential_leads'].append({
                **client,
                'summary': user_message
            })
        elif '[POTENTIAL_NO]' in ai_response:
            should_end = True
            ai_response = ai_response.replace('[POTENTIAL_NO]', '').strip()
        
        # Add AI response to history
        current_state['conversation_history'][client_id].append({
            'role': 'agent',
            'content': ai_response
        })
        
        if should_end:
            current_state['current_index'] += 1
            
            # Check if all clients are done and generate report
            if current_state['current_index'] >= len(current_state['clients']):
                filename = save_potential_leads()
                return jsonify({
                    'success': True,
                    'message': ai_response,
                    'is_potential': is_potential,
                    'conversation_ended': should_end,
                    'all_done': True,
                    'report_file': filename,
                    'total_potential_leads': len(current_state['potential_leads']),
                    'next_client': False
                })
        
        return jsonify({
            'success': True,
            'message': ai_response,
            'is_potential': is_potential,
            'conversation_ended': should_end,
            'next_client': current_state['current_index'] < len(current_state['clients'])
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/skip-client', methods=['POST'])
def skip_client():
    """Skip current client and move to next"""
    current_state['current_index'] += 1
    return jsonify({
        'success': True,
        'next_client': current_state['current_index'] < len(current_state['clients'])
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current status"""
    return jsonify({
        'clients_loaded': len(current_state['clients']),
        'current_index': current_state['current_index'],
        'context_set': bool(current_state['sales_context']),
        'potential_leads': len(current_state['potential_leads'])
    })

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Manually generate the potential leads report"""
    filename = save_potential_leads()
    return jsonify({
        'success': True,
        'filename': filename,
        'total_potential_leads': len(current_state['potential_leads']),
        'message': f'Report generated: {filename}'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
