chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractContent") {
    console.log("Message received in content script");

    // Extract text content (remove HTML tags)
    const content = document.body.innerText.trim();
    console.log("Extracted text content:", content);

    // Send content to the backend API
    fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: content, url: false }) // url: false since we're sending raw text
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("API response:", data);

        // Parse the analysis text (similar to analyze.js)
        const cleanedText = data.analysis.trim();
        const sectionsRaw = cleanedText.split('\n\n');
        const sections = {
          summary: '',
          leaning: '',
          reasoning: ''
        };

        sectionsRaw.forEach(section => {
          section = section.trim();
          if (!section) return;
          const cleanSection = section.replace(/\*\*/g, '');
          if (cleanSection.startsWith('Summary:')) {
            sections.summary = cleanSection.replace(/^Summary:\s*/i, '').trim();
          } else if (cleanSection.match(/^(Political Leaning|Leaning|Bias):\s*/i)) {
            sections.leaning = cleanSection.replace(/^(Political Leaning|Leaning|Bias):\s*/i, '').trim();
          } else if (cleanSection.match(/^(Reasoning|Analysis|Explanation):\s*/i)) {
            sections.reasoning = cleanSection.replace(/^(Reasoning|Analysis|Explanation):\s*/i, '').trim();
          } else if (!sections.summary) {
            sections.summary = section.trim();
          }
        });

        console.log("Parsed sections:", sections);

        // Send parsed results to the popup
        sendResponse({
          status: "success",
          data: sections
        });
      })
      .catch(error => {
        console.error("Error calling API:", error);
        sendResponse({
          status: "error",
          message: error.message || "Failed to analyze content"
        });
      });

    // Return true for asynchronous response
    return true;
  } else if (request.action === "updateSummary") {
    // Handle the summary text for highlighting
    const summary = request.summary;
    const sentences = summary.split('\n');
    console.log("Sentences to highlight:", sentences);

    // Function to highlight sentences in yellow
    const highlightSentences = (sentences) => {
      sentences.forEach(sentence => {
        const escapedSentence = sentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const pattern = new RegExp(`(${escapedSentence})`, 'g');
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while (node = walker.nextNode()) {
          if (node.nodeValue.trim()) {
            const parent = node.parentNode;
            const newNodeValue = node.nodeValue.replace(pattern, '<span style="background-color: yellow;">$1</span>');
            if (newNodeValue !== node.nodeValue) {
              const tempDiv = document.createElement('div');
              tempDiv.innerHTML = newNodeValue;
              while (tempDiv.firstChild) {
                parent.insertBefore(tempDiv.firstChild, node);
              }
              parent.removeChild(node);
            }
          }
        }
      });
    };

    highlightSentences(sentences);
    sendResponse({ status: "success" });
    return true;
  }
});