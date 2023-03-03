"""Main Flask app for OpenAI GPT-3 and DALL-E 2 game generator.
"""
import openai
from openai.error import AuthenticationError
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai.error import AuthenticationError
from utils import ( language_translate, calculate_tokens_from_text)
from prompter import get_game_prompter_instance
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

#TEXT_ENGINE = "text-curie-001"
TEXT_ENGINE = "text-davinci-003"
IS_TRANSLATE = False
TEXT_ENGINE_TEMPERATURE = 0.8

#LANGUAGE = "en"
LANGUAGE = "zh-tw"
prompter = get_game_prompter_instance(LANGUAGE)

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
        response =openai.Completion.create(
            engine=TEXT_ENGINE,
            prompt="This",
            max_tokens=2,
            n=1,
            stop=None,
            temperature=0.5,
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


def generate_game_scene(game_story):
    """Generate game scene using OpenAI GPT-3."""
    # Generate game scene using OpenAI GPT-3
    local_text_engine = "gpt-3.5-turbo"
    print(f"\n Start generating game_story...: {game_story}")
    prompt_of_game_story = prompter.generate_game_scene(game_story, text_engine=local_text_engine)
    print("\n Prompt of game_story: ", prompt_of_game_story)

    api_settings = {
        **get_model_selection(local_text_engine),
        **prompt_of_game_story,
        "n": 1,
        "max_tokens": 1024,
        "temperature": TEXT_ENGINE_TEMPERATURE,
        "presence_penalty" : 2
    }

    response = get_engine_method(local_text_engine)(**api_settings)
    game_scene =parse_text_response(response, text_engine=local_text_engine)
    print(f"\n Generated game_scene: {game_scene}")
    return game_scene

def generate_character_choices(game_scene):
    """Generate character choices using OpenAI GPT-3."""
    print(f"\n Start generating character_choices...: {game_scene}")
    prompt_of_character_choices = prompter.generate_character_choices_prompt(game_scene)
    print("\n Prompt of character_choices: ", prompt_of_character_choices)
    response = openai.Completion.create(
        engine=TEXT_ENGINE,
        prompt=prompt_of_character_choices,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=TEXT_ENGINE_TEMPERATURE,
    )
    character_choices = response.choices[0].text.strip()
    print(f"\n Generated character_choices: {character_choices}")
    return character_choices

def compress_game_scene(game_scene, max_token):
    """Compress game scens using OpenAI GPT-3."""
    print(f"#############################\n")
    print(f"\n Start compressing game_scene...: {game_scene}")
    prompt_of_compress_game_scene = prompter.compress_game_scene(game_scene)
    #print("\n Prompt of compress_game_scene: ", prompt_of_compress_game_scene)
    response = openai.Completion.create(
        engine=TEXT_ENGINE,
        prompt=prompt_of_compress_game_scene,
        max_tokens=max_token,
        n=1,
        stop=None,
        temperature=0.5,
    )
    compressed_game_scene = response.choices[0].text.strip()
    print(f"\n Compressed game_scene: {compressed_game_scene}")
    print(f"#############################\n")    
    return compressed_game_scene


def generate_dalle2_prompt(game_scene):
    """Generate DALL-E 2 prompt."""
    # Call the api to summarize the game scene first
    # print(f"/n Start summarizing game_scene for DALLE-2: {game_scene}")
    # game_scene_tokens = calculate_tokens_from_text(game_scene)
    # if game_scene_tokens > 100:
    #     summarize_prompt = prompter.summarize_game_scene(game_scene)
    #     response = openai.Completion.create(
    #         engine=TEXT_ENGINE,
    #         prompt=summarize_prompt,
    #         max_tokens=1024,
    #         n=1,
    #         stop=None,
    #         temperature=0.5,
    #     )
    #     summarized_game_scene = response.choices[0].text.strip()
    #     # Generate DALLE2 prompt
    #     print(f"\n Start generating DALLE2 prompt with summarized game thene...: {summarized_game_scene}")    
    #     text2image_prompt =prompter.generate_text2image_prompt(summarized_game_scene)

    #     print(f"\n Start generating Midjourney's prompt: {text2image_prompt}")
    #     response = openai.Completion.create(
    #         engine=TEXT_ENGINE,
    #         prompt=text2image_prompt,
    #         max_tokens=1024,
    #         n=1,
    #         stop=None,
    #         temperature=0.5,
    #     )
    #     dalle2_prompt = response.choices[0].text.strip()
    # else:
    #     dalle2_prompt = game_scene
    dalle2_prompt = game_scene
    print(f"\n Generated DALLE2 prompt: {dalle2_prompt}")
    return dalle2_prompt


def generate_game_image(game_scene):
    """Generate game image using OpenAI DALL-E 2."""
    # Generate game image using OpenAI DALL-E 2
    print(f"\n Start generating game image...: {game_scene}")
    response = openai.Image.create(
      prompt=game_scene,
      n=1,
      size='512x512'
    )
    game_image = response['data'][0]['url']
    print(f"\n Generated game image: {game_image}")
    return game_image


def update_game_scene_with_previous(previous_game_scenes, last_game_scene, player_input):
    # Update game scene using OpenAI GPT-3
    #print(f"\n Start updating game scene...: {game_scene}, {player_input}")
    updated_game_scene_prompt = prompter.update_game_scene_with_previous(
        previous_game_scenes = previous_game_scenes,
        last_game_scene = last_game_scene,
        player_input = player_input
    )
    print("\n ###########Updated game scene prompt#######\n")
    print(updated_game_scene_prompt)
    response = openai.Completion.create(
        engine=TEXT_ENGINE,
        prompt=updated_game_scene_prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=TEXT_ENGINE_TEMPERATURE,
    )
    updated_game_scene = response.choices[0].text.strip()
    print("\n Updated game scene: ", updated_game_scene)
    return updated_game_scene

# Function to update game image
def update_game_image(game_scene, game_image):
    print(f"\n Start updating game image...: {game_scene}")
    # Update game image using OpenAI DALL-E 2
    response = openai.Image.create(
      prompt=game_scene,
      n=1,
      size='512x512'
    )
    updated_game_image = response['data'][0]['url']
    return updated_game_image

def parse_text_response(openai_text_response, text_engine):
    """According to the text engine, parse the response content.
    
    Different text engine support different response structures
    """
    if "text" in text_engine:
        return openai_text_response.choices[0].text.strip()
    elif "gpt-3.5" in text_engine:
        return openai_text_response['choices'][0]['message']['content']

def get_model_selection(text_engine):
    """Return the model selection according to the text engine."""
    model_seletection = {
        "gpt-3.5-turbo": {  "model": text_engine},
        "text-davinci-003": {  "engine": text_engine},
    }
    return model_seletection[text_engine]

def get_engine_method(text_engine):
    """Return the engine method according to the text engine."""
    method_selected = {
        "gpt-3.5-turbo": openai.ChatCompletion.create,
        "text-davinci-003": openai.Completion.create,
    }
    return method_selected[text_engine]

if __name__ == "__main__":
    app.run(debug=True, port=5007)
