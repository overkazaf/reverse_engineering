const initializeInterview = () => {
    const interviewModalOverlay = document.getElementById('interview-modal-overlay');
    const startBtn = document.getElementById('mock-interview-btn');
    const closeBtn = document.getElementById('interview-close-btn');
    
    if (!interviewModalOverlay || !startBtn) return;

    const loadingEl = document.getElementById('interview-loading');
    const contentEl = document.getElementById('interview-content');
    const summaryEl = document.getElementById('interview-summary');
    
    const progressEl = document.getElementById('interview-progress');
    const questionEl = document.getElementById('interview-question');
    const optionsContainerEl = document.getElementById('interview-options-container');
    const feedbackEl = document.getElementById('interview-feedback');
    const feedbackTextEl = document.getElementById('interview-feedback-text');

    const selfAssessEl = document.getElementById('interview-self-assess');
    const correctBtn = document.getElementById('interview-assess-correct-btn');
    const wrongBtn = document.getElementById('interview-assess-wrong-btn');

    const scoreEl = document.getElementById('interview-score');
    const analysisListEl = document.getElementById('interview-analysis-list');
    const wrongListEl = document.getElementById('interview-wrong-list');
    const restartBtn = document.getElementById('interview-restart-btn');

    const prevBtn = document.getElementById('interview-prev-btn');
    const nextBtn = document.getElementById('interview-next-btn');
    
    let questions = [];
    let userAnswers = [];
    let currentIndex = 0;

    const resetState = () => {
        questions = [];
        userAnswers = [];
        currentIndex = 0;
        contentEl.style.display = 'none';
        summaryEl.style.display = 'none';
        loadingEl.style.display = 'block';
        loadingEl.innerText = 'Generating questions...'; // Reset loading text
        prevBtn.disabled = true;
        nextBtn.disabled = true;
    };

    const fetchQuestions = async () => {
        try {
            const pageContent = document.querySelector('.md-content__inner').innerText;
            const response = await fetch('http://127.0.0.1:5001/api/mock-interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: pageContent })
            });

            if (!response.ok) throw new Error('Failed to fetch questions');
            
            questions = await response.json();
            if (!Array.isArray(questions) || questions.length === 0 || !questions[0].options) {
                 throw new Error('Received invalid multiple-choice question format.');
            }
            userAnswers = new Array(questions.length).fill(null);
            loadingEl.style.display = 'none';
            contentEl.style.display = 'block';
            nextBtn.disabled = false;
            renderQuestion();
        } catch (error) {
            console.error(error);
            loadingEl.innerText = "Sorry, couldn't generate questions. Please try again.";
        }
    };

    const renderQuestion = () => {
        const q = questions[currentIndex];
        progressEl.innerText = `Question ${currentIndex + 1} / ${questions.length}`;
        questionEl.innerText = q.question;
        
        optionsContainerEl.innerHTML = '';
        for (const key in q.options) {
            const button = document.createElement('button');
            button.className = 'interview-option-btn md-button';
            button.dataset.key = key;
            button.innerHTML = `<strong>${key}:</strong> ${q.options[key]}`;
            button.addEventListener('click', () => handleOptionClick(key));
            optionsContainerEl.appendChild(button);
        }
        
        feedbackEl.style.display = 'none';
        prevBtn.disabled = currentIndex === 0;
        nextBtn.innerText = 'Skip'; // Default to Skip
        nextBtn.disabled = false;
    };
    
    const handleOptionClick = (selectedKey) => {
        const q = questions[currentIndex];
        const isCorrect = selectedKey === q.correct_answer;
        userAnswers[currentIndex] = isCorrect;
        
        // Disable all option buttons to prevent re-answering
        const buttons = optionsContainerEl.querySelectorAll('.interview-option-btn');
        buttons.forEach(btn => {
            btn.disabled = true;
            // Highlight the correct and wrong answers
            if (btn.dataset.key === q.correct_answer) {
                btn.classList.add('correct');
            } else if (btn.dataset.key === selectedKey) {
                btn.classList.add('wrong');
            }
        });
        
        // Show detailed feedback text
        feedbackEl.style.display = 'block';
        feedbackEl.className = isCorrect ? 'correct' : 'wrong';
        const feedbackHeader = feedbackEl.querySelector('h4');
        if (feedbackHeader) feedbackHeader.innerText = isCorrect ? 'Correct!' : 'Incorrect';
        feedbackTextEl.innerText = `The correct answer was ${q.correct_answer}: ${q.options[q.correct_answer]}`;
        
        // Disable the "Skip" button after an answer is chosen
        nextBtn.disabled = true;

        // Automatically move to the next question after a short delay
        setTimeout(() => {
            if (currentIndex < questions.length - 1) {
                currentIndex++;
                renderQuestion();
            } else {
                showSummary();
            }
        }, 1200); // 1.2 second delay to see feedback
    };

    const showSummary = () => {
        contentEl.style.display = 'none';
        summaryEl.style.display = 'block';
        prevBtn.disabled = true;
        nextBtn.disabled = true;

        const correctCount = userAnswers.filter(a => a === true).length;
        scoreEl.innerText = `You scored ${correctCount} out of ${questions.length}.`;
        
        const topicStats = {};
        questions.forEach((q, index) => {
            const topic = q.topic || 'General';
            if (!topicStats[topic]) {
                topicStats[topic] = { correct: 0, total: 0 };
            }
            topicStats[topic].total++;
            if (userAnswers[index] === true) {
                topicStats[topic].correct++;
            }
        });

        analysisListEl.innerHTML = '';
        for (const topic in topicStats) {
            const stat = topicStats[topic];
            const percentage = Math.round((stat.correct / stat.total) * 100);
            const item = document.createElement('div');
            item.className = 'analysis-item';
            item.innerHTML = `
                <span>${topic}</span>
                <span>${stat.correct} / ${stat.total} (${percentage}%)</span>
            `;
            analysisListEl.appendChild(item);
        }

        wrongListEl.innerHTML = '';
        const wrongAnswers = questions.filter((q, index) => userAnswers[index] === false);

        if (wrongAnswers.length > 0) {
            wrongAnswers.forEach(q => {
                const item = document.createElement('div');
                item.className = 'wrong-item';
                item.innerHTML = `
                    <h4>Q: ${q.question}</h4>
                    <p><strong>Your Answer:</strong> ${userAnswers[questions.indexOf(q)] !== null ? 'Incorrect' : 'Skipped'}</p>
                    <p><strong>Correct Answer:</strong> ${q.correct_answer} - ${q.options[q.correct_answer]}</p>
                    <p><strong>Topic:</strong> ${q.topic || 'N/A'}</p>
                `;
                wrongListEl.appendChild(item);
            });
        } else {
            wrongListEl.innerHTML = '<p>Congratulations, you got everything right!</p>';
        }
    };

    startBtn.addEventListener('click', () => {
        resetState();
        interviewModalOverlay.style.display = 'flex';
        fetchQuestions();
    });

    closeBtn.addEventListener('click', () => {
        interviewModalOverlay.style.display = 'none';
    });

    correctBtn.addEventListener('click', () => {
        userAnswers[currentIndex] = true;
        nextBtn.click(); // Programmatically click next
    });

    wrongBtn.addEventListener('click', () => {
        userAnswers[currentIndex] = false;
        nextBtn.click(); // Programmatically click next
    });

    nextBtn.addEventListener('click', () => {
        if (userAnswers[currentIndex] === null) {
             userAnswers[currentIndex] = false; // Treat skipped as wrong
        }
        if (currentIndex < questions.length - 1) {
            currentIndex++;
            renderQuestion();
        } else {
            showSummary();
        }
    });

    prevBtn.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            renderQuestion();
        }
    });

    restartBtn.addEventListener('click', () => {
        summaryEl.style.display = 'none'; // Hide the summary before restarting
        resetState();
        fetchQuestions();
    });
};

document.addEventListener('DOMContentLoaded', initializeInterview);
document.addEventListener('page:loaded', initializeInterview); 