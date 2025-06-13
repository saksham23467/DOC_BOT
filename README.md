# DocBot - Documentation Assistant

A powerful chatbot that can answer questions about any documentation by using AI to understand and search through the content.

## Features

- Load and index any documentation from a URL
- Ask questions in natural language
- Get instant, accurate answers based on the documentation
- Beautiful, modern UI with chat interface
- Persistent chat history

## Deployment Instructions

### Deploying to Streamlit Cloud

1. Create a GitHub repository and push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your repository, branch, and main file (doc_chatbot_app.py)
6. Add your environment variables:
   - Add your Google API key as `GOOGLE_API_KEY`

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the app:
   ```bash
   streamlit run doc_chatbot_app.py
   ```

## Environment Variables

- `GOOGLE_API_KEY`: Your Google API key for Gemini model access

## Note

Make sure to keep your API keys secure and never commit them to version control. Use environment variables or secrets management in production. 