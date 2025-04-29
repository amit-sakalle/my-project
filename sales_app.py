import json
import logging
import traceback
import random
from flask import Flask, render_template, request, jsonify

# --- Basic Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Placeholder for CRM/Data (Expanded with more fields including reasons/lessons) ---
MOCK_CRM_DATA = {
    "alpha_corp": {
        "display_name": "Alpha Corp", "contact": "John Doe", "status": "Prospecting", "value": "$50,000",
        "last_contact": "2024-03-15", "industry": "Manufacturing", "products_interested": ["ERP Solution", "Supply Chain Module"],
        "potential_needs": "Streamlining production workflow.", "next_step_suggestion": "Schedule discovery call to detail ERP benefits.",
        "reason_for_status": None, "lessons_learned": None
    },
    "beta_solutions": {
        "display_name": "Beta Solutions", "contact": "Jane Smith", "status": "Negotiation", "value": "$120,000",
        "last_contact": "2024-04-01", "industry": "Software Development", "products_interested": ["Cloud Hosting", "API Gateway"],
        "potential_needs": "Scalable infrastructure for new product launch.", "next_step_suggestion": "Finalize pricing and SLA terms.",
        "reason_for_status": "Currently negotiating final terms, price sensitivity is a factor.", "lessons_learned": None
    },
    "gamma_tech": {
        "display_name": "Gamma Tech", "contact": "Peter Jones", "status": "Closed Won", "value": "$75,000",
        "last_contact": "2024-01-20", "industry": "Biotechnology", "products_interested": ["Data Analytics Platform"],
        "potential_needs": "Analyzing research data.", "next_step_suggestion": "Onboarding and training.",
        "reason_for_status": "Strong value proposition on data processing speed and accuracy.", "lessons_learned": "Highlighting specific performance metrics was key during demos."
    },
    "delta_industries": {
        "display_name": "Delta Industries", "contact": "Alice Brown", "status": "Lead", "value": "$25,000",
        "last_contact": "2024-04-10", "industry": "Construction", "products_interested": ["Project Management Software"],
        "potential_needs": "Better tracking of project timelines and resources.", "next_step_suggestion": "Send initial info pack and case studies.",
        "reason_for_status": None, "lessons_learned": None
    },
    "omega_systems": {
        "display_name": "Omega Systems", "contact": "Robert Green", "status": "Qualified Lead", "value": "$90,000",
        "last_contact": "2024-04-05", "industry": "Finance", "products_interested": ["Cybersecurity Audit", "Compliance Suite"],
        "potential_needs": "Meeting new regulatory requirements.", "next_step_suggestion": "Prepare detailed proposal based on audit scope.",
        "reason_for_status": "Confirmed need and budget, awaiting formal proposal.", "lessons_learned": None
    },
    "sigma_solutions": {
        "display_name": "Sigma Solutions", "contact": "Mary White", "status": "Proposal Sent", "value": "$200,000",
        "last_contact": "2024-03-28", "industry": "Logistics", "products_interested": ["Fleet Management System", "Route Optimization"],
        "potential_needs": "Reducing fuel costs and improving delivery times.", "next_step_suggestion": "Follow up on proposal feedback next week.",
        "reason_for_status": "Proposal under review by client's technical team.", "lessons_learned": None
    },
    "epsilon_enterprises": {
        "display_name": "Epsilon Enterprises", "contact": "David Black", "status": "Closed Lost", "value": "$40,000",
        "last_contact": "2024-02-11", "industry": "Retail", "products_interested": ["POS System Upgrade"],
        "potential_needs": "Modernizing checkout process.", "next_step_suggestion": "Review reasons for loss, check back in 6 months.",
        "reason_for_status": "Lost to competitor due to lower price point.", "lessons_learned": "Need to better articulate long-term value vs upfront cost for budget-conscious retail clients."
    },
    "zeta_global": {
        "display_name": "Zeta Global", "contact": "Sarah King", "status": "Prospecting", "value": "$65,000",
        "last_contact": "2024-04-15", "industry": "Telecommunications", "products_interested": ["Network Monitoring Tools"],
        "potential_needs": "Improving network reliability.", "next_step_suggestion": "Qualify further - understand current monitoring setup.",
        "reason_for_status": None, "lessons_learned": None
    }
}

# --- Simplified Chatbot Logic ---

def get_lead_info_simple(lead_key, requested_field=None):
    """
    Retrieves and formats information for a given lead key from the mock CRM data.
    Can return a specific field or a full summary.
    Args:
        lead_key (str): The snake_case key of the lead.
        requested_field (str, optional): The specific field key (e.g., 'status', 'reason_for_status') to retrieve. Defaults to None.
    Returns:
        tuple: A formatted response string and the raw data/value, or (error_message, None) if not found.
    """
    if lead_key not in MOCK_CRM_DATA:
        logging.warning(f"get_lead_info_simple called with invalid key: {lead_key}")
        display_name_guess = lead_key.replace("_", " ").title()
        return f"Sorry, couldn't find information for '{display_name_guess}'.", None

    info = MOCK_CRM_DATA[lead_key]
    display_name = info.get("display_name", lead_key.replace("_", " ").title())

    # Map display-friendly field names back to data keys if needed
    field_map = {
        "reason for status": "reason_for_status",
        "lessons learned": "lessons_learned",
        "products interested": "products_interested",
        "potential needs": "potential_needs",
        "next step suggestion": "next_step_suggestion",
        "last contact": "last_contact",
        # Add other direct mappings if needed
        "status": "status", "contact": "contact", "value": "value", "industry": "industry"
    }
    data_key = field_map.get(requested_field, requested_field) # Use mapped key or original if not in map

    if data_key: # Check if a specific field (mapped or direct) was requested
        if data_key in info:
            value = info[data_key]
            if isinstance(value, list):
                value_str = ", ".join(value) if value else "N/A"
            else:
                # Use "Not specified" or similar for None values in specific fields
                value_str = str(value) if value is not None else "Not specified"

            # Use the requested_field name (more user-friendly) in the response
            field_display_name = requested_field.replace('_', ' ') if requested_field else data_key.replace('_', ' ')
            formatted_response = f"The <b>{field_display_name}</b> for <b>{display_name}</b> is: {value_str}"
            return formatted_response, value
        else:
            logging.warning(f"Requested field '{data_key}' (from '{requested_field}') not found for lead '{lead_key}'")
            field_display_name = requested_field.replace('_', ' ') if requested_field else data_key.replace('_', ' ')
            return f"Sorry, I don't have the field '<b>{field_display_name}</b>' for <b>{display_name}</b>.", None
    else:
        # Format the full summary including new fields, handling None values gracefully
        formatted_response = (
            f"Found info for '<b>{display_name}</b>':<br>"
            f"&nbsp;&nbsp;Contact: {info.get('contact', 'N/A')}<br>"
            f"&nbsp;&nbsp;Status: {info.get('status', 'N/A')}<br>"
            f"&nbsp;&nbsp;Deal Value: {info.get('value', 'N/A')}<br>"
            f"&nbsp;&nbsp;Last Contact: {info.get('last_contact', 'N/A')}<br>"
            f"&nbsp;&nbsp;Industry: {info.get('industry', 'N/A')}<br>"
            f"&nbsp;&nbsp;Products Interested: {', '.join(info.get('products_interested', [])) or 'N/A'}<br>"
            f"&nbsp;&nbsp;Potential Needs: {info.get('potential_needs', 'N/A')}<br>"
            f"&nbsp;&nbsp;Reason for Status: {info.get('reason_for_status') or 'Not specified'}<br>"
            f"&nbsp;&nbsp;Lessons Learned: {info.get('lessons_learned') or 'Not specified'}<br>"
            f"&nbsp;&nbsp;Next Step Suggestion: {info.get('next_step_suggestion', 'N/A')}"
        )
        return formatted_response, info

# --- Sample Questions Generator ---
def get_example_questions(num_questions=2):
    """Generates a few example questions based on CRM data."""
    examples = []
    if not MOCK_CRM_DATA: return ""

    lead_keys = list(MOCK_CRM_DATA.keys())
    # Include new fields in options
    field_options = ["status", "contact", "industry", "value", "next step suggestion", "reason for status", "lessons learned"]

    num_questions = min(num_questions, len(lead_keys))
    selected_keys = random.sample(lead_keys, num_questions)

    for key in selected_keys:
        display_name = MOCK_CRM_DATA[key].get("display_name", key.replace("_", " ").title())
        field = random.choice(field_options)
        # Generate varied question formats
        q_formats = [
            f"What is the {field} of {display_name}?",
            f"Tell me the {field} for {display_name}.",
        ]
        if field == "contact": q_formats.append(f"Who is the contact for {display_name}?")
        if field == "next step suggestion": q_formats.append(f"What is the next step for {display_name}?")
        if field == "reason for status": q_formats.append(f"Why is {display_name} {MOCK_CRM_DATA[key].get('status', '')}?") # Add status context
        if field == "lessons learned": q_formats.append(f"What lessons learned from {display_name}?")

        examples.append(random.choice(q_formats))
        # Add a general info request example sometimes
        if random.random() < 0.4: # Add general query less often
             examples.append(f"Tell me about {display_name}.")

    final_examples = random.sample(list(set(examples)), min(len(set(examples)), num_questions + 1)) # Unique examples

    if not final_examples: return ""
    return "<br><br>You can ask things like:<br>" + "<br>".join([f"&nbsp;&nbsp;- <i>{ex}</i>" for ex in final_examples])


def handle_greeting():
    """Generates a greeting response including example questions."""
    greeting = "Hello! Sales Assistant bot here. How can I help you today?"
    examples = get_example_questions(2)
    return greeting + examples

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
        info_keywords = {"info", "information", "detail", "tell", "find", "show", "lookup", "about", "update", "what is", "what's", "who is", "who's", "why"} # Added 'why'
        # Keywords for specific fields (map input keywords to display-friendly field names used in get_lead_info_simple)
        field_keywords = {
            "status": ["status", "stage", "progress"],
            "contact": ["contact", "person", "who", "name"],
            "value": ["value", "deal size", "amount", "worth"],
            "last contact": ["last contact", "last contacted", "when talk"], # Use display name
            "industry": ["industry", "sector", "business type"],
            "products interested": ["products", "interested in", "services"], # Use display name
            "potential needs": ["needs", "requirements", "pain points"], # Use display name
            "reason for status": ["reason", "why"], # Use display name
            "lessons learned": ["lessons", "learned", "takeaway"], # Use display name
            "next step suggestion": ["next step", "what next", "suggestion", "plan"] # Use display name
        }

        if any(keyword in user_input_lower for keyword in greeting_keywords):
            return handle_greeting()
        if any(keyword in user_input_lower for keyword in farewell_keywords):
            return handle_farewell()

        is_info_request = any(keyword in user_input_lower for keyword in info_keywords)
        found_lead_key = None
        requested_field = None # This will store the display-friendly field name

        sorted_keys = sorted(MOCK_CRM_DATA.keys(), key=lambda k: len(MOCK_CRM_DATA[k].get("display_name", "")), reverse=True)

        for key in sorted_keys:
            data = MOCK_CRM_DATA[key]
            display_name_lower = data.get("display_name", "").lower()
            if display_name_lower and display_name_lower in user_input_lower:
                found_lead_key = key
                logging.info(f"Found company match: '{display_name_lower}' in input maps to key '{key}'")
                break
            if not found_lead_key and key.replace("_", " ") in user_input_lower:
                 found_lead_key = key
                 logging.info(f"Found company match by key: '{key}' in input")
                 break

        if found_lead_key:
            # Check for specific field requests using the display-friendly names as keys
            for field_display_name, keywords in field_keywords.items():
                if any(kw in user_input_lower for kw in keywords):
                    # Basic check to avoid matching 'name' keyword to 'display_name' field
                    if field_display_name == "contact" and "name" in keywords and "company name" in user_input_lower:
                        continue
                    requested_field = field_display_name # Store the display-friendly name
                    logging.info(f"Found requested field: '{requested_field}' based on keywords: {keywords}")
                    break

            # Pass the display-friendly field name to get_lead_info_simple
            formatted_response, lead_data_or_value = get_lead_info_simple(found_lead_key, requested_field)

            # Add general follow-up only if returning full summary (requested_field is None) and data was found
            if not requested_field and lead_data_or_value:
                status = lead_data_or_value.get("status", "").lower()
                # Follow-up logic remains the same, using internal status keys
                status_followups = {
                    "prospecting": "What's our next step to qualify them?",
                    "lead": "What information do we need to qualify them further?",
                    "qualified lead": "What's the strategy to move them towards a proposal?",
                    "negotiation": "What are the key points to address to close this deal?",
                    "proposal sent": "When is the follow-up scheduled, or what feedback have we received?",
                    "closed won": "Great job! What were the key factors to success here?",
                    "closed lost": "What were the main reasons this deal was lost, and what can we learn?"
                }
                follow_up = status_followups.get(status, "What's the next planned action for this lead?")
                if follow_up:
                    # Check if the specific follow-up question is already answered by the data
                    already_answered = False
                    if status == "closed lost" and lead_data_or_value.get("reason_for_status"):
                        already_answered = True
                    if status == "closed won" and lead_data_or_value.get("lessons_learned"):
                         already_answered = True
                    # Only add the follow-up if it provides additional value
                    if not already_answered:
                        formatted_response += f"<br><br><i>{follow_up}</i>"

            return formatted_response

        elif is_info_request:
            logging.warning(f"Info request detected, but no matching lead name found in input: '{user_input}'")
            examples = get_example_questions(1)
            return f"It sounds like you're asking for information, but I couldn't identify a company name from my records in your message. Please mention the company name clearly.{examples}"

        # --- Fallback: Unknown Intent ---
        logging.info(f"Input not recognized as greeting, farewell, or info request: '{user_input}'")
        examples = get_example_questions(2)
        return f"Sorry, I didn't quite understand that.{examples}"

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

    bot_response = process_user_input_simple(user_message)
    return jsonify({"response": bot_response})

# --- Run the App ---
if __name__ == "__main__":
    logging.info("Starting Flask development server (use WSGI for production)...")
    app.run(debug=False, host='0.0.0.0', port=5000)
