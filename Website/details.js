// Add an event listener to the form for the "submit" event
document.getElementById("articleLinkForm").addEventListener("submit", async (event) => {
    // Prevent the default form submission behavior (page reload)
    event.preventDefault();

    // Get the link from the input box
    const input = document.querySelector(".linkInput");
    const link = input.value;

    console.log("Link entered:", link);

    try {
        // Send the link to the backend to fetch and extract content
        const backendUrl = "http://your-backend-server.com/extract-content"; // Replace with your backend URL
        const result = await fetch(backendUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ link }), // Send the link to the backend
        });

        // Check if the backend request was successful
        if (!result.ok) {
            throw new Error("Failed to fetch content from the backend");
        }

        // Parse the response from the backend
        const data = await result.json();
        const content = data.content; // Extracted content from the website
        console.log("Extracted content:", content);

        // Send the extracted content to the backend for bias analysis
        const biasAnalysisUrl = "http://127.0.0.1:8000/analyze"; // Replace with your backend URL
        const biasResult = await fetch(biasAnalysisUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: content }), // Send the extracted content for analysis
        });

        // Check if the bias analysis request was successful
        if (!biasResult.ok) {
            throw new Error("Failed to analyze bias");
        }

        // Parse the bias analysis response
        const biasReport = await biasResult.json();
        console.log("Bias report from backend:", biasReport);

        // Show the "Read More" button and set its href to the details page with the content
        const readMoreLink = document.getElementById("readMore");
        readMoreLink.href = `../Website/details.html?content=${encodeURIComponent(content)}`;
        readMoreLink.style.display = "block";

        // Update the popup with the bias report text
        const predictedClassElement = document.getElementById("result");
        predictedClassElement.innerText = biasReport.text;

        // Log success message
        console.log("Bias report displayed successfully");
    } catch (error) {
        // Handle errors
        console.error("Error:", error);
        alert("An error occurred. Please try again.");
    }
});


// 