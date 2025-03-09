document.addEventListener("DOMContentLoaded", () => {
    // Add an event listener to the form for the "submit" event
    document.getElementById("articleLinkForm").addEventListener("submit", async (event) => {
        event.preventDefault();

        // Get the input value (link entered by the user)
        const input = document.querySelector(".linkInput");
        const link = input.value;

        console.log("Link entered:", link);

        try {
            // Send the link to the background script for processing
            const response = await chrome.runtime.sendMessage({ action: "processLink", link });

            // Handle the response from the background script
            if (response && response.success) {
                console.log("Link processed successfully:", response.data);
                alert("Link processed successfully!");
            } else {
                throw new Error(response?.error || "Failed to process link");
            }
        } catch (error) {
            // Handle errors
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        }
    });
});