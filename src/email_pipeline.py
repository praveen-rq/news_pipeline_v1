import os
import base64
from datetime import datetime
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file to make configuration more secure and flexible
load_dotenv()

class EmailPipeline:
    """
    Main pipeline class that handles the extraction of emails from Gmail
    and storing them in a Supabase database. This pipeline is specifically designed
    to process emails from a target sender and archive their content for further processing.
    """
    
    def __init__(self, pipeline_name: str = "default"):
        """
        Initialize the email pipeline by setting up connections to Gmail API and Supabase.
        The target email address is retrieved from environment variables for flexibility.
        
        Args:
            pipeline_name: A unique identifier for this pipeline instance. Useful when 
                          running multiple pipelines for different purposes.
        """
        self.gmail_service = self._setup_gmail_service()
        self.supabase: Client = self._setup_supabase()
        self.target_email = os.getenv('TARGET_EMAIL')
        self.pipeline_name = pipeline_name

    def _setup_gmail_service(self):
        """
        Set up Gmail API service using OAuth2 credentials.
        
        The method uses refresh token authentication flow which is suitable for server applications.
        Credentials are securely loaded from environment variables rather than hardcoded.
        The scope is limited to read-only access to ensure minimal permissions.
        
        Returns:
            A configured Gmail API service object that can be used to interact with Gmail.
        """
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        creds = None

        # Load credentials from environment variables instead of token files
        # This approach is more secure for deployment environments
        creds = Credentials(
            None,
            refresh_token=os.getenv('GMAIL_REFRESH_TOKEN'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv('GMAIL_CLIENT_ID'),
            client_secret=os.getenv('GMAIL_CLIENT_SECRET'),
            scopes=SCOPES
        )

        return build('gmail', 'v1', credentials=creds)

    def _setup_supabase(self) -> Client:
        """
        Set up Supabase client connection using environment variables.
        
        Supabase is a PostgreSQL database with a REST API, used here
        for storing the processed email data in a structured format.
        
        Returns:
            A configured Supabase client that can perform database operations.
        """
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        return create_client(url, key)

    def _decode_message(self, message_data: str) -> str:
        """
        Decode base64 URL-safe encoded message data from Gmail API.
        
        Gmail API returns email body content in base64url encoding,
        which needs to be decoded to readable text.
        
        Args:
            message_data: Base64 encoded string of the email message
            
        Returns:
            Decoded UTF-8 string containing the email content
        """
        return base64.urlsafe_b64decode(message_data).decode('utf-8')

    def _parse_email_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw email data from Gmail API response into a structured format.
        
        This method extracts key information like subject, date, and body text
        from the complex nested structure returned by Gmail API. It handles 
        both multipart and simple message types.
        
        Args:
            message: Raw message data from Gmail API
            
        Returns:
            Dictionary containing structured email data with message_id, subject,
            date, body text, from_email, and timestamp of processing
        """
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extract the sender's email address
        from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
        # The From header may contain a name and email in format "Name <email@example.com>"
        # Extract just the email portion if needed
        from_email = from_header
        if '<' in from_header and '>' in from_header:
            from_email = from_header.split('<')[1].split('>')[0]
        
        # Extract email body, handling both multipart messages and simple messages
        body = ''
        if 'parts' in message['payload']:
            # Multipart message - look for plain text part
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = self._decode_message(part['body']['data'])
                    break
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            # Simple message with direct body content
            body = self._decode_message(message['payload']['body']['data'])

        return {
            'message_id': message['id'],
            'subject': subject,
            'date': date,
            'body': body,
            'from_email': from_email,
            'pipeline_name': self.pipeline_name,
            'processed_at': datetime.utcnow().isoformat()
        }

    def fetch_emails(self) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail that match the target sender criteria.
        
        This method queries Gmail API for messages from the specific target email
        address and processes each matching message to extract its content.
        
        Returns:
            List of dictionaries containing structured data for each email
        """
        query = f'from:{self.target_email}'
        results = self.gmail_service.users().messages().list(
            userId='me',
            q=query
        ).execute()

        messages = results.get('messages', [])
        email_data = []

        for message in messages:
            # For each message ID, fetch the full message content
            msg = self.gmail_service.users().messages().get(
                userId='me',
                id=message['id']
            ).execute()
            email_data.append(self._parse_email_data(msg))

        return email_data

    def save_to_supabase(self, emails: List[Dict[str, Any]]) -> None:
        """
        Save processed email data to Supabase database.
        
        Each email is inserted as a separate record into the 'emails' table
        in the Supabase database, allowing for easy querying and further
        processing of the email content.
        
        Args:
            emails: List of processed email data dictionaries
        """
        for email in emails:
            self.supabase.table('emails').insert(email).execute()

    def run(self) -> None:
        """
        Run the complete pipeline from fetching emails to saving them in the database.
        
        This is the main entry point that orchestrates the entire process:
        1. Fetch emails from Gmail
        2. Save them to Supabase if any are found
        3. Handle errors and provide feedback
        
        Raises:
            Exception: If any error occurs during processing
        """
        try:
            emails = self.fetch_emails()
            if emails:
                self.save_to_supabase(emails)
                print(f"Successfully processed {len(emails)} emails")
            else:
                print("No new emails found")
        except Exception as e:
            print(f"Error in pipeline: {str(e)}")
            raise

# Entry point of the script - creates and runs the pipeline when executed directly
if __name__ == "__main__":
    # Pass a custom pipeline name if needed
    pipeline = EmailPipeline(pipeline_name="news_digest_pipeline")
    pipeline.run() 