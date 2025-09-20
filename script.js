let selectedImage = null;
let videoStream = null;
const API_URL = "http://127.0.0.1:5000/predict"; 

// ✅ DEMO Mode toggle (true = Kalinga Campus, false = Global)
let DEMO_MODE = true;

// ----------------- Camera Handling -----------------
function openCamera() {
    const video = document.getElementById("cameraFeed");
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
          videoStream = stream;
          video.srcObject = stream;
          video.play();
      })
      .catch(err => {
          alert("⚠️ Cannot access camera: " + err.message);
      });
}

document.getElementById("captureBtn").addEventListener("click", () => {
    const video = document.getElementById("cameraFeed");
    if (!videoStream) {
        alert("⚠️ Camera is not open");
        return;
    }
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    selectedImage = canvas.toDataURL("image/jpeg");

    document.getElementById("previewImg").src = selectedImage;
    document.getElementById("previewImg").style.display = "block";
    document.getElementById("analyzeBtn").style.display = "inline-block";
});

// ----------------- File Upload -----------------
document.getElementById("fileInput").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(ev) {
            selectedImage = ev.target.result;
            document.getElementById("previewImg").src = selectedImage;
            document.getElementById("previewImg").style.display = "block";
            document.getElementById("analyzeBtn").style.display = "inline-block";
        };
        reader.readAsDataURL(file);
    }
});

// ----------------- Analyze Waste -----------------
function analyzeWaste() {
    if (!selectedImage) {
        alert("Upload or capture a photo first!");
        return;
    }

    fetch(selectedImage)
      .then(res => res.blob())
      .then(blob => {
          const formData = new FormData();
          formData.append("image", blob, "waste.jpg");

          return fetch(API_URL, { method: "POST", body: formData });
      })
      .then(res => res.json())
      .then(data => {
          document.getElementById("resultSection").innerHTML = `
            <div class="result-card">
              <h3>🎉 Waste Analysis Complete</h3>
              <p><strong>✅ Waste Type:</strong> ${data.waste_type}</p>
              <p><strong>📊 Confidence:</strong> ${(data.confidence * 100).toFixed(2)}%</p>
              <p><strong>☁️ Ozone Impact:</strong> ${data.odp_units} ODP units</p>
              <p><strong>🌍 Ozone Protection Score:</strong> ${data.ozone_protection_score}%</p>
              <p><strong>💡 Suggested Action:</strong> ${data.action}</p>
              <p><strong>💰 Value:</strong> ${data.value || "N/A"}</p>
            </div>
          `;

          // ✅ Show waste sites
          showNearbyWasteSites(data.waste_type);

          // ✅ Load charts
          loadStatsGraph();
      })
      .catch(err => {
          console.error(err);
          alert("❌ Error analyzing waste. Backend might not be running.");
      });
}

// ----------------- Helper: Haversine Distance -----------------
function haversine(lat1, lon1, lat2, lon2) {
    function toRad(x) { return x * Math.PI / 180; }
    let R = 6371e3; // meters
    let φ1 = toRad(lat1);
    let φ2 = toRad(lat2);
    let Δφ = toRad(lat2 - lat1);
    let Δλ = toRad(lon2 - lon1);

    let a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
    let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // in meters
}

// ----------------- Map & Disposal Check -----------------
function showNearbyWasteSites(predictedWaste) {
    const locSection = document.getElementById("location-section");
    locSection.style.display = "block";

    let mapCenter = DEMO_MODE ? [21.1642, 81.7756] : [20.5937, 78.9629];
    let zoomLevel = DEMO_MODE ? 17 : 5;
    const map = L.map("map").setView(mapCenter, zoomLevel);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    setTimeout(() => map.invalidateSize(), 100);

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(pos => {
            const lat = pos.coords.latitude;
            const lng = pos.coords.longitude;
            map.setView([lat, lng], DEMO_MODE ? 17 : 13);

            L.marker([lat, lng]).addTo(map)
              .bindPopup("📍 You are here")
              .openPopup();

            let bins = [];
            if (DEMO_MODE) {
                // ✅ Fixed bins in Kalinga University Campus
                bins = [
                    { name: "Organic Bin (Hostel Mess)", type: "Organic", lat: 21.1645, lng: 81.7757 },
                    { name: "Plastic Bin (Canteen)", type: "Plastic", lat: 21.1640, lng: 81.7758 },
                    { name: "Glass Bin (Library Gate)", type: "Glass", lat: 21.1643, lng: 81.7753 },
                    { name: "Metal Bin (Admin Block)", type: "Metal", lat: 21.1639, lng: 81.7754 },
                    { name: "E-Waste Bin (Computer Lab)", type: "E-Waste", lat: 21.1646, lng: 81.7752 },
                    { name: "Battery Bin (Parking)", type: "Battery", lat: 21.1641, lng: 81.7760 }
                ];
            } else {
                // 🌍 Global Mode: dynamic bins near user location
                bins = [
                    { name: "Organic Bin", type: "Organic", lat: lat+0.002, lng: lng+0.002 },
                    { name: "Plastic Bin", type: "Plastic", lat: lat-0.002, lng: lng-0.002 },
                    { name: "E-Waste Bin", type: "E-Waste", lat: lat+0.001, lng: lng-0.001 }
                ];
            }

            const list = document.getElementById("location-list");
            list.innerHTML = "";

            bins.forEach(bin => {
                L.marker([bin.lat, bin.lng])
                 .addTo(map)
                 .bindPopup(`🗑️ ${bin.name} (${bin.type})`);
                
                const li = document.createElement("li");
                li.textContent = `🗑️ ${bin.name} (${bin.type})`;
                list.appendChild(li);
            });

            // ✅ Suggest correct bin
            const correctBin = bins.find(b => b.type === predictedWaste);
            if (correctBin) {
                L.popup()
                  .setLatLng([lat, lng])
                  .setContent(`✅ Detected ${predictedWaste}. Please dispose at <b>${correctBin.name}</b>.`)
                  .openOn(map);
            }

            // ✅ Wrong disposal check
            bins.forEach(bin => {
                let d = haversine(lat, lng, bin.lat, bin.lng);
                if (d < 30 && predictedWaste !== bin.type) {
                    L.popup()
                      .setLatLng([lat, lng])
                      .setContent(`⚠️ Wrong Disposal! Detected ${predictedWaste}, but you are near <b>${bin.name}</b>.`)
                      .openOn(map);
                }
            });

            loadHeatmap(map);
            setTimeout(() => map.invalidateSize(), 100);
        });
    }
}

// ----------------- Graphs -----------------
function loadStatsGraph() {
    fetch("http://127.0.0.1:5000/stats")
      .then(res => res.json())
      .then(data => {
          const ctx = document.getElementById("wasteChart").getContext("2d");
          new Chart(ctx, {
              type: "pie",
              data: {
                  labels: Object.keys(data),
                  datasets: [{
                      data: Object.values(data),
                      backgroundColor: ["#ff6384","#36a2eb","#ffce56","#4caf50","#9966ff","#ff9f40"]
                  }]
              }
          });
      });
}

// ----------------- Heatmap -----------------
function loadHeatmap(map) {
    fetch("http://127.0.0.1:5000/heatmap")
      .then(res => res.json())
      .then(points => {
          const heat = L.heatLayer(points.map(p => [p[0], p[1], 0.5]), { radius: 25 });
          heat.addTo(map);
      });
}

// ----------------- Toggle Mode Button -----------------
document.getElementById("toggleModeBtn").addEventListener("click", () => {
    DEMO_MODE = !DEMO_MODE;
    document.getElementById("toggleModeBtn").textContent = DEMO_MODE 
        ? "🌍 Switch to Global Mode" 
        : "🏫 Switch to Campus Mode";
    
    alert(`Mode switched to ${DEMO_MODE ? "Campus (Kalinga University)" : "Global"} 🌍`);
});
