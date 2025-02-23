// Listen for messages from the popup script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractContent") {
      console.log("Message received in content script"); 

      const content = document.body.innerText.trim();
      console.log("Extracted content:", content);
  
      // Send the content back to the popup script
      sendResponse({ content: content });
    }
  
    // Return true to indicate you want to send a response asynchronously
    return true;
  });