# Import required libraries
import requests
import json
from ai_engine import UAgentResponse, UAgentResponseType

OPENAI_API_KEY = "sk-proj-bgGaJc1BFQqgGRXiPFipT3BlbkFJUUCgEBTclZOquyXzHH2Z"

# Configuration for making requests to OpenAI
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
MODEL_ENGINE = "gpt-4"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

class AIStylistRequest(Model):
    age: str
    size: str
    weather: str
    place: str
    gender: str
    height: str
    skin_tone: str
    preferences: str
    occasion: str  # New attribute for occasion

class Error(Model):
    text: str

# Send a prompt and context to the AI model and return the content of the completion
async def get_completion(context: str, prompt: str, max_tokens: int = 1024):
    data = {
        "model": MODEL_ENGINE,
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(OPENAI_URL, headers=HEADERS, data=json.dumps(data))
        messages = response.json()['choices']
        message = messages[0]['message']['content']
        print(message)
    except Exception as ex:
        return None

    print("Got response from AI model: " + message)
    return message

# Instruct the AI model to retrieve data and context for the data and return it in machine-readable JSON format
async def get_data(age, gender, place, size, weather, height, skin_tone, preferences, occasion):
    context = f'You are a fashion AI Stylist who can provide outfit recommendations based on current trends and user preferences in a machine-readable format. Based on the following details, generate outfit recommendations according to the latest style fashion trends for a vacation: - Age: {age} - Size: {size} - Weather: {weather} - Place: {place} - Gender: {gender} - Height: {height} - Skin Tone: {skin_tone} - Preferences: {preferences} - Occasion: {occasion} Provide suggestions for items like tops, bottoms, shoes, and accessories.'
    request = 'Please provide me fashion recommendations for the provided details.'
    response = await get_completion(context, request, max_tokens=2048)

    try:
        return response
    except Exception as ex:
        return Error(text="Sorry, I wasn't able to answer your request this time. Feel free to try again.")

sample_protocol = Protocol("sample protocol")

# Message handler for data requests sent to this agent
@sample_protocol.on_message(model=AIStylistRequest, replies={UAgentResponse})
async def handle_request(ctx: Context, sender: str, msg: AIStylistRequest):
    ctx.logger.info(f"Got request from {sender}: {msg.size}")
    response = await get_data(msg.age, msg.gender, msg.place, msg.size, msg.weather, msg.height, msg.skin_tone, msg.preferences, msg.occasion)
    ctx.logger.info(response)
    await ctx.send(sender, UAgentResponse(message=str(response), type=UAgentResponseType.FINAL))

agent.include(sample_protocol, publish_manifest=True)