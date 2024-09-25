let currentQuestion = 0;
let questions = [];

// Load questions from a CSV file
function loadQuestions() {
    fetch('q')
        .then(response => response.text())
        .then(data => {
            const rows = data.split('\n');
            rows.slice(0, 6).forEach(row => {  // Limit to 6 questions
                const [question, ...options] = row.split(',');
                questions.push({ question, options });
            });
            renderQuestion(); // Render the first question after loading
        })
        .catch(error => console.error('Error loading questions:', error));
}

function renderQuestion() {
    const questionCard = document.querySelector('.question-card');

    // If we're on the last question (6th), show the submission card
    if (currentQuestion >= questions.length) {
        renderSubmissionCard();
    } else {
        const question = questions[currentQuestion];

        // Dynamically create the question and options UI
        questionCard.innerHTML = `
            <h2>Question ${currentQuestion + 1}</h2>
            <p class="question">${question.question}</p>
            <ul>
                ${question.options.map((option, index) => `
                    <li><input type="radio" name="answer" value="${index + 1}"> ${option}</li>
                `).join('')}
            </ul>
            <button id="next-btn" onclick="nextQuestion()">
                ${currentQuestion < questions.length - 1 ? 'Next' : 'Finish'}
            </button>
        `;
    }
}

function renderSubmissionCard() {
    const questionCard = document.querySelector('.question-card');

    // Create the submission UI
    questionCard.innerHTML = `
        <h2>Assessment Complete</h2>
        <p>Thank you for answering all the questions. Please submit your assessment.</p>
        <button id="submit-btn" onclick="submitAssessment()">Submit</button>
    `;
}

function nextQuestion() {
    if (currentQuestion < questions.length) {
        currentQuestion++;
        renderQuestion();
    }
}

function submitAssessment() {
    alert('Assessment submitted successfully!');
    // Here you can handle form submission, save data, etc.
}

// Timer countdown function
let timeLeft = 1500; // 25 minutes in seconds
function startTimer() {
    const timerElement = document.getElementById('timer');
    const timerInterval = setInterval(() => {
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        if (seconds < 10) {
            seconds = '0' + seconds;
        }
        timerElement.innerHTML = `${minutes}:${seconds}`;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            alert('Time is up!');
        }
        timeLeft--;
    }, 1000);
}

// Webcam access and display function
function startWebcam() {
    const webcamElement = document.getElementById('webcam');
    const cameraStatus = document.getElementById('camera-status');
    
    navigator.mediaDevices.getUserMedia({ video: true })
    .then((stream) => {
        webcamElement.srcObject = stream;
        cameraStatus.innerText = "Monitoring User Activity";
    })
    .catch((err) => {
        console.error("Webcam access denied: ", err);
        cameraStatus.innerText = "Camera access denied or not supported";
    });
}

window.onload = function() {
    loadQuestions(); // Load questions from the CSV
    startTimer();    // Start the timer
    startWebcam();   // Start the webcam
};

