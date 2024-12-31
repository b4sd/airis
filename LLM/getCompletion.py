from openai import OpenAI
from dotenv import load_dotenv
import os
from LLM.prompts import prompts
load_dotenv()

def getCompletion(userPrompt, promptStyle="default"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Define the messages list to be sent
    messages = [
        {"role": "system", "content": prompts.get(promptStyle, "")},  # Ensure 'promptStyle' exists in 'prompts'
        {"role": "user", "content": userPrompt}
    ]
    print()
    print(messages)
    print()
    
    # Make the API call
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini"
        )
        print(response)
    except Exception as e:
        print(f"Error during API request: {e}")
        return None
    
    # Return the completion text
    return response.choices[0].message.content