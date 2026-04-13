document.addEventListener('DOMContentLoaded', () => {
    // ---- Theme Toggle Functionality ----
    const themeToggleBtn = document.getElementById('theme-toggle');
    const htmlElement = document.documentElement;
    const themeIcon = themeToggleBtn.querySelector('ion-icon');

    // Retrieve saved user setting if available
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);

    themeToggleBtn.addEventListener('click', () => {
        const currentTheme = htmlElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    });

    function setTheme(theme) {
        htmlElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Dynamically toggle icon based on mode
        if(theme === 'dark') {
            themeIcon.setAttribute('name', 'sunny-outline');
        } else {
            themeIcon.setAttribute('name', 'moon-outline');
        }
    }

    // ---- Smooth Scrolling Integration ----
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if(targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // ---- Document/PDF Upload Dropzone ----
    const dropzone = document.getElementById('upload-dropzone');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const uploadBtn = document.getElementById('upload-btn');
    
    let selectedFiles = [];

    // Prompt OS File Browser
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    // Highlight area gently on dragover
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            handleFiles(fileInput.files);
        }
    });

    function handleFiles(files) {
        // Only accept new pdfs and prevent duplicate entries visually
        Array.from(files).forEach(file => {
            if (file.type === 'application/pdf' && !selectedFiles.some(f => f.name === file.name)) {
                selectedFiles.push(file);
            }
        });
        updateFileList();
    }

    function updateFileList() {
        fileList.innerHTML = ''; // Wipe and rebuild
        if (selectedFiles.length === 0) {
            uploadBtn.disabled = true;
            return;
        }

        uploadBtn.disabled = false;
        
        selectedFiles.forEach((file, index) => {
            const li = document.createElement('li');
            li.className = 'file-item';
            
            // Calc standard KB
            const sizeKB = (file.size / 1024).toFixed(1);
            
            li.innerHTML = `
                <div style="display: flex; gap: 0.5rem; align-items: center; max-width: 60%;">
                    <ion-icon name="document-text-outline" style="color: var(--primary-color); font-size: 1.2rem;"></ion-icon>
                    <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-weight: 500;">${file.name}</span>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: center; color: var(--text-secondary); font-size: 0.8rem;">
                    <span>${sizeKB} KB</span>
                    <button class="remove-btn" data-index="${index}" style="color: #ef4444; font-size: 1.25rem; display: flex; align-items: center; transition: transform 0.2s;">
                        <ion-icon name="close-circle-outline"></ion-icon>
                    </button>
                </div>
            `;
            fileList.appendChild(li);
        });

        // Setup removal interactions
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                // Hover effect logic implemented via CSS usually, button acts rawly here
                const idx = parseInt(e.currentTarget.getAttribute('data-index'));
                selectedFiles.splice(idx, 1);
                updateFileList();
            });
        });
    }

    // Interactive Sync Button to mock Vector Database insertion
    uploadBtn.addEventListener('click', () => {
        uploadBtn.innerHTML = '<ion-icon name="reload-outline" style="animation: spin 1s linear infinite;"></ion-icon> Uploading...';
        uploadBtn.disabled = true;

        // Artificial delay simulating Endee API
        setTimeout(() => {
            uploadBtn.innerHTML = '<ion-icon name="checkmark-circle-outline"></ion-icon> Synced Successfully';
            uploadBtn.style.background = 'var(--success-color)';
            uploadBtn.style.boxShadow = 'none';
            selectedFiles = [];
            
            setTimeout(() => {
                updateFileList();
                uploadBtn.innerHTML = 'Sync to Vector Database';
                // Reset styling to primary button state
                uploadBtn.style.background = ''; 
                uploadBtn.style.boxShadow = '';
                
                // Emulate assistant responding to knowledge insertion
                addMessage('Documents received and indexed into the Endee vector store! What would you like to know about them?', 'ai');
            }, 2000);
        }, 1500);
    });

    // ---- Chat Application Features ----
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const chatHistory = document.getElementById('chat-history');

    // Auto-expanding chat bubble based on text input volume
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value.trim() === '') {
            this.style.height = '48px';
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        // Define chat styling conditionally
        if (sender === 'ai') {
            messageDiv.innerHTML = `
                <div class="avatar"><ion-icon name="sparkles-outline"></ion-icon></div>
                <div class="msg-content">${text}</div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="msg-content">${text}</div>
            `;
        }
        
        chatHistory.appendChild(messageDiv);
        
        // Scroll smoothly to newly attached output node
        chatHistory.scrollTo({
            top: chatHistory.scrollHeight,
            behavior: 'smooth'
        });
    }

    function processUserMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        
        // Standardize text area height and clean
        chatInput.value = '';
        chatInput.style.height = '48px';

        // Simulate a RAG fetch + LLM Generation processing duration (1 to 2.5 seconds)
        setTimeout(() => {
            const responses = [
                "Based on the parsed documentation chunks, your data highlights the integration parameters optimized for fast inference.",
                "I retrieved a highly relevant section specifying that Endee interacts locally without exposing data to public clouds, besides the secure Gemini API tunnel.",
                "I am searching through the embedded chunks but nothing directly matches yet. Could you clarify?",
                "Absolutely. The technical specification notes that Gemini 1.5 Pro functions beautifully when parsing complex vector intersections."
            ];
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            addMessage(randomResponse, 'ai');
        }, 1000 + Math.random() * 1500);
    }

    sendBtn.addEventListener('click', processUserMessage);
    
    // Support enter wrapping behavior with SHIFT modifiers commonly requested
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            processUserMessage();
        }
    });

    // Provide inline spinning keyframes for icons used in pure JS without dirtying the CSS file
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes spin { 100% { transform: rotate(360deg); } }
    `;
    document.head.appendChild(style);
});
