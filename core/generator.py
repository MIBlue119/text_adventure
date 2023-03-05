"""Define the genration related classes and functions.
"""
import openai
from openai.error import AuthenticationError
from core.prompter import get_game_prompter_instance
from core.config import (TEXT_ENGINE, LANGUAGE, TEXT_ENGINE_TEMPERATURE)

prompter = get_game_prompter_instance(LANGUAGE)

def generate_game_scene(game_story):
    """Generate game scene using OpenAI GPT-3."""
    # Generate game scene using OpenAI GPT-3
    print(f"\n Start generating game_story...: {game_story}")
    prompt_of_game_story = prompter.generate_game_scene(game_story, text_engine=TEXT_ENGINE)
    print("\n Prompt of game_story: ", prompt_of_game_story)

    api_settings = {
        **get_model_selection(TEXT_ENGINE),
        **prompt_of_game_story,
        "n": 1,
        "max_tokens": 512,
        "temperature": TEXT_ENGINE_TEMPERATURE,
        "presence_penalty" : 2
    }

    response = get_engine_method(TEXT_ENGINE)(**api_settings)
    game_scene =parse_text_response(response, text_engine=TEXT_ENGINE)
    print(f"\n Generated game_scene: {game_scene}")
    return game_scene

def generate_character_choices(game_scene):
    """Generate character choices using OpenAI GPT-3."""
    print(f"\n Start generating character_choices...: {game_scene}")
    prompt_of_character_choices = prompter.generate_character_choices_prompt(game_scene, text_engine=TEXT_ENGINE)
    print("\n Prompt of character_choices: ", prompt_of_character_choices)

    api_settings = {
        **get_model_selection(TEXT_ENGINE),
        **prompt_of_character_choices,
        "n": 1,
        "max_tokens": 512,
        "temperature": TEXT_ENGINE_TEMPERATURE,
        "presence_penalty" : 2
    }
    response = get_engine_method(TEXT_ENGINE)(**api_settings)
    character_choices = parse_text_response(response, text_engine=TEXT_ENGINE)
    print(f"\n Generated character_choices: {character_choices}")
    return character_choices

def compress_game_scene(game_scene, max_token):
    """Compress game scens using OpenAI GPT-3."""
    print(f"#############################\n")
    print(f"\n Start compressing game_scene...: {game_scene}")
    prompt_of_compress_game_scene = prompter.compress_game_scene(game_scene, text_engine=TEXT_ENGINE)
    
    api_settings = {
        **get_model_selection(TEXT_ENGINE),
        **prompt_of_compress_game_scene,
        "n": 1,
        "max_tokens": max_token,
        "temperature": 0.5,
        "presence_penalty" : 2, 
    }
    response = get_engine_method(TEXT_ENGINE)(**api_settings)
    compressed_game_scene = parse_text_response(response, text_engine=TEXT_ENGINE)
    print(f"\n Compressed game_scene: {compressed_game_scene}")
    print(f"#############################\n")    
    return compressed_game_scene


def generate_dalle2_prompt(game_scene):
    """Generate DALL-E 2 prompt."""
    # Call the api to summarize the game scene first
    print(f"/n Start summarizing game_scene for DALLE-2: {game_scene}")
    summarize_prompt = prompter.summarize_game_scene(game_scene, text_engine=TEXT_ENGINE)
    api_settings = {
        **get_model_selection(TEXT_ENGINE),
        **summarize_prompt,
        "n": 1,
        "max_tokens": 256,
        "temperature": 0.5,
        "presence_penalty" : 2,
    }
    response = get_engine_method(TEXT_ENGINE)(**api_settings)
    summarized_game_scene = parse_text_response(response, text_engine=TEXT_ENGINE)
    # Generate text 2 image prompt for DALL-E 2
    text2image_prompt = prompter.generate_text2image_prompt(summarized_game_scene, text_engine=TEXT_ENGINE)
    api_settings = {
        **get_model_selection(TEXT_ENGINE),
        **text2image_prompt,
        "n": 1,
        "max_tokens": 256,
        "temperature": 0.5,
        "presence_penalty" : 2,
    }
    response = get_engine_method(TEXT_ENGINE)(**api_settings)
    dalle2_prompt = parse_text_response(response, text_engine=TEXT_ENGINE)
    dalle2_prompt = dalle2_prompt +",in the Digital art style, high quality,  more details"
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
        player_input = player_input,
        text_engine=TEXT_ENGINE
    )
    print("\n ###########Updated game scene prompt#######\n")
    print(updated_game_scene_prompt)
    api_settings = {
        **get_model_selection(TEXT_ENGINE),
        **updated_game_scene_prompt,
        "n": 1,
        "max_tokens": 512,
        "temperature": TEXT_ENGINE_TEMPERATURE,
        "presence_penalty" : 2
    }
    response = get_engine_method(TEXT_ENGINE)(**api_settings)
    updated_game_scene = parse_text_response(response, text_engine=TEXT_ENGINE)
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
