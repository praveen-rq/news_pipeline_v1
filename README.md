# Email Pipeline

This pipeline fetches emails from a specific Gmail sender and stores them in a Supabase database. It runs automatically every day at 10:00 AM IST using GitHub Actions.

## Setup Instructions

### 1. Gmail API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API
4. Create OAuth 2.0 credentials
5. Download the credentials and note down the Client ID and Client Secret
6. Generate a refresh token using the OAuth 2.0 Playground:
   - Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
   - Set up OAuth 2.0 configuration
   - Select the Gmail API scope: `https://www.googleapis.com/auth/gmail.readonly`
   - Exchange authorization code for tokens
   - Copy the refresh token

### 2. Supabase Setup

1. Create a new project in [Supabase](https://supabase.com)
2. Create a new table called `emails` with the following columns:
   - `message_id` (text, primary key)
   - `subject` (text)
   - `date` (text)
   - `body` (text)
   - `processed_at` (timestamp with time zone)

### 3. GitHub Repository Setup

1. Fork this repository
2. Add the following secrets to your repository (Settings > Secrets and variables > Actions):
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `GMAIL_REFRESH_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `TARGET_EMAIL`

### 4. Local Development

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the pipeline:
   ```bash
   python src/email_pipeline.py
   ```

## Pipeline Details

The pipeline:
1. Connects to Gmail using OAuth 2.0
2. Fetches emails from the specified sender
3. Processes and stores the emails in Supabase
4. Runs automatically at 10:00 AM IST daily

## Manual Trigger

You can manually trigger the pipeline from the Actions tab in your GitHub repository.

## Error Handling

The pipeline includes error handling and logging. Check the GitHub Actions logs for any issues.

# News Pipeline

A Python application for fetching and processing emails from a specific sender.

## Setup Gmail API Authentication

To use this application, you need to set up authentication with the Gmail API. Follow these steps:

1. **Create a Google Cloud Project and enable Gmail API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable the Gmail API for your project
   - Set up OAuth consent screen (you can set it as "External" for testing)

2. **Create OAuth 2.0 Client ID:**
   - Go to "Credentials" in your Google Cloud project
   - Click "Create Credentials" and select "OAuth client ID"
   - Choose "Desktop application" as the application type
   - Give it a name and click "Create"
   - Download the credentials (JSON file)

3. **Set up environment variables:**
   - Create a `.env` file in the project root
   - Add the following variables:
     ```
     GMAIL_CLIENT_ID=your_client_id
     GMAIL_CLIENT_SECRET=your_client_secret
     TARGET_EMAIL=target_email_address
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     ```

4. **Generate Refresh Token:**
   - Run the authentication setup script:
     ```
     python src/auth_setup.py
     ```
   - This will open a browser window for you to authenticate with your Google account
   - After authentication, the script will display your refresh token
   - Add the refresh token to your `.env` file:
     ```
     GMAIL_REFRESH_TOKEN=your_refresh_token
     ```

## Running the Application

After setup is complete, run the email pipeline:

```
python src/email_pipeline.py
```

This will fetch emails from the specified target email address and save them to your Supabase database. 