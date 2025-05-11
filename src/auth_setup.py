import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

def setup_gmail_credentials():
    """
    Setup Gmail API OAuth credentials and generate a refresh token.
    This script needs to be run once to authorize the application and
    obtain a refresh token that can be used in the email pipeline.
    """
    # Define the scopes - same as in the email pipeline
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    # The file token.pickle will store the user's access and refresh tokens
    creds = None
    
    # Check if token.pickle exists with valid credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Get client_id and client_secret from environment variables
            client_id = os.getenv('GMAIL_CLIENT_ID')
            client_secret = os.getenv('GMAIL_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                print("ERROR: GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET must be set in your .env file")
                return
            
            # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    }
                },
                SCOPES
            )
            
            # Run the authorization flow - this will open a browser window
            # for the user to authenticate with their Google account
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        # Display the refresh token for setting in .env file
        if creds.refresh_token:
            print("\n=== SETUP SUCCESSFUL ===")
            print(f"Your refresh token: {creds.refresh_token}")
            print("Add this to your .env file as GMAIL_REFRESH_TOKEN")
            print("Keep this token secure and do not share it!")
        else:
            print("No refresh token was generated. Try again or check permissions.")

if __name__ == "__main__":
    setup_gmail_credentials() 