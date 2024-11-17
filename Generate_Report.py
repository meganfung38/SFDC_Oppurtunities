import json
import openai
from config import OPENAI_API_KEY


# configure openAI access
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI() # create openAI client instance

def ask_openai(openai_client, system_prompt, user_prompt):
    """calls openai"""
    try:
        completion = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Here is the SFDC lead data: {user_prompt}"
                }
            ]
        )
        return completion.choices[0].message.content
    # debugging
    except Exception as openai_error:
        return f"Unexpected error: {openai_error}"


def generate_report(data):
    """generates an AI driven report analyzing:
    - SFDC opportunity call logs (RingSense AI driven analytics)
    - identifies trends for why opportunity stages were either downgraded or closed/won
    - comprehensive report that offers actionable insights for better sales performance analysis"""

    # context for pre-processing
    documentation = ()

    # define RC products and their plans/ pricing
    RC_products = ()

    # define system prompt-- directions for how to analyze process data
    system_prompt = ()

    # full prompt for request
    full_request = documentation + RC_products + system_prompt

    # user prompt
    # may need formatting depending on how data is processed/ returned
    user_prompt = data

    return ask_openai(client, full_request, user_prompt)

# sample request
print(ask_openai(client,
           "You are an expert in answering questions about the Mike Tyson vs Jake Paul fight.",
           "When was the fight between Mike Tyson and Jake Paul and who won"))

