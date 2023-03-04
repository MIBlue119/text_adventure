"""Main Flask app for OpenAI GPT-3 and DALL-E 2 game generator.
"""
import openai
from openai.error import AuthenticationError
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai.error import AuthenticationError
from core.config import TEXT_ENGINE, LANGUAGE
from core.generator import (generate_game_scene,
                            generate_character_choices, 
                            compress_game_scene, 
                            generate_dalle2_prompt, 
                            generate_game_image,
                            update_game_scene_with_previous,
                            update_game_image)
# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Set OpenAI API key
openai.api_key = ""

@app.route("/")
def index():
    return render_template("index.html")

main_game_scene= None
character_choices = None
last_game_scene = None
previous_game_scenes = []

@app.route("/api/check-api-key", methods=["POST"])
def check_api_key():
    """Check OpenAI API key."""
    # Parse API request from frontend
    api_key = request.json["api_key"]
    # Set OpenAI API key
    openai.api_key = api_key
    try:
        # Check OpenAI by calling the OpenAI API
        if "text" in TEXT_ENGINE:
            response =openai.Completion.create(
                engine=TEXT_ENGINE,
                prompt="This",
                max_tokens=2,
                n=1,
                stop=None,
                temperature=0.5,
            )
        elif "gpt-3.5" in TEXT_ENGINE:
            response =openai.ChatCompletion.create(
                model=TEXT_ENGINE,
                messages=[
                    {"role":"system", "content":"T"}
                ],
                max_tokens=1,
            )
        # Return success message if API key is valid
        return jsonify({"api_key_valid": True, "message": "Valid API key."})
    except AuthenticationError as e:
        print(e)
        # Return error message if API key is invalid
        return jsonify({"api_key_valid": False, "message": "Invalid API key."})


@app.route("/api/game-content", methods=["POST"])
def generate_game_content():
    """Generate game content using OpenAI GPT-3 and DALL-E 2."""
    # Parse API request from frontend
    api_key = request.json["api_key"]
    game_story = request.json["game_story"]
    # Set OpenAI API key
    openai.api_key = api_key
    # Generate game content using OpenAI GPT-3 and DALL-E 2
    global main_game_scene
    global last_game_scene
    global character_choices
    main_game_scene = generate_game_scene(game_story)
    # Generate character choices using OpenAI GPT-3
    character_choices = generate_character_choices(main_game_scene)    
    # Generate DALL-E 2 prompt
    dalle2_prompt = generate_dalle2_prompt(main_game_scene)
    game_image = generate_game_image(dalle2_prompt)
    # Update last game scene
    character_choices_selecction_prefix = {
        "en": "Select a character to play as: ",
        "zh-tw": "選擇一個角色來玩:\n",
    }
    last_game_scene = main_game_scene +"\n"+f"{character_choices_selecction_prefix[LANGUAGE]}"+ character_choices
    # Return game content
    return jsonify({"game_scene": last_game_scene , "game_image": game_image})


@app.route("/api/update-game", methods=["POST"])
def update_game():
    """Update game using OpenAI GPT-3 and DALL-E 2."""
    # Parse API request
    api_key = request.json["api_key"]
    game_story = request.json["game_story"]
    global last_game_scene
    global previous_game_scenes
    game_scene = last_game_scene #request.json["game_scene"]
    game_image = request.json["game_image"]
    player_input = request.json["player_input"]
    # Set OpenAI API key
    print(f"api_key: {api_key}")    
    openai.api_key = api_key
    print(f"game_story: {game_story}")
    print(f"game_scene: {game_scene}")
    print(f"player_input: {player_input}")
    # Update game using OpenAI GPT-3 and DALL-E 2
    game_scene = update_game_scene_with_previous(previous_game_scenes, game_scene, player_input)
    # Generate DALL-E 2 prompt
    dalle2_prompt = generate_dalle2_prompt(game_scene)
    game_image = update_game_image(dalle2_prompt, game_image)

    # Update previous game scenes
    INTER_PROMPT = {
            "en": "\nHere is the player's decision or thoughts:",
            "zh-tw": "\n這是玩家的決定或想法："
    }
    new_previous_game_scene = last_game_scene+f"{INTER_PROMPT[LANGUAGE]}"+player_input+"\n"
    compressed_game_scene = compress_game_scene(new_previous_game_scene, max_token=500) 
    previous_game_scenes.append(compressed_game_scene)
    if len(previous_game_scenes) >=6:
        previous_game_scenes.pop(0)

    # Update last game scene
    last_game_scene = game_scene
    # Return updated game content
    return jsonify({"game_scene": last_game_scene, "game_image": game_image})


if __name__ == "__main__":
    app.run(debug=True, port=5007)
