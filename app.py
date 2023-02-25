import openai
import requests
from flask import Flask, request, jsonify, render_template

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Set OpenAI API key
openai.api_key = ""

@app.route("/")
def index():
    return render_template("index.html")

# API route to generate game content
@app.route("/api/game-content", methods=["POST"])
def generate_game_content():
    # Parse API request
    api_key = request.json["api_key"]
    game_story = request.json["game_story"]
    # Set OpenAI API key
    openai.api_key = api_key
    # Generate game content using OpenAI GPT-3 and DALL-E 2
    game_scene = generate_game_scene(game_story)
    game_image = generate_game_image(game_scene)
    # Return game content
    return jsonify({"game_scene": game_scene, "game_image": game_image})

# API route to update game
@app.route("/api/update-game", methods=["POST"])
def update_game():
    # Parse API request
    api_key = request.json["api_key"]
    game_story = request.json["game_story"]
    game_scene = request.json["game_scene"]
    game_image = request.json["game_image"]
    player_input = request.json["player_input"]
    # Set OpenAI API key
    openai.api_key = api_key
    # Update game using OpenAI GPT-3 and DALL-E 2
    game_scene = update_game_scene(game_scene, player_input)
    game_image = update_game_image(game_scene, game_image)
    # Return updated game content
    return jsonify({"game_scene": game_scene, "game_image": game_image})


# Function to generate game scene
def generate_game_scene(game_story):
    # Generate game scene using OpenAI GPT-3
    response = openai.Completion.create(
        engine="davinci",
        prompt=game_story,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    game_scene = response.choices[0].text.strip()
    return game_scene

# Function to generate game image
def generate_game_image(game_scene):
    # Generate game image using OpenAI DALL-E 2
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}",
        },
        json={
            "model": "image-alpha-001",
            "prompt": f"Generate an image of {game_scene}",
            "num_images": 1,
            "size": "512x512",
            "response_format": "url",
        },
    )
    game_image = response.json()["data"][0]["url"]
    return game_image

# Function to update game scene
def update_game_scene(game_scene, player_input):
    # Update game scene using OpenAI GPT-3
    response = openai.Completion.create(
        engine="davinci",
        prompt=f"{game_scene} Player typed: {player_input}",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    updated_game_scene = response.choices[0].text.strip()
    return updated_game_scene

# Function to update game image
def update_game_image(game_scene, game_image):
    # Update game image using OpenAI DALL-E 2
    response = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai.api_key}",
        },
        json={
            "model": "image-alpha-001",
            "prompt": f"Generate an image of {game_scene}",
            "num_images": 1,
            "size": "512x512",
            "response_format": "url",
            "starting_image": game_image,
        },
    )
    updated_game_image = response.json()["data"][0]["url"]
    return updated_game_image
if __name__ == "__main__":
    app.run(debug=True, port=5004)
