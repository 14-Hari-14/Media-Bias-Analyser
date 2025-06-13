document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('articleLinkForm');
    const resultContainer = document.getElementById('resultContainer');
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.innerHTML = '<div class="loader"></div>';

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = form.querySelector('.linkInput').value.trim();

        if (!url) {
            showError('Please enter a valid URL');
            return;
        }

        // Clear previous results and show loading
        resultContainer.innerHTML = '';
        resultContainer.appendChild(spinner);

        try {
            const response = await fetch('http://localhost:8000/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: url, url: true })
            });

            if (!response.ok) throw new Error(`Server error: ${response.status}`);

            const data = await response.json();
            console.log('API Response:', data.analysis); // Log response for debugging
            displayResults(data.analysis);

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'Failed to analyze article');
        } finally {
            spinner.remove();
        }
    });

    function displayResults(analysisText) {
        // Normalize text: trim and split by double newlines
        const cleanedText = analysisText.trim();
        const sectionsRaw = cleanedText.split('\n\n');

        // Initialize sections
        const sections = {
            summary: '',
            leaning: '',
            reasoning: ''
        };

        // Process each section
        sectionsRaw.forEach(section => {
            section = section.trim();
            if (!section) return;

            // Remove markdown bolding and check for headers
            const cleanSection = section.replace(/\*\*/g, '');
            if (cleanSection.startsWith('Summary:')) {
                sections.summary = cleanSection.replace(/^Summary:\s*/i, '').trim();
            } else if (cleanSection.match(/^(Political Leaning|Leaning|Bias):\s*/i)) {
                sections.leaning = cleanSection.replace(/^(Political Leaning|Leaning|Bias):\s*/i, '').trim();
            } else if (cleanSection.match(/^(Reasoning|Analysis|Explanation):\s*/i)) {
                sections.reasoning = cleanSection.replace(/^(Reasoning|Analysis|Explanation):\s*/i, '').trim();
            } else {
                // If no header, assume it's the summary (first section)
                if (!sections.summary) {
                    sections.summary = section.trim();
                }
            }
        });

        // Log extracted sections for debugging
        console.log('Extracted Sections:', sections);

        resultContainer.innerHTML = `
            <div class="result-card">
                <h3>Article Summary</h3>
                <p>${sections.summary || 'No summary available'}</p>
            </div>
            <div class="result-card">
                <h3>Political Leaning</h3>
                <p class="leaning ${sections.leaning ? sections.leaning.toLowerCase().split(' ')[0] : ''}">
                    ${sections.leaning || 'Could not determine'}
                </p>
            </div>
            <div class="result-card">
                <h3>Detailed Analysis</h3>
                <p>${sections.reasoning || 'No detailed analysis available'}</p>
            </div>
        `;
    }

    function showError(message) {
        resultContainer.innerHTML = `
            <div class="error-card">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
});