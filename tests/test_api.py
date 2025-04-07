import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.environ.get('OPENAI_API_KEY')
print(f'API key length: {len(api_key)}')
print(f'API key first 10 chars: {api_key[:10]}')
print(f'API key last 10 chars: {api_key[-10:]}')

# Set API key
openai.api_key = api_key

# Test API call
try:
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'Hello'}]
    )
    print('API call successful')
    print(f'Response: {response.choices[0].message.content}')
except Exception as e:
    print(f'API call failed: {e}')
