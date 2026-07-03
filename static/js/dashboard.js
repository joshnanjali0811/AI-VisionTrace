let currentData = null;
let trendChart = null;
let distChart = null;

const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");

uploadArea.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", handleUpload);

function showPage(pageId, event) {
    // Scroll top ki vellakunda undataniki
    const scrollPos = window.scrollY;

    document.querySelectorAll(".page").forEach(page => page.classList.remove("active"));
    document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));

    document.getElementById(pageId).classList.add("active");
    if (event) event.target.classList.add("active");

    // Scroll position maintain cheyyadam
    setTimeout(() => window.scrollTo(0, scrollPos), 10);

    if (pageId === "trend") loadTrendChart();
    if (pageId === "distribution") loadDistributionChart();
    if (pageId === "history") loadHistory();
}

async function handleUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const loading = document.getElementById("loading");
    const result = document.getElementById("result");
    loading.style.display = "block";
    result.innerHTML = "";

    const formData = new FormData();
    formData.append("file", file);

    let endpoint = "";
    if (file.type.startsWith("image/")) endpoint = "/upload/image";
    else if (file.type === "video/mp4") endpoint = "/upload/video";
    else {
        loading.style.display = "none";
        alert("Please upload JPG, PNG or MP4 only.");
        return;
    }

    try {
        const response = await fetch(endpoint, {method: "POST", body: formData});
        const data = await response.json();
        loading.style.display = "none";

        if (data.success) {
            currentData = data;
            displayResult(data);
        } else {
            alert(data.error || "Processing failed.");
        }
    } catch (error) {
        loading.style.display = "none";
        console.error(error);
        alert("Unable to connect to server.");
    }
}

function displayResult(data) {
    const resultDiv = document.getElementById("result");

    if (data.image) {
        resultDiv.innerHTML = `<img src="data:image/jpeg;base64,${data.image}" class="result-media" alt="Detection Result">`;
        document.getElementById("avgConfidence").textContent = data.avg_confidence + "%";
    }

    if (data.video_url) {
        resultDiv.innerHTML = `<video controls class="result-media"><source src="${data.video_url}" type="video/mp4">Your browser does not support video.</video>`;
        document.getElementById("avgConfidence").textContent = data.avg_vehicles_per_frame + " avg/frm";
    }

    document.getElementById("totalVehicles").textContent = data.total_vehicles;
    document.getElementById("procTime").textContent = data.processing_time + " s";
    document.getElementById("trafficSoon").textContent = data.traffic_status || "Normal";

    currentData = data;
    loadTrendChart();
    loadDistributionChart();
}

async function loadTrendChart() {
    try {
        const response = await fetch("/api/history");
        const json = await response.json();

        if (!json.success || json.data.length === 0) {
            document.getElementById("trendChart").parentElement.innerHTML = `
                <p style="text-align:center;padding:60px;color:#aaa;font-size:16px;">
                    📊 No data yet<br>
                    <span style="font-size:14px;color:#64748b">Upload an image or video to see trend chart</span>
                </p>`;
            return;
        }

        const labels = json.data.map(item => item.Timestamp.split(" ")[1]);
        const values = json.data.map(item => item["Total Vehicles"]);
        const ctx = document.getElementById("trendChart").getContext("2d");

        if (trendChart) trendChart.destroy();

        trendChart = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Vehicle Count",
                    data: values,
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239,68,68,0.25)",
                    fill: true,
                    tension: 0.35,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {legend: {labels: {color: "#ffffff", font:{size:14}}}},
                scales: {
                    x: {ticks: {color: "#cbd5e1", maxTicksLimit: 8}},
                    y: {beginAtZero: true, ticks: {color: "#cbd5e1", stepSize: 5}}
                }
            }
        });
    } catch (error) {
        console.error("Trend Chart Error:", error);
    }
}

// DISTRIBUTION GRAPH FIXED
function loadDistributionChart() {
    const canvas = document.getElementById("distChart");
    if (!canvas) return;

    if (!currentData ||!currentData.vehicle_counts) {
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = "16px Poppins";
        ctx.fillStyle = "#cccccc";
        ctx.textAlign = "center";
        ctx.fillText("Upload an image or video first.", canvas.width / 2, canvas.height / 2);
        return;
    }

    const labels = Object.keys(currentData.vehicle_counts);
    const values = Object.values(currentData.vehicle_counts);
    const ctx = canvas.getContext("2d");

    if (distChart) distChart.destroy();

    distChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Vehicle Distribution",
                data: values,
                backgroundColor: ["#3b82f6","#10b981","#f59e0b","#ef4444","#8b5cf6"],
                borderRadius: 10,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {legend: {display: false}},
            scales: {
                x: {ticks: {color: "#cbd5e1"}},
                y: {beginAtZero: true, ticks: {color: "#cbd5e1", stepSize: 2}}
            }
        }
    });
}

async function loadHistory() {
    const historyDiv = document.getElementById("historyTable");
    try {
        const response = await fetch("/api/history");
        const json = await response.json();
        if (!json.success || json.data.length === 0) {
            historyDiv.innerHTML = `<p style="text-align:center;color:#aaa;padding:20px;">No history available.</p>`;
            return;
        }
        let html = `<table><thead><tr><th>Time</th><th>Type</th><th>Total Vehicles</th><th>Processing</th><th>Confidence</th></tr></thead><tbody>`;
        json.data.slice(-10).reverse().forEach(item => {
            html += `<tr><td>${item.Timestamp}</td><td>${item.Type}</td><td>${item["Total Vehicles"]}</td><td>${item["Processing Time"]} s</td><td>${item["Average Confidence"]}%</td></tr>`;
        });
        html += `</tbody></table>`;
        historyDiv.innerHTML = html;
    } catch (error) {
        console.error("History Error:", error);
        historyDiv.innerHTML = `<p style="text-align:center;color:red;padding:20px;">Failed to load history.</p>`;
    }
}

uploadArea.addEventListener("dragover", e => {
    e.preventDefault();
    uploadArea.style.borderColor = "#22c55e";
});
uploadArea.addEventListener("dragleave", () => uploadArea.style.borderColor = "#ef4444");
uploadArea.addEventListener("drop", e => {
    e.preventDefault();
    uploadArea.style.borderColor = "#ef4444";
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleUpload({target: {files: files}});
    }
});

document.addEventListener("keydown", e => {
    if (e.ctrlKey && e.key.toLowerCase() === "u") {
        e.preventDefault();
        fileInput.click();
    }
});

window.onload = function () {
    loadHistory();
    console.log("VisionTrace AI Dashboard Loaded Successfully.");
};