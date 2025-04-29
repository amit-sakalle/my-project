import json
import logging
import traceback
from flask import Flask, render_template, request, jsonify

# --- Basic Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize Flask App ---
app = Flask(__name__)

# --- NLTK Download Removed ---

# --- Placeholder for CRM/Data (Expanded) ---
MOCK_CRM_DATA = {
    # Using snake_case for consistent key format, which we'll match against
    "alpha_corp": {"contact": "John Doe", "status": "Prospecting", "value": "$50,000", "last_contact": "2024-03-15", "display_name": "Alpha Corp"},
    "beta_solutions": {"contact": "Jane Smith", "status": "Negotiation", "value": "$120,000", "last_contact": "2024-04-01", "display_name": "Beta Solutions"},
    "gamma_tech": {"contact": "Peter Jones", "status": "Closed Won", "value": "$75,000", "last_contact": "2024-01-20", "display_name": "Gamma Tech"},
    "delta_industries": {"contact": "Alice Brown", "status": "Lead", "value": "$25,000", "last_contact": "2024-04-10", "display_name": "Delta Industries"},
    "omega_systems": {"contact": "Robert Green", "status": "Qualified Lead", "value": "$90,000", "last_contact": "2024-04-05", "display_name": "Omega Systems"},
    "sigma_solutions": {"contact": "Mary White", "status": "Proposal Sent", "value": "$200,000", "last_contact": "2024-03-28", "display_name": "Sigma Solutions"},
    "epsilon_enterprises": {"contact": "David Black", "status": "Closed Lost", "value": "$40,000", "last_contact": "2024-02-11", "display_name": "Epsilon Enterprises"},
    "zeta_global": {"contact": "Sarah King", "status": "Prospecting", "value": "$65,000", "last_contact": "2024-04-15", "display_name": "Zeta Global"}
}
# Added display_name for easier reference back

# --- Simplified Chatbot Logic ---

def get_lead_info_simple(lead_key):
    """
    Retrieves and formats information for a given lead key from the mock CRM data.
    Args:
        lead_key (str): The snake_case key of the lead.
    Returns:
        tuple: A formatted response string and the raw data, or None if not found.
    """
    if lead_key in MOCK_CRM_DATA:
        info = MOCK_CRM_DATA[lead_key]
        display_name = info.get("display_name", lead_key.replace("_", " ").title()) # Use display name or format key
        formatted_response = (
            f"Found info for '<b>{display_name}</b>':<br>"
            f"&nbsp;&nbsp;Contact: {info.get('contact', 'N/A')}<br>"
            f"&nbsp;&nbsp;Status: {info.get('status', 'N/A')}<br>"
            f"&nbsp;&nbsp;Deal Value: {info.get('value', 'N/A')}<br>"
            f"&nbsp;&nbsp;Last Contact: {info.get('last_contact', 'N/A')}"
        )
        return formatted_response, info
    else:
        # This function now expects a valid key, so this path shouldn't normally be hit
        # if called correctly from process_user_input_simple
        logging.warning(f"get_lead_info_simple called with invalid key: {lead_key}")
        return f"Sorry, couldn't find information for key '{lead_key}'.", None

def handle_greeting():
    """Generates a greeting response."""
    return "Hello! Sales Assistant bot here. How can I help you today?"

def handle_farewell():
    """Generates a farewell response."""
    return "Goodbye! Happy selling!"

def process_user_input_simple(user_input):
    """
    Analyzes user input using simple keyword matching.
    Returns the appropriate response string (HTML formatted where needed).
    """
    try:
        if not isinstance(user_input, str) or not user_input.strip():
            logging.warning("Empty or whitespace-only input received.")
            return "Please provide some input."

        logging.info(f"Processing user input: {user_input}")
        user_input_lower = user_input.lower().strip()

        # --- Basic Intent Recognition ---
        greeting_keywords = {"hello", "hi", "hey", "yo", "greeting", "morning", "afternoon", "evening"}
        farewell_keywords = {"bye", "goodbye", "exit", "quit", "see ya", "later"}
        info_keywords = {"info", "information", "status", "detail", "tell", "find", "show", "lookup", "about", "update", "what is", "what's"}

        # Check for greetings/farewells first
        if any(keyword in user_input_lower.split() for keyword in greeting_keywords):
            return handle_greeting()
        if any(keyword in user_input_lower.split() for keyword in farewell_keywords):
            return handle_farewell()

        # --- Information Request & Entity Extraction ---
        is_info_request = any(keyword in user_input_lower for keyword in info_keywords)

        if is_info_request:
            found_lead_key = None
            # Iterate through CRM keys and check if the display name (or parts of it) are in the user input
            for key, data in MOCK_CRM_DATA.items():
                display_name_lower = data.get("display_name", "").lower()
                # Check if the full display name is present
                if display_name_lower and display_name_lower in user_input_lower:
                    found_lead_key = key
                    logging.info(f"Found potential match: '{display_name_lower}' in input maps to key '{key}'")
                    break # Take the first full match

                # Optional: Check if the key itself (e.g., "alpha_corp") is in the input
                # This is less likely but could be a fallback
                if not found_lead_key and key.replace("_", " ") in user_input_lower:
                     found_lead_key = key
                     logging.info(f"Found potential match by key: '{key}' in input")
                     break


            if found_lead_key:
                formatted_response, lead_data = get_lead_info_simple(found_lead_key)

                # Add follow-up question based on status (optional enhancement)
                if lead_data:
                    status = lead_data.get("status", "").lower()
                    follow_up_question = ""
                    # (Follow-up logic remains the same as before)
                    status_followups = {
                        "prospecting": "What's our next step to qualify them?",
                        "lead": "What information do we need to qualify them further?",
                        "qualified lead": "What's the strategy to move them towards a proposal?",
                        "negotiation": "What are the key points to address to close this deal?",
                        "proposal sent": "When is the follow-up scheduled, or what feedback have we received?",
                        "closed won": "Great job! What were the key factors to success here?",
                        "closed lost": "What were the main reasons this deal was lost, and what can we learn?"
                    }
                    follow_up_question = status_followups.get(status, "What's the next planned action for this lead?")
                    if follow_up_question:
                        formatted_response += f"<br><br><i>{follow_up_question}</i>"

                return formatted_response
            else:
                # Info request keywords present, but no matching company name found
                logging.warning(f"Info request detected, but no matching lead name found in input: '{user_input}'")
                return "It sounds like you're asking for lead information, but I couldn't identify a company name from my records in your message. Please mention the company name clearly (e.g., 'status for Alpha Corp')."

        # --- Fallback: Unknown Intent ---
        return ("Sorry, I didn't quite understand that. You can ask things like: "
                "'What's the status of Beta Solutions?', 'Tell me about Gamma Tech', "
                "'hello', or 'bye'.")

    except Exception as e:
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
        logging.warning("Received POST request with no message.")
        return jsonify({"error": "No message received"}), 400

    # Process the message using the SIMPLIFIED function
    bot_response = process_user_input_simple(user_message)

    # Return the bot's response as JSON
    return jsonify({"response": bot_response})

# --- Run the App ---
if __name__ == "__main__":
    # Use Waitress for production: waitress-serve --host 0.0.0.0 --port 5000 sales_app:app
    logging.info("Starting Flask development server (use WSGI for production)...")
    app.run(debug=False, host='0.0.0.0', port=5000)
