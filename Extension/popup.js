// popup.js

document.getElementById("analyzeButton").addEventListener("click", async () => {
  // Get the active tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  // Send a message to the content script to extract the page content
  chrome.tabs.sendMessage(tab.id, { action: "extractContent" }, async (response) => {
      if (response && response.content) {
          const content = response.content;
          console.log("Extracted content sent to backend");

          // Send the content to the backend
          const backendUrl = "http://127.0.0.1:8000/analyze";
          const result = await fetch(backendUrl, {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ text: content }),
          });

          const biasReport = await result.json();
          console.log("Bias report from backend:", biasReport);

          // Send the summary text back to the content script
          chrome.tabs.sendMessage(tab.id, { action: "updatePage", summary: biasReport.summary }, (response) => {
              if (response && response.status === "success") {
                  console.log("Page updated successfully");
              }
          });

          // Show the "Read More" button
          const readMoreLink = document.getElementById("readMore");
          readMoreLink.href = `details.html?content=${encodeURIComponent(content)}`;
          readMoreLink.style.display = "block";

          const predicted_class = document.getElementById("result");
          result.innerText = biasReport.predicted_class;
      }
  });
});