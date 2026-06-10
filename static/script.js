// static/script.js

// --- Global State ---
let GAME_ID = null;
let IS_PLAYER_TURN = false;
let CURRENT_MODE = null;
const HEX_SIZE = 25;

// --- DOM Elements ---
const boardSVG = document.getElementById('game-board');
const statusDiv = document.getElementById('status');
const dimensionSelector = document.getElementById('dimension-selector');

const newGameVsAiBtn = document.getElementById('new-game-vs-ai');
const newGameVsFriendBtn = document.getElementById('new-game-vs-friend');
const newGameVsRandomBtn = document.getElementById('new-game-vs-random');
const resetBtn = document.getElementById('reset-game-btn');


// --- Event Listeners ---
newGameVsAiBtn.addEventListener('click', () => startNewGame('human_vs_ai'));
newGameVsFriendBtn.addEventListener('click', () => startNewGame('human_vs_human'));
newGameVsRandomBtn.addEventListener('click', () => startNewGame('human_vs_random'));
resetBtn.addEventListener('click', resetGame);


// --- API Communication ---
async function startNewGame(mode) {
    statusDiv.textContent = 'Starting a new game...';
    IS_PLAYER_TURN = false;
    CURRENT_MODE = mode;
    const selectedDim = dimensionSelector.value;

    const response = await fetch('/api/new_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: mode, dim: selectedDim })
    });
    const gameState = await response.json();
    GAME_ID = gameState.gameId;
    updateUI(gameState);
}

async function resetGame() {
    if (!GAME_ID) {
        alert("Start a game before you can reset!");
        return;
    }
    statusDiv.textContent = 'Resetting game...';
    IS_PLAYER_TURN = false;

    const response = await fetch('/api/reset_game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gameId: GAME_ID })
    });
    const gameState = await response.json();
    updateUI(gameState);
}


async function handleHexClick(row, col) {
    if (!GAME_ID || !IS_PLAYER_TURN) {
        return;
    }

    IS_PLAYER_TURN = false; // Disable further clicks until we get a response
    
    if (CURRENT_MODE === 'human_vs_ai') {
        statusDiv.textContent = 'Sending move... Computer is thinking...';
    } else {
        statusDiv.textContent = 'Sending move...';
    }


    const response = await fetch('/api/make_move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gameId: GAME_ID, move: [row, col] })
    });

    const gameState = await response.json();
    if (gameState.error) {
        alert(gameState.error);
    }
    
    updateUI(gameState);
}

// --- UI Update Functions ---
function updateUI(gameState) {
    drawBoard(gameState);
    updateStatus(gameState);
}

function updateStatus(gameState) {
    if (gameState.gameOver) {
        statusDiv.textContent = `Game Over! Player ${gameState.winner} wins by a ${gameState.winningStructure}!`;
        IS_PLAYER_TURN = false;
    } else {
        statusDiv.textContent = `Player ${gameState.currentPlayer}'s turn`;
        IS_PLAYER_TURN = true;
    }
}

function drawBoard(gameState) {
    const board = gameState.board;
    if (!board) return;

    const layers = (board.length + 1) / 2;
    boardSVG.innerHTML = ''; // Clear previous board

    const height = (25 * Math.sqrt(3) * (2 * layers - 1));
    const width = (75 * layers - 25);
    boardSVG.setAttribute('viewBox', `0 0 ${width} ${height}`);
    boardSVG.setAttribute('width', width * 1.5);
    boardSVG.setAttribute('height', height * 1.5);

    // This loop structure iterates through the board column by column,
    // and calculates the number of rows in each column ('col_size').
    for (let j = 0; j < board.length; j++) {
        const col_size = layers + (j < layers ? j : 2 * layers - 2 - j);
        for (let i = 0; i < col_size; i++) {
            
            // **FIXED LOGIC HERE**
            // The faulty 'if' condition was removed. Now we draw every hexagon
            // that the valid loop structure gives us.
            const cellValue = board[i][j];

            const hexPoints = calculateHexagonPoints(i, j, layers);
            const polygon = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            
            polygon.setAttribute("points", hexPoints.map(p => `${p.x},${p.y}`).join(' '));
            polygon.setAttribute("class", `hexagon player${cellValue}`);
            
            if (gameState.winningPath && gameState.winningPath.some(p => p[0] === i && p[1] === j)) {
                polygon.classList.add('winning-path');
            }

            if (cellValue === 0) { // Only allow clicks on empty cells
                polygon.onclick = () => handleHexClick(i, j);
            }

            boardSVG.appendChild(polygon);
        }
    }
}

function calculateHexagonPoints(i, j, layers) {
    const size = HEX_SIZE;
    const sqrt3 = Math.sqrt(3);
    const offsetX = j * size * 1.5;
    const offsetY = (Math.abs(j - layers + 1) + 2 * i) * size * sqrt3 / 2;

    return [
        { x: size / 2 + offsetX, y: offsetY },
        { x: size * 1.5 + offsetX, y: offsetY },
        { x: size * 2 + offsetX, y: size * sqrt3 / 2 + offsetY },
        { x: size * 1.5 + offsetX, y: size * sqrt3 + offsetY },
        { x: size / 2 + offsetX, y: size * sqrt3 + offsetY },
        { x: offsetX, y: size * sqrt3 / 2 + offsetY }
    ];
}