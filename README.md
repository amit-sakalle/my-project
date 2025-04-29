# Sales Chatbot Web Application

This is a simple Flask web application providing a chatbot interface for sales-related queries.

## Setup and Installation

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create a virtual environment:**
    It's highly recommended to use a virtual environment to manage dependencies.
    ```bash
    # For Windows
    python -m venv .venv
    .venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    Install the required Python packages using the `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```
    *Note: The first time you run the application, NLTK will download necessary data packages. This might take a moment.*

## Running the Application

### Development Server (Not for Production)

You can run the Flask development server for testing:
```bash
python sales_app.py
```
The application will be available at `http://localhost:5000` or `http://0.0.0.0:5000`.

### Production Server (Recommended)

For deployment, use a production-ready WSGI server like Waitress or Gunicorn.

**Using Waitress:**

1.  Install Waitress (if not already included in requirements, though it's good practice to add it):
    ```bash
    pip install waitress
    ```
    *(You might want to add `waitress` to your `requirements.txt`)*

2.  Run the application using Waitress:
    ```bash
    waitress-serve --host 0.0.0.0 --port 5000 sales_app:app
    ```
    This command tells Waitress to serve the `app` object found within the `sales_app.py` file, listening on all network interfaces (`0.0.0.0`) on port `5000`.

The application is now ready for deployment following these instructions.
