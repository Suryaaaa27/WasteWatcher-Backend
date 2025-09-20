// scan.js — handles upload, camera, and backend call

let selectedImage = null;

// Upload button
document.getElementById("uploadBtn").addEventListener("click", () => {
  document.getElementById("wasteFile").click();
});

document.getElementById("wasteFile").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    selectedImage = file;
    document.getElementById("scanBtn").disabled = false;
  }
});

// Camera button
document.getElementById("cameraBtn").addEventListener("click", async () => {
  const video = document.getElementById("cameraStream");
  video.style.display = "block";

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    document.getElementById("scanBtn").disabled = false;

    // Capture snapshot when clicking Scan
    document.getElementById("scanBtn").onclick = () => {
      const canvas = document.getElementById("snapshotCanvas");
      const ctx = canvas.getContext("2d");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob((blob) => {
        selectedImage = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
        sendToBackend(selectedImage);
      }, "image/jpeg");
    };
  } catch (err) {
    alert("❌ Camera access denied or unavailable.");
  }
});

// Scan button (for uploaded file)
document.getElementById("scanBtn").addEventListener("click", () => {
  if (selectedImage) {
    sendToBackend(selectedImage);
  }
});

// Send to Flask backend
async function sendToBackend(file) {
  const resultBox = document.getElementById("resultBox");
  const resultText = document.getElementById("resultText");
  resultBox.style.display = "block";
  resultText.innerText = "⏳ Scanning waste...";

  const formData = new FormData();
  formData.append("image", file);

  try {
    const res = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData
    });

    if (!res.ok) throw new Error("Server error");
    const data = await res.json();

    resultText.innerText =
      `✅ Waste Type: ${data.waste_type}\n` +
      `📊 Confidence: ${(data.confidence * 100).toFixed(1)}%\n` +
      `☁️ Ozone Impact: ${data.odp_units} ODP units\n` +
      `🌍 Ozone Protection Score: ${data.ozone_protection_score}%\n` +
      `💡 Suggested Action: ${data.action}\n` +
      `💰 Value: ${data.value}`;

  } catch (err) {
    console.error("Prediction error:", err);
    resultText.innerText = "❌ Failed to connect to AI server.";
  }
}
