"""Main Flask app for OpenAI GPT-3 and DALL-E 2 game generator.
"""
import openai
from openai.error import AuthenticationError
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai.error import AuthenticationError
from utils import ( language_translate, calculate_tokens_from_text)

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Set OpenAI API key
openai.api_key = ""

@app.route("/")
def index():
    return render_template("index.html")

main_game_scene= None
last_game_scene = None

TEXT_ENGINE = "text-curie-001"
IS_TRANSLATE = False

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
            engine="text-curie-001",
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
    main_game_scene = generate_game_scene(game_story)
    # Generate DALL-E 2 prompt
    dalle2_prompt = generate_dalle2_prompt(main_game_scene)
    game_image = generate_game_image(dalle2_prompt)
    # Update last game scene
    last_game_scene = main_game_scene
    if IS_TRANSLATE == True:
        translated_game_scene = language_translate(input_text = main_game_scene)
    else:
        translated_game_scene = main_game_scene
    print(f"\n Translated game_scene: {translated_game_scene}")
    # Return game content
    return jsonify({"game_scene": translated_game_scene, "game_image": game_image})


@app.route("/api/update-game", methods=["POST"])
def update_game():
    """Update game using OpenAI GPT-3 and DALL-E 2."""
    # Parse API request
    api_key = request.json["api_key"]
    game_story = request.json["game_story"]
    global last_game_scene
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
    game_scene = update_game_scene(game_scene, player_input)
    # Generate DALL-E 2 prompt
    dalle2_prompt = generate_dalle2_prompt(game_scene)
    game_image = update_game_image(dalle2_prompt, game_image)
    # Update last game scene
    last_game_scene = game_scene
    if IS_TRANSLATE == True:
        translated_game_scene = language_translate(input_text = game_scene, dest = "zh-tw")
    else:
        translated_game_scene = game_scene
    print(f"\n Translated game_scene: {translated_game_scene}")    
    # Return updated game content
    return jsonify({"game_scene": translated_game_scene, "game_image": game_image})


def generate_game_scene(game_story):
    """Generate game scene using OpenAI GPT-3."""
    # Generate game scene using OpenAI GPT-3
    print(f"\n Start generating game_story...: {game_story}")
    #prompt_of_game_story = "開始一個主題為"+f" {game_story} "+"的文字冒險遊戲" +". 由玩家來決定要採取的動作。請詳細描述場景中所有的物品/生物，如果場景中的人物在對話或跟主角對話，請把對話內容完整輸出來,"+"如果主角和場景中的任何生物互動，請把互動過程描述出來，不要重現重複的場景或對話，故事要曲折離奇/高潮迭起。"+"遊戲開始時，請詳述故事場景，並提供數個身份給玩家選擇。"+"每次你做完敘述後，要說明玩家的生命值和真氣值，生命值歸零玩家就死亡，真氣值歸零就無法使用法術。" +"現在遊戲開始。"
    #prompt_of_game_story = "Start a text adventure game with the theme of " + f"{game_story}" + ". Players determine the actions to take. Please describe in detail all the items/creatures in the scene. If characters in the scene have dialogue with the protagonist, please output the dialogue in its entirety. If the protagonist interacts with any creatures in the scene, please describe the interaction process. Do not repeat scenes or dialogue. The story should be full of twists and turns and climactic moments. " + "At the start of the game, please provide a detailed description of the story scene and provide several identities for the player to choose from. " + "After each narration, please explain the player's life value and true energy value. If the player's life value reaches zero, they will die, and if the true energy value reaches zero, they will not be able to use spells. " + "The game starts now."
    #prompt_of_game_story = "Start a text adventure game, and describe the game scene." + ". Players determine the actions to take. Please describe in detail all the items/creatures in the scene. If characters in the scene have dialogue with the protagonist, please output the dialogue in its entirety. If the protagonist interacts with any creatures in the scene, please describe the interaction process. Do not repeat scenes or dialogue. The story should be full of twists and turns and climactic moments. " + "At the start of the game, please provide a detailed description of the story scene and provide several identities for the player to choose from. " + "After each narration, please explain the player's life value and true energy value. If the player's life value reaches zero, they will die, and if the true energy value reaches zero, they will not be able to use spells." + "The game starts now."
    SUFFIX_PROMPT = "\n Generate the game scene to let player interation with it."
    prompt_of_game_story = "Start a text adventure game, and describe the game scene." + ". Players determine the actions to take. Please describe in detail all the items/creatures in the scene. If characters in the scene have dialogue with the protagonist, please output the dialogue in its entirety. If the protagonist interacts with any creatures in the scene, please describe the interaction process. Do not repeat scenes or dialogue. The story should be full of twists and turns and climactic moments. " + "At the start of the game, please provide a detailed description of the story scene and provide several identities for the player to choose from. " + "After each narration, please explain the player's life value and true energy value. If the player's life value reaches zero, they will die, and if the true energy value reaches zero, they will not be able to use spells." +SUFFIX_PROMPT
    print("\n Prompt of game_story: ", prompt_of_game_story)
    response = openai.Completion.create(
        engine="text-curie-001",
        #engine="text-davinci-003",
        prompt=prompt_of_game_story,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    game_scene = response.choices[0].text.strip()
    print(f"\n Generated game_scene: {game_scene}")
    return game_scene

def generate_dalle2_prompt(game_scene):
    """Generate DALL-E 2 prompt."""
    # Call the api to summarize the game scene first
    print(f"/n Start summarizing game_scene for DALLE-2: {game_scene}")
    game_scene_tokens = calculate_tokens_from_text(game_scene)
    if game_scene_tokens > 100:
        summarize_prompt = "Summarize this for a second-grade student in 500 words:\n"+"----------------------\n"+ f"{game_scene}"+"\n"+"----------------------\n"
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=summarize_prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        summarized_game_scene = response.choices[0].text.strip()
        # Generate DALLE2 prompt
        print(f"\n Start generating DALLE2 prompt with summarized game thene...: {summarized_game_scene}")    
        prompt = "Generate Midjourney's prompt according to this story:\n"+f"{summarized_game_scene}"

        print(f"\n Start generating Midjourney's prompt: {prompt}")
        response = openai.Completion.create(
            engine="text-curie-001",
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        dalle2_prompt = response.choices[0].text.strip()
    else:
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

# Function to update game scene
def update_game_scene(last_game_scene, player_input):
    # Update game scene using OpenAI GPT-3
    #print(f"\n Start updating game scene...: {game_scene}, {player_input}")
    global main_game_scene

    APPEND_PROMPT = "Provide detailed descriptions of all items/creatures in the scene, and if any characters in the scene are talking to the protagonist or conversing with other characters."
    PREFIX_PROMPT_PLAYER_INPUT = "\nHere is the player's new decision or thoughts: "
    SUFFIX_PROMPT_PLAYER_INPUT = "\nGenerate the next game scene to let player interation with it."
    if main_game_scene == last_game_scene:
        updated_game_scene_prompt = f"A text adventure game with the scene: {main_game_scene}\n" +APPEND_PROMPT +"\n"+ PREFIX_PROMPT_PLAYER_INPUT+ f"{player_input}"+ SUFFIX_PROMPT_PLAYER_INPUT
    elif main_game_scene != last_game_scene:
        updated_game_scene_prompt = f"A text adventure game with the scene: {main_game_scene}\n {last_game_scene} \n" +PREFIX_PROMPT_PLAYER_INPUT+ f"{player_input}"+ SUFFIX_PROMPT_PLAYER_INPUT
    
    print("\n Updated game scene prompt: ", updated_game_scene_prompt)
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=updated_game_scene_prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
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
if __name__ == "__main__":
    app.run(debug=True, port=5007)
