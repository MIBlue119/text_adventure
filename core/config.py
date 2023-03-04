"""Define the app's configuration.
"""


text_engine_choices = {
    "text-davinci-003": "text-davinci-003",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
}

TEXT_ENGINE = text_engine_choices["gpt-3.5-turbo"]
IS_TRANSLATE = False
TEXT_ENGINE_TEMPERATURE = 0.8

LANGUAGE = "zh-tw"