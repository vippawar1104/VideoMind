// Function to show status message
function showStatus(message, isError = false) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    statusDiv.className = 'status ' + (isError ? 'error' : 'success');
    setTimeout(() => {
        statusDiv.style.display = 'none';
    }, 3000);
}

// Function to get current YouTube video URL
function getCurrentVideoUrl() {
    return new Promise((resolve) => {
        chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
            const url = tabs[0].url;
            if (url.includes('youtube.com/watch')) {
                resolve(url);
            } else {
                resolve(null);
            }
        });
    });
}

// Function to open the web app with the video URL
function openWebApp(videoUrl) {
    const baseUrl = 'http://localhost:8501';
    const url = `${baseUrl}?video=${encodeURIComponent(videoUrl)}`;
    chrome.tabs.create({ url });
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const openAppBtn = document.getElementById('openAppBtn');

    analyzeBtn.addEventListener('click', async () => {
        const videoUrl = await getCurrentVideoUrl();
        if (videoUrl) {
            openWebApp(videoUrl);
        } else {
            showStatus('Please open a YouTube video first!', true);
        }
    });

    openAppBtn.addEventListener('click', () => {
        openWebApp('');
    });
});

// Content script functionality
if (window.location.hostname === 'www.youtube.com') {
    // Add analyze button to YouTube interface
    function addAnalyzeButton() {
        const buttonContainer = document.querySelector('#top-level-buttons-computed');
        if (buttonContainer && !document.getElementById('ai-analyze-btn')) {
            const analyzeBtn = document.createElement('button');
            analyzeBtn.id = 'ai-analyze-btn';
            analyzeBtn.className = 'style-scope ytd-button-renderer style-text';
            analyzeBtn.innerHTML = '🤖 Analyze with AI';
            analyzeBtn.style.marginLeft = '8px';
            
            analyzeBtn.addEventListener('click', () => {
                const videoUrl = window.location.href;
                openWebApp(videoUrl);
            });
            
            buttonContainer.appendChild(analyzeBtn);
        }
    }

    // Run when page loads
    addAnalyzeButton();

    // Run when YouTube's dynamic content updates
    const observer = new MutationObserver(addAnalyzeButton);
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}
