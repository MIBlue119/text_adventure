"""This module contains the Prompter class, which is used to prompt the user for game information.
"""

_game_prompter_instance = None
def get_game_prompter_instance(language:str="en"):
    """Get the game prompter.
    
    Args:
        language (str, optional): The language of the prompter. Defaults to "en".
        Currently only "en" and "zh-tw" are supported.
    """
    if language not in ["en", "zh-tw"]:
        raise ValueError(f"Language {language} is not supported.")
    global _game_prompter_instance 
    if _game_prompter_instance is None:
        _game_prompter_instance = GamePrompter(language)
    return _game_prompter_instance

class GamePrompter:
    def __init__(self, language: str = "en"):
        self.language = language
    
    def generate_game_scene(self):
        """Generate a game scene."""
        MAIN_PROMPT ={
            "en": "Start a text adventure game, and describe the game scene." + ". Players determine the actions to take. Please describe in detail all the items/creatures in the scene. If characters in the scene have dialogue with the protagonist, please output the dialogue in its entirety. If the protagonist interacts with any creatures in the scene, please describe the interaction process. Do not repeat scenes or dialogue. The story should be full of twists and turns and climactic moments. Please provide a detailed description of the story scene" + "After each narration, please explain the player's life value and true energy value. If the player's life value reaches zero, they will die, and if the true energy value reaches zero, they will not be able to use spells.",
            "zh-tw": "開始一個文字冒險遊戲，並描述遊戲場景。玩家決定要做什麼。請詳細描述場景中所有物品/生物。如果場景中的角色與主角對話，請輸出對話的全部內容。如果主角與場景中的任何生物互動，請描述互動過程。不要重複場景或對話。故事應充滿曲折和激動人心的時刻。遊戲開始時，請提供故事場景的詳細描述。每次叙述後，請說明玩家的生命值和真氣值。如果玩家的生命值為零，他們將死亡，如果真氣值為零，他們將無法使用法術。"
        }        
        SUFFIX_PROMPT = {
            "en": "\nGenerate the game scene to let player interation with it.",
            "zh-tw": "\n生成遊戲場景，讓玩家與之互動。"
        }
        return MAIN_PROMPT[self.language] + SUFFIX_PROMPT[self.language]
    
    def generate_character_choices_prompt(self, scene):
        MAIN_PROMPT= {
            "en":  "Provide several identities for the player to choose from according to the following game scene:\n",
            "zh-tw": "根據以下遊戲場景，提供幾個供玩家選擇的身份：\n"
        }
        return MAIN_PROMPT[self.language] + scene


    def generate_game_scene_choices(self, scene):
        """Generate choices for the game scene."""
        MAIN_PROMPT = {
            "en": "Generate choices for the player according to the follow game scene:\n",
            "zh-tw": "根據以下遊戲場景，生成選項供玩家選擇：\n"
        }
        prompt = MAIN_PROMPT[self.language] + scene
        return prompt

    def summarize_game_scene(self, text):
        """
        Summarize the game scene.
        """
        MAIN_PROMPT = {
            "en": "Summarize following game scene under 500 words and don't add other description:\n",
            "zh-tw": "將以下遊戲場景總結在500字內，並且不要添加其他描述：\n"
        }
        return MAIN_PROMPT[self.language] + text
    
    def generate_text2image_prompt(self, text):
        """Generate a prompt for text2image."""
        MAIN_PROMPT = {
            "en": "I want you to act as a prompt generator for Midjourney's artificial intelligence program. Your job is to provide detailed and creative descriptions that will inspire unique and interesting images from the AI. Keep in mind that the AI is capable of understanding a wide range of language and can interpret abstract concepts, so feel free to be as imaginative and descriptive as possible. For example, you could describe a scene from a futuristic city, or a surreal landscape filled with strange creatures. The more detailed and imaginative your description, the more interesting the resulting image will be. Rule: make the prompt less than 100 words and only response the prompt.",
            "zh-tw": "我想讓你扮演Midjourney的人工智能程式的提示生成器。你的工作是提供詳細而創意的描述，以啟發AI產生獨特且有趣的圖像。請記住，AI能夠理解各種語言，並能夠理解抽象概念，因此，請隨意發揮創意和描述。例如，你可以描述未來城市的場景，或者是充滿奇怪生物的超現實景觀。你的描述越詳細和創意，產生的圖像就越有趣。規則：提示不超過100字，並且只回應提示。"
        }
        INTER_PROMPT = {
            "en": "\nHere is my description:",
            "zh-tw": "\n這是我的描述："
        }
        SUFFIX_PROMPT = {
            "en": "\nGenerate the prompt:",
            "zh-tw": "\n生成提示："
        }
        return MAIN_PROMPT[self.language] + INTER_PROMPT[self.language] + text + SUFFIX_PROMPT[self.language]


    def update_game_scene(self, main_game_scene, last_game_scene, player_input):
        """Update the game scene.
        
        Args:
            main_game_scene (str): The main game scene.
            last_game_scene (str): The last game scene.
            player_input (str): The player's input.
        """
        START_PROMPT = {
            "en": "A text adventure game with the scene: ",
            "zh-tw": "一個文字冒險遊戲，場景為："
        }
        INTER_PROMPT = {
            "en": "\nHere is the player's new decision or thoughts:",
            "zh-tw": "\n這是玩家的新決定或想法："
        }
        SUFFIX_PROMPT = {
            "en": "\nGenerate the next game scene to let player interation with it and provide three choices for the player.",
            "zh-tw": "\n生成下一個遊戲場景，讓玩家與之互動，並為玩家提供三個選擇。"
        }

        if main_game_scene in  last_game_scene:
            prompt = START_PROMPT[self.language] + last_game_scene + INTER_PROMPT[self.language] + player_input + SUFFIX_PROMPT[self.language]
            
        else:
            prompt = START_PROMPT[self.language] + main_game_scene +"\n" + last_game_scene + "\n" +  INTER_PROMPT[self.language] + player_input + SUFFIX_PROMPT[self.language]

        return prompt

