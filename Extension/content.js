// content.js

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

      // Get the initial HTML content
      let text = document.body.innerHTML;

      // Function to highlight sentences in red
      const highlightSentences = (content, sentences) => {
        // Escape special characters in sentences to treat them as literal text in regex
        const escapedSentences = sentences.map(sentence => 
          sentence.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        );
        
        // Create a single regex pattern that matches any of the sentences
        const pattern = new RegExp(`(${escapedSentences.join('|')})`, 'g');
        
        // Replace all matching sentences with wrapped versions
        return content.replace(pattern, '<span style="background-color: yellow;">$1</span>');
      };

      // Apply the highlighting
      document.body.innerHTML = highlightSentences(text, sentences);

      // Send a response back (optional)
      sendResponse({ status: "success" });
  }

  // Return true to indicate you want to send a response asynchronously
  return true;
});