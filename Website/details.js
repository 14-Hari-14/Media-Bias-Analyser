document.addEventListener("DOMContentLoaded", () => {
    // Add an event listener to the form for the "submit" event
    document.getElementById("articleLinkForm").addEventListener("submit", async (event) => {
        event.preventDefault();

        // Get the input value (link entered by the user)
        const input = document.querySelector(".linkInput");
        const link = input.value;
        console.log("Link entered:", link);

        // Show loading state
        const resultContainer = document.getElementById("resultContainer");
        resultContainer.innerHTML = '<div class="loading">Analyzing article...</div>';

        try {
            // Send the link directly to your backend API instead of using chrome API
            const backendUrl = "http://127.0.0.1:8000/analyze-link";
            const response = await fetch(backendUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ url: link }),
            });

            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }

            const biasReport = await response.json();

            // Display the results on the page
            resultContainer.innerHTML = `
          <div class="result-card">
            <h3>Bias Analysis Results</h3>
            <p class="bias-result">${biasReport.text}</p>
            <div class="summary">${biasReport.summary}</div>
            <a href="details.html?content=${encodeURIComponent(JSON.stringify(biasReport))}" class="details-link">View Detailed Report</a>
          </div>
        `;

        } catch (error) {
            // Handle errors
            console.error("Error:", error);
            resultContainer.innerHTML = `<div class="error">An error occurred: ${error.message}</div>`;
        }
    });
});