# OpenAI GPT-3 and DALL-E 2 Text Adventure Game

This is a text adventure game that uses OpenAI's GPT-3 language model and DALL-E 2 image generation model to generate game content on the fly. Players can enter commands to progress the story and see new images generated by DALL-E 2.

- https://drive.google.com/file/d/1ah-3_qT-dU6_QlgXc7iB9FK5JOGv4d3Z/view

## Prerequisites

Before running the application, you need to have the following:

- An OpenAI API key
- Python 3.x
- Pip package manager

## Installation

1. Clone or download the repository
2. In the terminal or command prompt, navigate to the repository directory
3. Run `pip install -r requirements.txt` to install the necessary Python libraries
4. Set your OpenAI API key as an environment variable by running `export OPENAI_API_KEY=<YOUR_API_KEY>` (Unix-based systems) or `set OPENAI_API_KEY=<YOUR_API_KEY>` (Windows)
5. Run `python app.py` to start the Flask server
6. Open a web browser and go to `http://127.0.0.1:500` to play the game

## Usage

- Enter your OpenAI API key and player name, and select a game story to begin
- Enter commands to progress the story and see new images generated by DALL-E 2
- The game will continue until you reach the end or enter "quit"

## Technologies Used

- OpenAI GPT-3 API
- OpenAI DALL-E 2 API
- Python
- Flask
- HTML/CSS/JavaScript
- Bootstrap

## Credits

This project was inspired by and adapted from [OpenAI Codex Text Adventure Game](https://github.com/openai/codex-adventure). Special thanks to OpenAI for providing the GPT-3 and DALL-E 2 models and API.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
