"""Main Flask app for OpenAI GPT-3 and DALL-E 2 game generator.
"""
import openai
from openai.error import AuthenticationError
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai.error import AuthenticationError

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Set OpenAI API key
openai.api_key = ""

@app.route("/")
def index():
    return render_template("index.html")

main_game_scene= None

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
    main_game_scene = generate_game_scene(game_story)
    # Generate DALL-E 2 prompt
    dalle2_prompt = generate_dalle2_prompt(main_game_scene)
    game_image = generate_game_image(dalle2_prompt)
    # Return game content
    return jsonify({"game_scene": main_game_scene, "game_image": game_image})


@app.route("/api/update-game", methods=["POST"])
def update_game():
    """Update game using OpenAI GPT-3 and DALL-E 2."""
    # Parse API request
    api_key = request.json["api_key"]
    game_story = request.json["game_story"]
    game_scene = request.json["game_scene"]
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
    # Return updated game content
    return jsonify({"game_scene": game_scene, "game_image": game_image})


def generate_game_scene(game_story):
    """Generate game scene using OpenAI GPT-3."""
    # Generate game scene using OpenAI GPT-3
    print(f"Start generating game_story...: {game_story}")

    prompt_of_game_story = "開始一個主題為"+f" {game_story} "+"的文字冒險遊戲" +". 由玩家來決定要採取的動作。請詳細描述場景中所有的物品/生物，如果場景中的人物在對話或跟主角對話，請把對話內容完整輸出來,"+"如果主角和場景中的任何生物互動，請把互動過程描述出來，不要重現重複的場景或對話，故事要曲折離奇/高潮迭起。"+"遊戲開始時，請詳述故事場景，並提供數個身份給玩家選擇。"+"每次你做完敘述後，要說明玩家的生命值和真氣值，生命值歸零玩家就死亡，真氣值歸零就無法使用法術。" +"現在遊戲開始。" \
                            
    print("prompt_of_game_story: ", prompt_of_game_story)
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
    return game_scene

def generate_dalle2_prompt(game_scene):
    """Generate DALL-E 2 prompt."""
    # Call the api to summarize the game scene first
    print(f"Start summarizing game_scene...: {game_scene}")
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
    print(f"Summarized game_scene: {summarized_game_scene}")
    # Generate DALLE2 prompt
    print(f"Start generating DALLE2 prompt with summarized game thene...: {summarized_game_scene}")
    # prompt = """Act as a prompt gerneator for DALL-E 2. Your jop is to provide detailed and creative descriptions that will inspire unique and interesting images from AI. Keep in mind that the AI is capable of understanding a wide range of language and interpet abstract concepts, so feel free to be as imaginative and descriptive as possible. For example, you could describe a scene from a futuristic city, or a surreal landscape filled with strange creatures. The more detailed and creative your descriptions, the more interesting the images will be. """ \
    #             + f"Use this following story to generate prompt under 1024 tokens: {game_scene}"
    
    prompt = "Generate Midjourney's prompt according to this story:\n"+"----------------------\n"+ f"{summarized_game_scene}"+"\n"+"----------------------\n"
    
    print(f"Start generating Midjourney's prompt: {prompt}")
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    dalle2_prompt = response.choices[0].text.strip()
    print(f"Generated DALLE2 prompt: {dalle2_prompt}")
    return dalle2_prompt


def generate_game_image(game_scene):
    """Generate game image using OpenAI DALL-E 2."""
    # Generate game image using OpenAI DALL-E 2
    print(f"Start generating game image...: {game_scene}")
    response = openai.Image.create(
      prompt=game_scene,
      n=1,
      size='512x512'
    )
    game_image = response['data'][0]['url']

    return game_image

# Function to update game scene
def update_game_scene(game_scene, player_input):
    # Update game scene using OpenAI GPT-3
    print(f"Start updating game scene...: {game_scene}, {player_input}")
    updated_game_scene_prompt = "Update the game scene with player's input:\n"+"----------------------\n"+ f"{game_scene}"+"\n"+"----------------------\n"+"Player's input:\n"+"----------------------\n"+ f"{player_input}"+"\n"+"----------------------\n"
    response = openai.Completion.create(
        engine="text-curie-001",
        prompt=updated_game_scene_prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )
    updated_game_scene = response.choices[0].text.strip()
    print("Updated game scene: ", updated_game_scene)
    global main_game_scene
    print("Main game scene: ", main_game_scene)
    return f"Updated game event: {updated_game_scene} \n\n, original background: "+ main_game_scene

# Function to update game image
def update_game_image(game_scene, game_image):

    print(f"Start updating game image...: {game_scene}")
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
