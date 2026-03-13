const form = document.getElementById("prediction-form");
const healthButton = document.getElementById("health-check");
const healthOutput = document.getElementById("health-output");
const resultPanel = document.getElementById("result-panel");
const resultTitle = document.getElementById("result-title");
const resultMessage = document.getElementById("result-message");
const resultJson = document.getElementById("result-json");

async function readResponse(response) {
  try {
    return await response.json();
  } catch {
    return { detail: "Invalid JSON response from API." };
  }
}

async function runHealthCheck() {
  healthOutput.textContent = "Checking backend health...";

  try {
    const response = await fetch("/api/health");
    const payload = await readResponse(response);
    healthOutput.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    healthOutput.textContent = `Health check failed: ${error.message}`;
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  resultPanel.className = "result-panel";
  resultPanel.classList.remove("hidden");
  resultTitle.textContent = "Loading prediction...";
  resultMessage.textContent = "The backend is processing your weather input.";
  resultJson.textContent = "";

  try {
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const body = await readResponse(response);

    if (!response.ok) {
      resultPanel.classList.add("error");
      resultTitle.textContent = `Request failed (${response.status})`;
      resultMessage.textContent = body.detail || "Prediction request failed.";
      resultJson.textContent = JSON.stringify(body, null, 2);
      return;
    }

    resultPanel.classList.add(body.prediction === "Yes" ? "success" : "error");
    resultTitle.textContent = `Prediction: ${body.prediction}`;
    resultMessage.textContent = body.message;
    resultJson.textContent = JSON.stringify(body, null, 2);
  } catch (error) {
    resultPanel.classList.add("error");
    resultTitle.textContent = "Network error";
    resultMessage.textContent = error.message;
    resultJson.textContent = "";
  }
});

healthButton.addEventListener("click", runHealthCheck);