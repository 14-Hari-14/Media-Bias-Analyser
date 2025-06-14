const spinner = document.createElement('div');
spinner.className = 'spinner';
spinner.innerHTML = '<div class="loader"></div>';

const analyzeBtn = document.getElementById('analyzeButton');
const resultContainer = document.getElementById('result');
const readMoreLink = document.getElementById('readMore');

function displayResult(result, resultContainer) {
    try {
        // Save data with a unique key
        const uniqueKey = `result_${Date.now()}`;
        if (chrome && chrome.storage && chrome.storage.local) {
            chrome.storage.local.set({ [uniqueKey]: result }, () => {
                console.log('Data saved with key:', uniqueKey);
            });
            console.log('Result stored in chrome.storage.local');
        } else {
            console.warn('chrome.storage is not available. Falling back to localStorage.');
            localStorage.setItem(uniqueKey, JSON.stringify(result));
            console.log('Result stored in localStorage');
        }
    } catch (error) {
        console.error('Error storing result:', error);
        resultContainer.innerHTML = '<p class="error">Failed to store the result. Please try again.</p>';
    }
}

analyzeBtn.addEventListener('click', async () => {
    resultContainer.appendChild(spinner);

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        chrome.tabs.sendMessage(tab.id, { action: 'extractContent' }, (response) => {
            if (chrome.runtime.lastError) {
                console.error('Message error:', chrome.runtime.lastError.message);
                resultContainer.innerHTML = `<p class="error">Error: ${chrome.runtime.lastError.message}</p>`;
                spinner.remove();
                analyzeBtn.remove();
                return;
            }

            if (response && response.status === 'success') {
                const { summary, leaning, reasoning } = response.data;
                console.log('Parsed API response:', { summary, leaning, reasoning });

                // Save and display results
                displayResult(response.data, resultContainer);
                resultContainer.innerHTML = `
          <div class="result-card">
            <h3>Article Summary</h3>
            <p>${summary || 'No summary available'}</p>
          </div>
          <div class="result-card">
            <h3>Political Leaning</h3>
            <p class="leaning ${leaning ? leaning.toLowerCase().split(' ')[0] : ''}">
              ${leaning || 'Could not determine'}
            </p>
          </div>
          <div class="result-card">
            <h3>Detailed Analysis</h3>
            <p>${reasoning || 'No detailed analysis available'}</p>
          </div>
        `;

                // Show "Read More" link
                const BASE_URL = 'http://localhost:8080/Website/';
                readMoreLink.href = `${BASE_URL}details.html?key=${uniqueKey}`;
                readMoreLink.style.display = 'block';

                // // Optional: Send summary for highlighting (uncomment if needed)
                // chrome.tabs.sendMessage(tab.id, { action: 'updateSummary', summary }, (highlightResponse) => {
                //   if (highlightResponse && highlightResponse.status === 'success') {
                //     console.log('Page updated successfully with highlights');
                //   }
                // });
            } else {
                console.error('Error from content script:', response.message);
                resultContainer.innerHTML = `<p class="error">Error: ${response.message}</p>`;
            }

            spinner.remove();
            analyzeBtn.remove();
        });
    } catch (error) {
        console.error('Error:', error);
        resultContainer.innerHTML = '<p class="error">There was an error processing your request. Please try again later.</p>';
        spinner.remove();
        analyzeBtn.remove();
    }
});