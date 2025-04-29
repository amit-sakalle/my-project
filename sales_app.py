import json
import nltk # Added NLTK import
import logging # Added logging import
import traceback # Added traceback import
# Removed spaCy import
# Removed re import (will replace regex logic)
from flask import Flask, render_template, request, jsonify

# --- Basic Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Download NLTK Resources (Run once at startup) ---
try:
    # Added 'punkt_tab' which is needed by word_tokenize internally
    nltk_resources = ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
    for resource in nltk_resources:
        logging.info(f"Ensuring NLTK resource '{resource}' is available...")
        nltk.download(resource, quiet=True)
    logging.info("NLTK resources checked/downloaded.")
except Exception as e:
    logging.error(f"Failed to download NLTK resources during startup: {str(e)}\n{traceback.format_exc()}", exc_info=False)
    # Depending on the deployment, you might want to exit here if NLTK is critical
    # raise SystemExit("Critical NLTK resources failed to download.")

# --- spaCy model loading removed ---

# --- Placeholder for CRM/Data (Expanded) ---
MOCK_CRM_DATA = {
    # Using snake_case for consistent key format
    "alpha_corp": {"contact": "John Doe", "status": "Prospecting", "value": "$50,000", "last_contact": "2024-03-15"},
    "beta_solutions": {"contact": "Jane Smith", "status": "Negotiation", "value": "$120,000", "last_contact": "2024-04-01"},
    "gamma_tech": {"contact": "Peter Jones", "status": "Closed Won", "value": "$75,000", "last_contact": "2024-01-20"},
    "delta_industries": {"contact": "Alice Brown", "status": "Lead", "value": "$25,000", "last_contact": "2024-04-10"},
    "omega_systems": {"contact": "Robert Green", "status": "Qualified Lead", "value": "$90,000", "last_contact": "2024-04-05"},
    "sigma_solutions": {"contact": "Mary White", "status": "Proposal Sent", "value": "$200,000", "last_contact": "2024-03-28"},
    "epsilon_enterprises": {"contact": "David Black", "status": "Closed Lost", "value": "$40,000", "last_contact": "2024-02-11"},
    "zeta_global": {"contact": "Sarah King", "status": "Prospecting", "value": "$65,000", "last_contact": "2024-04-15"}
}
# --- End Placeholder ---

# --- Chatbot Logic Functions ---

# --- Input Handling Functions ---
def validate_input(user_input):
    """
    Validates that the input is a non-empty string.
    
    Args:
        user_input (str): The input to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(user_input, str) or not user_input.strip():
        return False
    return True

# --- Lead Management Functions ---
def get_lead_info(lead_name):
    """
    Retrieves and formats information for a given lead from the mock CRM data.
    
    Args:
        lead_name (str): The name of the lead to retrieve information for.
        
    Returns:
        tuple: A formatted response string and the raw data, or None if not found.
    """
    # Normalize input by converting to lowercase and replacing spaces with underscores
    lead_key = lead_name.lower().replace(" ", "_")
    
    if lead_key in MOCK_CRM_DATA:
        logging.debug(f"Found exact match for lead '{lead_name}' with key: {lead_key}")
        info = MOCK_CRM_DATA[lead_key]
        formatted_response = (
            f"Found info for '<b>{lead_name}</b>':<br>"
            f"&nbsp;&nbsp;Contact: {info.get('contact', 'N/A')}<br>"
            f"&nbsp;&nbsp;Status: {info.get('status', 'N/A')}<br>"
            f"&nbsp;&nbsp;Deal Value: {info.get('value', 'N/A')}<br>"
            f"&nbsp;&nbsp;Last Contact: {info.get('last_contact', 'N/A')}"
        )
        return formatted_response, info
    else:
        # Check for close matches (case-insensitive and space-agnostic)
        potential_matches = [
            key.replace("_", " ").title() 
            for key in MOCK_CRM_DATA.keys()
            if lead_name.lower().replace(" ", "_") == key
        ]
        
        logging.info(f"Searching for lead '{lead_name}' with normalized key: {lead_key}")
        logging.debug(f"Potential matches found: {potential_matches}")
        
        if potential_matches:
            formatted_response = f"Did you mean '<b>{', '.join(potential_matches)}</b>'?"
            logging.debug(f"Found potential matches for '{lead_name}': {potential_matches}")
        else:
            formatted_response = (
                f"Sorry, I couldn't find any information for a lead named '<b>{lead_name}</b>'. "
                "Please check the spelling or provide more details."
            )
            logging.warning(f"No matching lead found for query: '{lead_name}'")

        return formatted_response, None

# --- Response Generation Functions ---
def handle_greeting():
    """Generates a greeting response."""
    return "Hello! Sales Assistant bot here. How can I help you today?"

def handle_farewell():
    """Generates a farewell response."""
    return "Goodbye! Happy selling!"

# --- NLTK-based Processing Function ---
def process_user_input_nltk(user_input):
    """
    Analyzes user input using NLTK for tokenization, POS tagging, and NER.
    Returns the appropriate response string (HTML formatted where needed).
    """
    try:
        # Validate input
        if not isinstance(user_input, str):
            logging.error("Invalid input type. Input must be a string.")
            raise TypeError("Input must be a string.")
            
        if not user_input.strip():
            logging.warning("Empty or whitespace-only input received.") # Changed to warning
            # No need to raise ValueError here, can just return a message
            return "Please provide some input."

        # Log the received message for debugging purposes
        logging.info(f"Processing user input: {user_input}")

        # NLTK resources are now downloaded at startup

        user_input_lower = user_input.lower()
        tokens = nltk.word_tokenize(user_input)
        tagged_tokens = nltk.pos_tag(tokens)

        # --- Basic Intent Recognition (using keywords in tokenized input) ---
        greeting_keywords = {"hello", "hi", "hey", "yo", "greeting", "morning", "afternoon", "evening"}
        farewell_keywords = {"bye", "goodbye", "exit", "quit", "see ya", "later"}
        info_keywords = {"info", "information", "status", "detail", "tell", "find", "show", "lookup", "about", "update"}

        token_set = set(t.lower() for t in tokens) # Use tokenized words for keyword check
        is_greeting = any(word in greeting_keywords for word in token_set)
        is_farewell = any(word in farewell_keywords for word in token_set)
        is_info_request = any(word in info_keywords for word in token_set)

        # Prioritize greeting/farewell
        if is_greeting:
            return handle_greeting()
        if is_farewell:
            return handle_farewell()

        # --- Entity Extraction & Info Intent (using NLTK NER) ---
        if is_info_request:
            lead_name = None
            # Use NLTK's Named Entity Recognition (NER)
            # This creates a tree structure where subtrees labeled 'ORGANIZATION' or 'GPE' (Geo-Political Entity, sometimes catches company names) are potential leads
            tree = nltk.ne_chunk(tagged_tokens)
            potential_leads = []
            for subtree in tree.subtrees():
                # Look for ORGANIZATION or GPE tags
                if hasattr(subtree, 'label') and subtree.label() in ['ORGANIZATION', 'GPE']:
                    # Join the words in the tagged subtree to form the name
                    entity_name = ' '.join([leaf[0] for leaf in subtree.leaves()])
                    potential_leads.append(entity_name)

            # Check if any extracted potential leads match our CRM data
            found_lead_data = None
            for potential_name in potential_leads:
                potential_name_lower = potential_name.lower()
                if potential_name_lower in MOCK_CRM_DATA:
                    lead_name = potential_name # Keep original casing
                    formatted_response, found_lead_data = get_lead_info(lead_name)
                    break # Stop after finding the first match

            # If a lead was found and data retrieved
            if found_lead_data:
                status = found_lead_data.get("status", "").lower()
                follow_up_question = ""
                # Define follow-up questions based on status
                status_followups = {
                    "prospecting": {
                        "question": "What's our next step to qualify them?",
                        "suggested_action": "Consider scheduling a discovery call or requesting more information."
                    },
                    "lead": {
                        "question": "What information do we need to qualify them further?",
                        "suggested_action": "Review the lead qualification criteria and gather missing details."
                    },
                    "qualified lead": {
                        "question": "What's the strategy to move them towards a proposal?",
                        "suggested_action": "Develop a tailored value proposition and prepare key talking points."
                    },
                    "negotiation": {
                        "question": "What are the key points to address to close this deal?",
                        "suggested_action": "Review outstanding objections and prepare negotiation strategies."
                    },
                    "proposal sent": {
                        "question": "When is the follow-up scheduled, or what feedback have we received?",
                        "suggested_action": "Follow up with the client for feedback and be prepared to address concerns."
                    },
                    "closed won": {
                        "question": "Great job! What were the key factors to success here?",
                        "suggested_action": "Document lessons learned and share successes with the team."
                    },
                    "closed lost": {
                        "question": "What were the main reasons this deal was lost, and what can we learn?",
                        "suggested_action": "Conduct a post-mortem analysis and identify areas for improvement."
                    }
                }
                
                # Get follow-up question based on status
                follow_up_question = status_followups.get(status.lower(), 
                    "What's the next planned action for this lead?")

                if follow_up_question:
                    formatted_response += f"<br><br><i>{follow_up_question}</i>"

                return formatted_response
            else:
                # If info keywords present but NER didn't find a match in CRM
                return "It sounds like you're asking for lead information, but I couldn't identify a matching company name from my records. Could you please clarify which lead (e.g., 'status for Alpha Corp')?"

        # --- Fallback: Unknown Intent ---
        return ("Sorry, I didn't quite understand that. You can ask things like: "
                "'What's the status of Beta Solutions?', 'Tell me about Gamma Tech', "
                "'hello', or 'bye'.")
    except Exception as e:
        # Log the error with detailed traceback information
        logging.error(f"Error processing user input: {str(e)}\n{traceback.format_exc()}", exc_info=False)
        return "An error occurred while processing your request. Please try again."

# --- Flask Routes ---
@app.route("/")
def home():
    """Serves the main chat page (index.html)."""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """Handles incoming chat messages via POST request."""
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message received"}), 400

    # Process the message using the NLTK function
    bot_response = process_user_input_nltk(user_message) # Changed function call

    # Return the bot's response as JSON
    return jsonify({"response": bot_response})

# --- Run the App ---
if __name__ == "__main__":
    # debug=False is recommended for production.
    # Use a production-ready WSGI server (like Gunicorn or Waitress)
    # instead of the Flask development server for deployment.
    # Example using Waitress (install with: pip install waitress):
    # waitress-serve --host 0.0.0.0 --port 5000 sales_app:app
    logging.info("Starting Flask development server (use WSGI for production)...")
    app.run(debug=False, host='0.0.0.0', port=5000) # Listen on all interfaces, DEBUG SET TO FALSE
