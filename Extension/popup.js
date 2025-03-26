const spinner = document.createElement('div');
spinner.className = 'spinner';
spinner.innerHTML = '<div class="loader"></div>';
const analyzebtn = document.getElementById("analyzeButton")

function displayResult(result, resultContainer) {
    try {
        // Saving data with a unique key
        const uniqueKey = `result_${Date.now()}`;
        if (chrome && chrome.storage && chrome.storage.local) {
            chrome.storage.local.set({ [uniqueKey]: result }, () => {
                console.log("Data saved with key:", uniqueKey);
            });
            console.log("Result stored in local storage");
        } else {
            console.warn("chrome.storage is not available. Falling back to localStorage.");
            localStorage.setItem(uniqueKey, JSON.stringify(result));
            console.log("Result stored in localStorage");
        }
    } catch (error) {
        console.error('Error storing result in session storage:', error);
        resultContainer.innerHTML = '<p class="error">Failed to store the result. Please try again.</p>';
    }
}

analyzebtn.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { action: "extractContent" }, async (response) => {
      if (response && response.content) {
          const content = response.content;
          console.log("Extracted content sent to backend");
          const resultContainer = document.getElementById("result");
          resultContainer.appendChild(spinner);

          try{
                const result = await fetch("http://127.0.0.1:8000/analyze", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ text: content, url: false }),
                });

                const biasReport = await result.json();
                console.log("Bias report from backend:", biasReport);

                // Send the summary text back to the content script
                //   chrome.tabs.sendMessage(tab.id, { action: "updateSummary", summary: biasReport.summary }, (response) => {
                //       if (response && response.status === "success") {
                //           console.log("Page updated successfully");
                //       }
                //   });

                // Show the "Read More" button
                const BASE_URL = "https://media-bias.netlify.app/";
                const LOCAL_URL = "http://127.0.0.1:5500/Website/";

                displayResult(biasReport, resultContainer);
                const readMoreLink = document.getElementById("readMore");
                readMoreLink.href = `${LOCAL_URL}details.html`;
                readMoreLink.style.display = "block";
                
                // Update the popup with the bias report text
                resultContainer.innerHTML = `
                    <h3>Left Bias: ${biasReport.left.length} lines</h3>
                    <h3>Right Bias: ${biasReport.right.length} lines</h3>
                    <h3>Center Bias: ${biasReport.center.length} lines</h3>
                `;

                console.log(`Left Bias: ${biasReport.left.length} lines`);
                console.log(`Right Bias: ${biasReport.right.length} lines`);
                console.log(`Center Bias: ${biasReport.center.length} lines`);

                // Send the bias report text to the content script to update the webpage
                chrome.tabs.sendMessage(tab.id, { action: "updateBias", text: biasReport.text }, (response) => {
                    if (response && response.status === "success") {
                        console.log("Webpage updated with bias report text successfully");
                    }
                });

        } catch (error) {
            console.error('Error:', error);
            resultContainer.innerHTML = '<p class="error">There was an error processing your request. Please try again later.</p>';
        } finally {
            spinner.remove();
            analyzebtn.remove();
        }
      }
  });
});