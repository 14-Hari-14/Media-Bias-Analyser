// Listen for messages from the popup script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extractContent") {
      console.log("Message received in content script");

      // Extract the page content
      const content = document.body.innerHTML.trim();
      console.log("Extracted content:", content);

      // Send the content back to the popup script
      sendResponse({ content: content });
  } else if (request.action === "updateSummary") {
      // Handle the summary text from the popup script
      const summary = request.summary;

      // Split the summary text by '\n'
      const sentences = summary.split('\n');
      console.log(sentences);

      // Function to highlight sentences in red
      const highlightSentences = (sentences) => {
        sentences.forEach(sentence => {
          // Escape special characters in sentences to treat them as literal text in regex
          const escapedSentence = sentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          
          // Create a regex pattern that matches the sentence
          const pattern = new RegExp(`(${escapedSentence})`, 'g');
          
          // Find all text nodes and replace matching sentences with wrapped versions
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

      // Apply the highlighting
      highlightSentences(sentences);

      // Send a response back (optional)
      sendResponse({ status: "success" });
  }

  // Return true to indicate you want to send a response asynchronously
  return true;
});