document.getElementById("analyzeButton").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { action: "extractContent" }, async (response) => {
      if (response && response.content) {
          const content = response.content;
          console.log("Extracted content sent to backend");

          const result = await fetch("http://127.0.0.1:8000/analyze", {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({ text: content }),
          });

          const biasReport = await result.json();
          console.log("Bias report from backend:", biasReport);

          // Send the summary text back to the content script
          chrome.tabs.sendMessage(tab.id, { action: "updateSummary", summary: biasReport.summary }, (response) => {
              if (response && response.status === "success") {
                  console.log("Page updated successfully");
              }
          });

          // Show the "Read More" button
          const readMoreLink = document.getElementById("readMore");
          readMoreLink.href = `../Website/details.html?content=${encodeURIComponent(content)}`;
          readMoreLink.style.display = "block";

          // Update the popup with the bias report text
          const predicted_class = document.getElementById("result");
          predicted_class.innerText = biasReport.text;

          // Send the bias report text to the content script to update the webpage
          chrome.tabs.sendMessage(tab.id, { action: "updateBias", text: biasReport.text }, (response) => {
              if (response && response.status === "success") {
                  console.log("Webpage updated with bias report text successfully");
              }
          });
      }
  });
});