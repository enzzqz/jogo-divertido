from flask import Flask, request, jsonify, render_template_string
import random

app = Flask(__name__)

# HTML com CSS e JavaScript
html_content = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jogos Divertidos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #282c34;
            color: white;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        .game-container {
            margin-bottom: 40px;
        }
        h1, h2 {
            margin-bottom: 20px;
        }
        .buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            margin: 5px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        #pedra { background-color: #d9534f; }
        #papel { background-color: #5bc0de; }
        #tesoura { background-color: #5cb85c; }
        .quiz-option {
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .button-1 { background-color: #d9534f; }
        .button-2 { background-color: #5bc0de; }
        .button-3 { background-color: #5cb85c; }
        .button-4 { background-color: #f0ad4e; }
        .button-5 { background-color: #0275d8; }
        .button-6 { background-color: #5bc0de; }
        .button-7 { background-color: #d9534f; }
        .button-8 { background-color: #5cb85c; }
        .button-9 { background-color: #f0ad4e; }
        .hangman-letter {
            padding: 10px 20px;
            font-size: 16px;
            margin: 5px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        #result, #guess-result, #quiz-result, #hangman-display {
            margin-top: 20px;
            font-size: 18px;
        }
        .result-box, .quiz-result-box {
            margin-top: 20px;
            padding: 20px;
            border: 1px solid #fff;
            border-radius: 10px;
            background-color: rgba(255, 255, 255, 0.1);
        }
        #scoreboard {
            display: flex;
            justify-content: space-between;
            width: 300px;
            margin-top: 20px;
        }
        #history {
            margin-top: 20px;
            width: 300px;
        }
    </style>
    <script>
        let wins = 0;
        let losses = 0;
        let ties = 0;
        let history = [];
        let correctAnswer = '';
        let attempts = 6;
        let usedLetters = [];
        let word = '';

        async function playRPS(choice) {
            const response = await fetch('/play_rps', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ choice: choice })
            });
            const result = await response.json();
            document.getElementById('result').innerHTML = 
                `<div class="result-box">
                    <p>Você escolheu: ${result.user_choice}</p>
                    <p>Computador escolheu: ${result.computer_choice}</p>
                    <p>Resultado: ${result.result}</p>
                </div>`;

            if (result.result === "você ganhou") {
                wins++;
            } else if (result.result === "você perdeu") {
                losses++;
            } else {
                ties++;
            }

            history.push(`Você: ${result.user_choice}, Computador: ${result.computer_choice}, Resultado: ${result.result}`);
            updateScoreboard();
            updateHistory();
        }

        async function guessNumberGame(number) {
            const response = await fetch('/guess_number', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ guess: number })
            });
            const result = await response.json();
            document.getElementById('guess-result').innerHTML = `<div class="result-box">${result.message}</div>`;
        }

        async function startQuiz() {
            const response = await fetch('/start_quiz');
            const result = await response.json();
            document.getElementById('quiz-question').innerText = result.question;
            correctAnswer = result.correct_answer;
            // Display answers
            let answersHTML = '';
            for (const [key, value] of Object.entries(result.answers)) {
                answersHTML += `<button class="quiz-option" onclick="answerQuiz('${key}')">${key}: ${value}</button>`;
            }
            document.getElementById('quiz-result').innerHTML = answersHTML;
        }

        async function answerQuiz(answer) {
            const response = await fetch('/answer_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ answer: answer })
            });
            const result = await response.json();
            document.getElementById('quiz-result').innerHTML = `<div class="result-box">${result.message}</div>`;
        }

        async function startHangman() {
            const response = await fetch('/start_hangman');
            const result = await response.json();
            word = result.word;
            attempts = result.attempts;
            usedLetters = result.used_letters;
            document.getElementById('hangman-display').innerText = result.word_display;
            document.getElementById('hangman-attempts').innerText = `Tentativas restantes: ${attempts}`;
            document.getElementById('hangman-used-letters').innerText = `Letras usadas: ${usedLetters.join(', ')}`;
            document.getElementById('hangman-message').innerText = '';
        }

        async function guessHangman(letter) {
            const response = await fetch('/guess_hangman', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ letter: letter })
            });
            const result = await response.json();
            document.getElementById('hangman-display').innerText = result.word_display;
            document.getElementById('hangman-attempts').innerText = `Tentativas restantes: ${result.attempts}`;
            document.getElementById('hangman-used-letters').innerText = `Letras usadas: ${result.used_letters.join(', ')}`;
            document.getElementById('hangman-message').innerText = result.message;
            if (result.game_over) {
                alert('O jogo acabou!');
            }
        }

        function updateScoreboard() {
            document.getElementById('scoreboard').innerHTML = 
                `<div>Vitórias: ${wins}</div>
                 <div>Derrotas: ${losses}</div>
                 <div>Empates: ${ties}</div>`;
        }

        function updateHistory() {
            let historyHTML = '<ul>';
            for (let i = history.length - 1; i >= 0; i--) {
                historyHTML += `<li>${history[i]}</li>`;
            }
            historyHTML += '</ul>';
            document.getElementById('history').innerHTML = historyHTML;
        }

        // Start the quiz when the page loads
        document.addEventListener('DOMContentLoaded', startQuiz);
    </script>
</head>
<body>
    <div class="container">
        <h1>Jogos Divertidos</h1>

        <!-- Pedra, Papel e Tesoura -->
        <div class="game-container">
            <h2>Pedra, Papel e Tesoura</h2>
            <div class="buttons">
                <button id="pedra" onclick="playRPS('pedra')">Pedra</button>
                <button id="papel" onclick="playRPS('papel')">Papel</button>
                <button id="tesoura" onclick="playRPS('tesoura')">Tesoura</button>
            </div>
            <div id="result"></div>
            <div id="scoreboard">
                <div>Vitórias: 0</div>
                <div>Derrotas: 0</div>
                <div>Empates: 0
                </div>
            </div>
            <div id="history"></div>
        </div>

        <!-- Adivinhe o Número -->
        <div class="game-container">
            <h2>Adivinhe o Número</h2>
            <input type="number" id="number-guess" min="1" max="10" placeholder="Digite um número de 1 a 10">
            <button onclick="guessNumberGame(document.getElementById('number-guess').value)">Adivinhar</button>
            <div id="guess-result"></div>
        </div>

        <!-- Quiz -->
        <div class="game-container">
            <h2>Quiz</h2>
            <div id="quiz-question"></div>
            <div id="quiz-result"></div>
        </div>

        <!-- Forca -->
        <div class="game-container">
            <h2>Forca</h2>
            <button class="hangman-letter" onclick="guessHangman('a')">A</button>
            <button class="hangman-letter" onclick="guessHangman('b')">B</button>
            <button class="hangman-letter" onclick="guessHangman('c')">C</button>
            <button class="hangman-letter" onclick="guessHangman('d')">D</button>
            <button class="hangman-letter" onclick="guessHangman('e')">E</button>
            <button class="hangman-letter" onclick="guessHangman('f')">F</button>
            <button class="hangman-letter" onclick="guessHangman('g')">G</button>
            <button class="hangman-letter" onclick="guessHangman('h')">H</button>
            <button class="hangman-letter" onclick="guessHangman('i')">I</button>
            <button class="hangman-letter" onclick="guessHangman('j')">J</button>
            <button class="hangman-letter" onclick="guessHangman('k')">K</button>
            <button class="hangman-letter" onclick="guessHangman('l')">L</button>
            <button class="hangman-letter" onclick="guessHangman('m')">M</button>
            <button class="hangman-letter" onclick="guessHangman('n')">N</button>
            <button class="hangman-letter" onclick="guessHangman('o')">O</button>
            <button class="hangman-letter" onclick="guessHangman('p')">P</button>
            <button class="hangman-letter" onclick="guessHangman('q')">Q</button>
            <button class="hangman-letter" onclick="guessHangman('r')">R</button>
            <button class="hangman-letter" onclick="guessHangman('s')">S</button>
            <button class="hangman-letter" onclick="guessHangman('t')">T</button>
            <button class="hangman-letter" onclick="guessHangman('u')">U</button>
            <button class="hangman-letter" onclick="guessHangman('v')">V</button>
            <button class="hangman-letter" onclick="guessHangman('w')">W</button>
            <button class="hangman-letter" onclick="guessHangman('x')">X</button>
            <button class="hangman-letter" onclick="guessHangman('y')">Y</button>
            <button class="hangman-letter" onclick="guessHangman('z')">Z</button>
            <div id="hangman-display"></div>
            <div id="hangman-attempts"></div>
            <div id="hangman-used-letters"></div>
            <div id="hangman-message"></div>
        </div>
    </div>
</body>
</html>
"""

def play_rps(user_choice):
    choices = ["pedra", "papel", "tesoura"]
    computer_choice = random.choice(choices)

    if user_choice == computer_choice:
        result = "empate"
    elif (user_choice == "pedra" and computer_choice == "tesoura") or \
         (user_choice == "papel" and computer_choice == "pedra") or \
         (user_choice == "tesoura" and computer_choice == "papel"):
        result = "você ganhou"
    else:
        result = "você perdeu"

    return {"user_choice": user_choice, "computer_choice": computer_choice, "result": result}

def guess_number(number):
    correct_number = random.randint(1, 10)
    if number == correct_number:
        return {"message": "Parabéns! Você acertou!"}
    else:
        return {"message": f"Você errou! O número correto era {correct_number}."}

def start_quiz():
    questions = [
        {"question": "Qual é a capital da França?", "answers": {"A": "Paris", "B": "Londres", "C": "Berlim", "D": "Madri"}, "correct_answer": "A"},
        {"question": "Qual é a fórmula da água?", "answers": {"A": "H2O", "B": "CO2", "C": "O2", "D": "NaCl"}, "correct_answer": "A"},
        # Adicione mais perguntas e respostas conforme necessário
    ]
    question = random.choice(questions)
    return question

def answer_quiz(answer):
    if answer == correct_answer:
        return {"message": "Correto!"}
    else:
        return {"message": "Incorreto. Tente novamente!"}

def start_hangman():
    words = ["python", "flask", "programacao", "desenvolvimento", "computador"]
    word = random.choice(words).upper()
    word_display = "_" * len(word)
    return {"word": word, "word_display": word_display, "attempts": 6, "used_letters": []}

def guess_hangman(letter):
    global word, word_display, attempts, used_letters
    letter = letter.upper()
    if letter in used_letters:
        return {"word_display": word_display, "attempts": attempts, "used_letters": used_letters, "message": "Letra já usada.", "game_over": False}

    used_letters.append(letter)
    if letter in word:
        word_display = "".join([letter if word[i] == letter else word_display[i] for i in range(len(word))])
        if "_" not in word_display:
            return {"word_display": word_display, "attempts": attempts, "used_letters": used_letters, "message": "Você venceu!", "game_over": True}
        return {"word_display": word_display, "attempts": attempts, "used_letters": used_letters, "message": "Correto!", "game_over": False}
    else:
        attempts -= 1
        if attempts <= 0:
            return {"word_display": word_display, "attempts": attempts, "used_letters": used_letters, "message": f"Game over! A palavra era {word}.", "game_over": True}
        return {"word_display": word_display, "attempts": attempts, "used_letters": used_letters, "message": "Incorreto!", "game_over": False}

@app.route('/')
def index():
    return render_template_string(html_content)

@app.route('/play_rps', methods=['POST'])
def play_rps_route():
    data = request.json
    user_choice = data.get('choice')
    result = play_rps(user_choice)
    return jsonify(result)

@app.route('/guess_number', methods=['POST'])
def guess_number_route():
    data = request.json
    number = int(data.get('guess'))
    result = guess_number(number)
    return jsonify(result)

@app.route('/start_quiz', methods=['GET'])
def start_quiz_route():
    result = start_quiz()
    return jsonify(result)

@app.route('/answer_quiz', methods=['POST'])
def answer_quiz_route():
    data = request.json
    answer = data.get('answer')
    result = answer_quiz(answer)
    return jsonify(result)

@app.route('/start_hangman', methods=['GET'])
def start_hangman_route():
    global word, word_display, attempts, used_letters
    result = start_hangman()
    word = result['word']
    word_display = result['word_display']
    attempts = result['attempts']
    used_letters = result['used_letters']
    return jsonify(result)

@app.route('/guess_hangman', methods=['POST'])
def guess_hangman_route():
    data = request.json
    letter = data.get('letter')
    result = guess_hangman(letter)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
