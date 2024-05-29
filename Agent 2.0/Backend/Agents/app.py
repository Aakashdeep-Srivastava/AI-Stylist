import requests
import os
from flask import Flask, request, jsonify
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Define Request, Response, and Error Models
class OutfitRequest(Model):
    age: str
    size: str
    weather: str
    place: str
    gender: str
    occasion: str = "casual"
    style: str = "modern"

class OutfitResponse(Model):
    recommendations: str

class ErrorResponse(Model):
    error: str

# Define the function to get outfit recommendations
def chat(prompt, role="user"):
    endpoint = "https://api.openai.com/v1/chat/completions"
    openai_api_key = os.getenv('OPENAI_API_KEY')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": "gpt-4",
        "messages": [{
            "role": role,
            "content": prompt
        }]
    }

    response = requests.post(endpoint, json=data, headers=headers)
    response_data = response.json()

    if 'choices' in response_data and response_data['choices']:
        response = response_data['choices'][0]['message']['content'].strip()
        return response
    else:
        return "No valid response received."

async def get_outfit_recommendations(age, size, weather, place, gender, occasion="casual", style="modern"):
    prompt = f"""
    Based on the following details, generate outfit recommendations according to the latest {style} fashion trends for a {occasion} occasion:
    - Age: {age}
    - Size: {size}
    - Weather: {weather}
    - Place: {place}
    - Gender: {gender}

    Provide suggestions for items like tops, bottoms, shoes, and accessories.
    """

    return chat(prompt)

# Create Flask app
app = Flask(__name__)

# Create Outfit Agent
OutfitAgent = Agent(
    name="OutfitAgent",
    port=8004,
    seed="Outfit Agent secret phrase",
    endpoint=["http://127.0.0.1:8004/submit"],
)

# Registering agent on Almanac and funding it.
fund_agent_if_low(OutfitAgent.wallet.address())

# On agent startup printing address
@OutfitAgent.on_event('startup')
async def agent_details(ctx: Context):
    ctx.logger.info(f'Outfit Agent Address is {OutfitAgent.address}')

# On_query handler to check cost
@OutfitAgent.on_query(model=OutfitRequest, replies={OutfitResponse, ErrorResponse})
async def query_handler(ctx: Context, sender: str, msg: OutfitRequest):
    try:
        ctx.logger.info(f'Fetching outfit recommendations for user with details: {msg.dict()}')
        recommendations = await get_outfit_recommendations(
            age=msg.age,
            size=msg.size,
            weather=msg.weather,
            place=msg.place,
            gender=msg.gender,
            occasion=msg.occasion,
            style=msg.style
        )
        ctx.logger.info(recommendations)
        await ctx.send(sender, OutfitResponse(recommendations=recommendations))
    except Exception as e:
        error_message = f"Error fetching outfit recommendations: {str(e)}"
        ctx.logger.error(error_message)
        await ctx.send(sender, ErrorResponse(error=error_message))

@app.route('/outfit_recommendations', methods=['POST'])
def outfit_recommendations():
    data = request.json
    required_fields = ["age", "size", "weather", "place", "gender"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    age = data.get("age")
    size = data.get("size")
    weather = data.get("weather")
    place = data.get("place")
    gender = data.get("gender")
    occasion = data.get("occasion", "casual")
    style = data.get("style", "modern")

    recommendations = get_outfit_recommendations(age, size, weather, place, gender, occasion, style)
    return jsonify({"recommendations": recommendations})

# Starting agent and Flask app
if __name__ == "__main__":
    import threading

    def start_agent():
        OutfitAgent.run()

    agent_thread = threading.Thread(target=start_agent)
    agent_thread.start()

    app.run(port=5000)
