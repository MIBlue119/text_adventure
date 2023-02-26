// DOM elements
const introPage = document.getElementById("introPage");
const gamePage = document.getElementById("gamePage");
const gameTitle = document.getElementById("gameTitle");
const gameScene = document.getElementById("gameScene");
const gameImage = document.getElementById("gameImage");
const gameInput = document.getElementById("gameInput");
const gameInputText = document.querySelector("#gameInput input[type='text']");
const gameInputButton = document.querySelector("#gameInput button[type='button']");

// Global variables
let playerName = "Player";
let gameStory = "";

// Wait spinner
const waitSpinner = `<div class="spinner"></div>`;

// Event listener for intro page form
document.querySelector("#introForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  openaiApiKey = document.querySelector("#openaiApiKey").value;

  // Check if API key is valid
  const api_key_valid = await checkApiKey();
  if (!api_key_valid) {
      alert("Please enter a valid OpenAI API key.");
      return;
  }
  console.log(openaiApiKey);
  // playerName = document.querySelector("#playerName").value;
  gameStory = document.querySelector('input[name="gameStory"]:checked').value;
  // Call API to generate game content
  showGamePage();
});

// Event listener for game input form
gameInput.addEventListener("submit", (event) => {
  event.preventDefault();
  const inputText = gameInputText.value;
  gameInputText.value = "";
  updateGame(inputText);
});



async function checkApiKey(){
  // Call API to validate API key
  const response =  await fetch("/api/check-api-key", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      api_key: openaiApiKey,
    }),
  });
  const data =  await response.json();
  console.log(data);
  // Check if API key is valid
  if (data.api_key_valid) {
    return true;
  } else {
    return false;
  }
}

// Function to show game page
function showGamePage() {
  // Update game title
  gameTitle.innerHTML = `Welcome to the game, ${playerName}!`;
  // Show game page and hide intro page
  introPage.style.display = "none";
  gamePage.style.display = "block";
  // Call API to generate game content
  console.log("Start to generate game content")
  generateGameContent();
}

// Function to generate game content
async function generateGameContent() {
  // Show wait spinner
  gameScene.innerHTML = waitSpinner;
  // Call API to generate game content
  const response = await fetch("/api/game-content", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      api_key: openaiApiKey,
      game_story: gameStory,
    }),
  });
  const data = await response.json();
  // Update game scene and image
  updateGameScene(data.game_scene);
  updateGameImage(data.game_image);
}
async function generateGameContent() {
  // Show wait spinner
  gameScene.innerHTML = waitSpinner;
  // Call API to generate game content
  const response = await fetch("/api/game-content", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      api_key: openaiApiKey,
      game_story: gameStory,
    }),
  });
  const data = await response.json();
  // // Hide wait spinner
  gameScene.innerHTML = data.game_scene;
  // // Show wait spinner
  // gameScene.innerHTML = waitSpinner;
  // Update game image
  updateGameImage(data.game_image);
}

// Function to update game scene
function updateGameScene(gameSceneContent) {
  gameScene.innerHTML = gameSceneContent;
}

// Function to update game image
function updateGameImage(gameImageUrl) {
  if (gameImageUrl !== "") {
    gameImage.innerHTML = `<img src="${gameImageUrl}" alt="Game image">`;
  } else {
    gameImage.innerHTML = "";
  }
}

// Function to update game
async function updateGame(inputText) {
  // Show wait spinner
  //gameScene.innerHTML = waitSpinner;
  // Call API to update game
  const response = await fetch("/api/update-game", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      api_key: openaiApiKey,
      game_story: gameStory,
      game_scene: gameScene.innerHTML,
      game_image: gameImage.querySelector("img") ? gameImage.querySelector("img").src : "",
      player_input: inputText,
    }),
  });
  const data = await response.json();
  // Update game scene and image
  updateGameScene(data.game_scene);
  updateGameImage(data.game_image);
}
