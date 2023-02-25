import tiktoken 
from googletrans import Translator
import re

def calculate_tokens_from_text(text:str=None, encoding_name:str="gpt2"):
    """Calculate the number of tokens from text."""
    # Calculate the number of tokens from text
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(text))
    return num_tokens

def language_translate(input_text, dest='zh-tw'):
    """Translate text to target language."""
    print(input_text)
    # add period if there's no period at the end of line
    input_text = re.sub('\n\n','.\n',input_text)
    # delete empty space in the beginning
    input_text = re.sub('\n\s','\n',input_text)
    # delete empty line
    input_text = re.sub('^\n','',input_text)    
    translator = Translator()
    translated = translator.translate(input_text, dest=dest)
    return translated.text


if __name__ == "__main__":
    text="""A text adventure game with the scene: You are Harry Potter, a wizard attending Hogwarts School of Witchcraft and Wizardry. Your journey begins with a game of exploration, in which you must choose which actions to take to progress through the game. Every scene in the game contains objects and creatures that can be interacted with, and if any characters in the scene are speaking or interacting with Harry, please include their entire dialogue in your submission. If the character and Harry interact with each other, please describe the interaction. You do not need to repeat scenes or dialogue, and the story must be unpredictable/high-energy from beginning to end. The game begins when you begin your story.
Provide detailed descriptions of all items/creatures in the scene, and if any characters in the scene are talking to the protagonist or conversing with other characters.

Player's new decisions:   我想跟妙麗說話"""
    print(calculate_tokens_from_text(text=text, encoding_name="gpt2"))
    print(language_translate(input_text=text, dest='zh-tw'))
    