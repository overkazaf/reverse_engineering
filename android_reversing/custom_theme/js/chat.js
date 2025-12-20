// Keep existing chat app logic
function initializeApp() {
    // --- DOM Elements ---
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow) return;

    const toggleButton = document.getElementById('chat-toggle-button');
    const closeButton = document.getElementById('chat-close-button');
    const sendButton = document.getElementById('chat-send-button');
    const chatInput = document.getElementById('chat-input');
    const messagesContainer = document.getElementById('chat-messages');
    const fullscreenButton = document.getElementById('chat-fullscreen-button');
    const chatHeader = document.getElementById('chat-header');
    const chatTitle = document.getElementById('chat-title');
    const chatView = document.getElementById('chat-view');
    const shellView = document.getElementById('shell-view');
    const shellButton = document.getElementById('chat-shell-button');
    const shellOutput = document.getElementById('shell-output');
    const shellInput = document.getElementById('shell-input');
    const fileWriteModal = document.getElementById('file-write-modal');
    const modalFilepath = document.getElementById('modal-filepath');
    const modalFileContent = document.getElementById('modal-file-content');
    const modalConfirmButton = document.getElementById('modal-confirm-button');
    const modalCancelButton = document.getElementById('modal-cancel-button');
    
    let fileWriteCallback = null;
    let currentView = 'chat';

    // --- Core Logic ---

    function setupEventListeners() {
        toggleButton.addEventListener('click', toggleChatWindow);
        closeButton.addEventListener('click', closeChatWindow);
        sendButton.addEventListener('click', sendMessage);
        fullscreenButton.addEventListener('click', toggleFullscreen);
        shellButton.addEventListener('click', toggleShellView);

        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        chatInput.addEventListener('input', autoResizeInput);
        shellInput.addEventListener('keydown', handleShellInputKeydown);

        makeDraggable(chatWindow, chatHeader);

        modalCancelButton.addEventListener('click', () => fileWriteModal.style.display = 'none');
        modalConfirmButton.addEventListener('click', () => {
            if (fileWriteCallback) fileWriteCallback();
            fileWriteModal.style.display = 'none';
        });

        messagesContainer.addEventListener('click', handleMessageContainerClick);
        const resizeObserver = new ResizeObserver(saveState);
        resizeObserver.observe(chatWindow);
    }

    function toggleChatWindow() {
        chatWindow.classList.toggle('visible');
        if (chatWindow.classList.contains('visible')) {
            if (currentView === 'chat') chatInput.focus();
            else shellInput.focus();
        }
        saveState();
    }
    
    function closeChatWindow() {
        chatWindow.classList.remove('visible');
        saveState();
    }

    async function sendMessage() {
        const prompt = chatInput.value.trim();
        if (!prompt) return;

        appendMessage(prompt, 'user');
        chatInput.value = '';
        autoResizeInput();
        sendButton.disabled = true;

        const botMessageDiv = appendMessage('', 'bot');

        try {
            const response = await fetch('http://127.0.0.1:5001/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt }),
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);
            
            const responseText = await response.text();
            renderMarkdown(botMessageDiv, responseText);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        } catch (error) {
            console.error('Fetch error:', error);
            renderMarkdown(botMessageDiv, `<p>Sorry, an error occurred. See the console for details.</p>`);
        } finally {
            sendButton.disabled = false;
            saveState();
        }
    }
    
    async function executeShellCommand(command) {
        const commandEcho = document.createElement('div');
        commandEcho.innerHTML = `<span class="shell-prompt">&gt;</span><span class="shell-command">${command}</span>`;
        shellOutput.appendChild(commandEcho);

        const resultElement = document.createElement('div');
        resultElement.className = 'shell-result';
        shellOutput.appendChild(resultElement);
        
        try {
            const response = await fetch('http://127.0.0.1:5001/shell', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command }),
            });
            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            resultElement.textContent = await response.text();
        } catch (error) {
            resultElement.textContent = `Error: ${error.message}`;
        }
        shellOutput.scrollTop = shellOutput.scrollHeight;
        saveState();
    }

    async function writeFile(filepath, content) {
        try {
            const response = await fetch('http://127.0.0.1:5001/write-file', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath, content }),
            });
            const result = await response.json();
            if (result.status === 'success') {
                appendMessage(`✅ File '${filepath}' saved successfully.`, 'bot_system');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('File write error:', error);
            appendMessage(`❌ Error saving file: ${error.message}`, 'bot');
        }
    }

    function autoResizeInput() {
        chatInput.style.height = 'auto';
        const newHeight = Math.min(chatInput.scrollHeight, 200);
        chatInput.style.height = newHeight + 'px';
    }

    function handleShellInputKeydown(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const command = shellInput.value.trim();
            if (command) {
                executeShellCommand(command);
                shellInput.value = '';
            }
        }
    }

    function handleMessageContainerClick(event) {
        const target = event.target;
        if (!target) return;
        
        const copyButton = target.closest('.copy-code-button');
        if (copyButton) {
            const code = copyButton.closest('pre').querySelector('code').innerText;
            navigator.clipboard.writeText(code).then(() => {
                copyButton.innerText = 'Copied!';
                setTimeout(() => copyButton.innerText = 'Copy', 2000);
            });
            return;
        }

        const proposeButton = target.closest('.propose-file-button');
        if (proposeButton) {
            const filepath = proposeButton.dataset.filepath;
            const content = proposeButton.closest('pre').querySelector('code').innerText;
            showFileWriteModal(filepath, content);
        }
    }

    function appendMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', `${sender}-message`);

        const avatar = document.createElement('span');
        avatar.className = 'chat-avatar';
        let avatarIcon = 'psychology';
        if (sender === 'user') avatarIcon = 'person';
        avatar.innerHTML = `<span class="material-icons">${avatarIcon}</span>`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'chat-message-content';
        renderMarkdown(contentDiv, text);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return contentDiv;
    }

    function renderMarkdown(element, text) {
        if (typeof marked === 'undefined' || typeof DOMPurify === 'undefined') {
            element.innerHTML = text.replace(/\n/g, '<br>');
            return;
        }
        const dirty = marked.parse(text, { breaks: true, gfm: true });
        element.innerHTML = DOMPurify.sanitize(dirty);

        if (typeof hljs !== 'undefined') {
            element.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightBlock(block);
                if (element.closest('.bot-message')) {
                    const pre = block.parentElement;
                    if (!pre.querySelector('.copy-code-button')) {
                        const copyButton = document.createElement('button');
                        copyButton.innerText = 'Copy';
                        copyButton.className = 'copy-code-button';
                        pre.style.position = 'relative';
                        pre.appendChild(copyButton);
                    }
                }
            });
        }
    }

    function showFileWriteModal(filepath, content) {
        modalFilepath.innerText = filepath;
        modalFileContent.innerText = content;
        fileWriteCallback = () => writeFile(filepath, content);
        fileWriteModal.style.display = 'flex';
    }

    function makeDraggable(element, handle) {
        let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
        handle.onmousedown = dragMouseDown;
        function dragMouseDown(e) {
            e = e || window.event;
            e.preventDefault();
            pos3 = e.clientX;
            pos4 = e.clientY;
            document.onmouseup = closeDragElement;
            document.onmousemove = elementDrag;
        }
        function elementDrag(e) {
            e = e || window.event;
            e.preventDefault();
            pos1 = pos3 - e.clientX;
            pos2 = pos4 - e.clientY;
            pos3 = e.clientX;
            pos4 = e.clientY;
            element.style.top = (element.offsetTop - pos2) + "px";
            element.style.left = (element.offsetLeft - pos1) + "px";
        }
        function closeDragElement() {
            document.onmouseup = null;
            document.onmousemove = null;
        }
    }
    
    function toggleFullscreen() {
        chatWindow.classList.toggle('fullscreen');
        const icon = fullscreenButton.querySelector('.material-icons');
        icon.textContent = chatWindow.classList.contains('fullscreen') ? 'fullscreen_exit' : 'fullscreen';
        saveState();
    }
    
    function toggleShellView() {
        const shellIcon = shellButton.querySelector('.material-icons');
        if (currentView === 'chat') {
            currentView = 'shell';
            chatView.style.display = 'none';
            shellView.style.display = 'flex';
            chatTitle.innerText = 'Local Shell';
            shellIcon.innerText = 'chat';
            shellInput.focus();
        } else {
            currentView = 'chat';
            shellView.style.display = 'none';
            chatView.style.display = 'flex';
            chatTitle.innerText = 'Chat with Gemini';
            shellIcon.innerText = 'terminal';
            chatInput.focus();
        }
        saveState();
    }

    function saveState() {
        const state = {
            visible: chatWindow.classList.contains('visible'),
            fullscreen: chatWindow.classList.contains('fullscreen'),
            position: { top: chatWindow.style.top, left: chatWindow.style.left },
            size: { width: chatWindow.style.width, height: chatWindow.style.height },
            view: currentView,
        };
        localStorage.setItem('chatState', JSON.stringify(state));
    }

    function loadState() {
        const state = JSON.parse(localStorage.getItem('chatState'));
        if (state) {
            if (state.visible) chatWindow.classList.add('visible');
            if (state.fullscreen) toggleFullscreen();
            if (state.position && state.position.top && state.position.left) {
                chatWindow.style.top = state.position.top;
                chatWindow.style.left = state.position.left;
            }
            if (state.size && state.size.width && state.size.height) {
                chatWindow.style.width = state.size.width;
                chatWindow.style.height = state.size.height;
            }
            if (state.view && state.view !== currentView) {
                toggleShellView();
            }
        }
    }

    // --- Kick things off ---
    setupEventListeners();
    loadState();
}

// --- New Standalone Interactive Quiz Logic ---
function initializeQuiz() {
    // --- DOM Elements ---
    const startInterviewButton = document.getElementById('start-interview-button');
    const quizOverlay = document.getElementById('quiz-modal-overlay');

    if (!startInterviewButton || !quizOverlay) {
        // If the quiz elements aren't on the page, do nothing.
        return;
    }

    const quizModal = document.getElementById('quiz-modal');
    const closeButton = document.getElementById('quiz-close-button');
    const startButton = document.getElementById('quiz-start-button');
    
    // Views
    const startView = document.getElementById('quiz-start-view');
    const loadingView = document.getElementById('quiz-loading-view');
    const questionView = document.getElementById('quiz-question-view');
    const resultsView = document.getElementById('quiz-results-view');

    // Question View Elements
    const progressBar = document.getElementById('quiz-progress');
    const progressText = document.getElementById('quiz-progress-text');
    const questionText = document.getElementById('quiz-question-text');
    const optionsContainer = document.getElementById('quiz-options-container');
    const nextButton = document.getElementById('quiz-next-button');

    // Results View Elements
    const scoreText = document.getElementById('quiz-score-text');
    const summaryContainer = document.getElementById('quiz-summary-container');
    const reviewButton = document.getElementById('quiz-review-button');
    const retryButton = document.getElementById('quiz-retry-button');

    // --- State ---
    let quizData = [];
    let userAnswers = [];
    let currentQuestionIndex = 0;
    let score = 0;

    // --- Core Logic ---
    function setupEventListeners() {
        startInterviewButton.addEventListener('click', openQuiz);
        closeButton.addEventListener('click', closeQuiz);
        startButton.addEventListener('click', fetchQuiz);
        nextButton.addEventListener('click', nextQuestion);
        retryButton.addEventListener('click', resetAndStart);
        reviewButton.addEventListener('click', showReview);
    }

    function openQuiz() {
        quizOverlay.style.display = 'flex';
        resetQuiz();
    }

    function closeQuiz() {
        if(questionView.style.display !== 'none' && !confirm("Are you sure you want to exit? Your progress will be lost.")) {
            return;
        }
        quizOverlay.style.display = 'none';
    }
    
    function resetAndStart() {
        resetQuiz();
        fetchQuiz();
    }
    
    function resetQuiz() {
        // Reset state
        quizData = [];
        userAnswers = [];
        currentQuestionIndex = 0;
        score = 0;
        
        // Reset UI
        showView('start');
        summaryContainer.innerHTML = '';
        nextButton.disabled = true;
        nextButton.textContent = "Next Question";
    }
    
    function showView(viewName) {
        [startView, loadingView, questionView, resultsView].forEach(v => v.style.display = 'none');
        document.getElementById(`quiz-${viewName}-view`).style.display = 'block';
    }

    async function fetchQuiz() {
        showView('loading');
        try {
            let path = window.location.pathname;
            path = path.slice(0, path.lastIndexOf('.html')) + '.md';
            if (path.startsWith('/')) path = path.substring(1);

            const response = await fetch('http://127.0.0.1:5001/mock-interview', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filepath: path }),
            });
            const data = await response.json();

            if (data.status === 'success' && data.quiz.questions.length > 0) {
                quizData = data.quiz.questions;
                showView('question');
                displayQuestion();
            } else {
                throw new Error(data.message || 'Failed to load quiz.');
            }
        } catch (error) {
            alert(`Error: ${error.message}`);
            showView('start');
        }
    }

    function displayQuestion() {
        const question = quizData[currentQuestionIndex];
        
        // Update progress
        const progressPercentage = ((currentQuestionIndex) / quizData.length) * 100;
        progressBar.style.width = `${progressPercentage}%`;
        progressText.textContent = `Question ${currentQuestionIndex + 1} of ${quizData.length}`;

        questionText.textContent = question.question;
        optionsContainer.innerHTML = '';
        
        for (const [key, value] of Object.entries(question.options)) {
            const optionButton = document.createElement('button');
            optionButton.className = 'quiz-option';
            optionButton.dataset.key = key;
            optionButton.innerHTML = `<strong>${key}</strong>: ${value}`;
            optionButton.addEventListener('click', () => selectOption(optionButton, key));
            optionsContainer.appendChild(optionButton);
        }
        nextButton.disabled = true;
        if(currentQuestionIndex === quizData.length - 1) {
            nextButton.textContent = "Finish & See Results";
        }
    }
    
    function selectOption(selectedButton, key) {
        // Deselect any previously selected option
        const currentlySelected = optionsContainer.querySelector('.selected');
        if (currentlySelected) {
            currentlySelected.classList.remove('selected');
        }
        
        selectedButton.classList.add('selected');
        userAnswers[currentQuestionIndex] = key;
        nextButton.disabled = false;
    }

    function nextQuestion() {
        // Logic to show correct/incorrect before moving on
        const question = quizData[currentQuestionIndex];
        const selectedKey = userAnswers[currentQuestionIndex];
        const correctKey = question.correct_answer;
        
        if(selectedKey === correctKey) {
            score++;
        }

        currentQuestionIndex++;
        if (currentQuestionIndex < quizData.length) {
            displayQuestion();
        } else {
            showResults();
        }
    }

    function showResults() {
        showView('results');
        scoreText.textContent = `You scored ${score} out of ${quizData.length}!`;
        
        // Check if there are any mistakes to review
        const mistakes = quizData.filter((q, i) => userAnswers[i] !== q.correct_answer);
        reviewButton.style.display = mistakes.length > 0 ? 'inline-flex' : 'none';
        
        // Pre-generate summary for review
        let summaryHTML = '';
        mistakes.forEach((q, i) => {
            summaryHTML += `
                <div class="quiz-summary-item">
                    <p><strong>Question:</strong> ${q.question}</p>
                    <p><strong>Your Answer (Incorrect):</strong> ${userAnswers[quizData.indexOf(q)]}. ${q.options[userAnswers[quizData.indexOf(q)]]}</p>
                    <p><strong>Correct Answer:</strong> ${q.correct_answer}. ${q.options[q.correct_answer]}</p>
                </div>
            `;
        });
        summaryContainer.innerHTML = summaryHTML;
        summaryContainer.style.display = 'none'; // Initially hidden
    }
    
    function showReview() {
        summaryContainer.style.display = 'block';
        reviewButton.style.display = 'none'; // Hide after clicking
    }

    // --- Kick things off ---
    setupEventListeners();
}

// --- Application Entry Point ---
if (typeof document$ !== 'undefined') {
    document$.subscribe(() => {
        setTimeout(() => {
            initializeApp(); // For the chat
            initializeQuiz();  // For the new quiz
        }, 0);
    });
} else {
    document.addEventListener('DOMContentLoaded', () => {
        initializeApp();
        initializeQuiz();
    });
} 