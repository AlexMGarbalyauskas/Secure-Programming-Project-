// insecure script file

// example of dangerous client-side rendering
function displayRawContent(html) {
    const container = document.getElementById("xss-output");
    if (container) {
        container.innerHTML = html; // XSS vulnerability
    }
}

// example auto-executed insecure script
console.log("Insecure script.js loaded — DOM not sanitized.");
