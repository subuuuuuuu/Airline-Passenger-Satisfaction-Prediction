document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------
    // 1. Navigation & Tab Switching
    // -------------------------------------------------------------
    const navItems = document.querySelectorAll(".nav-item");
    const sections = document.querySelectorAll(".content-section");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const target = item.getAttribute("data-target");
            
            // Update active nav item
            navItems.forEach(nav => nav.classList.remove("active"));
            item.classList.add("active");
            
            // Show target section
            sections.forEach(sec => {
                if (sec.id === target) {
                    sec.classList.add("active");
                } else {
                    sec.classList.remove("active");
                }
            });

            // If switching to insights, load metrics
            if (target === "insights-view") {
                loadModelMetrics();
            }
        });
    });

    // -------------------------------------------------------------
    // 2. Rating Sliders Label Updates
    // -------------------------------------------------------------
    const sliders = [
        { id: "Inflight wifi service", valId: "val-wifi" },
        { id: "Seat comfort", valId: "val-seat" },
        { id: "Food and drink", valId: "val-food" },
        { id: "Online boarding", valId: "val-boarding" },
        { id: "Ease of Online booking", valId: "val-booking" },
        { id: "Gate location", valId: "val-gate" },
        { id: "Inflight entertainment", valId: "val-ent" },
        { id: "On-board service", valId: "val-onboard" },
        { id: "Leg room service", valId: "val-legroom" },
        { id: "Baggage handling", valId: "val-baggage" },
        { id: "Checkin service", valId: "val-checkin" },
        { id: "Inflight service", valId: "val-inflight" },
        { id: "Cleanliness", valId: "val-clean" },
        { id: "Departure/Arrival time convenient", valId: "val-convenient" }
    ];

    sliders.forEach(sliderInfo => {
        const slider = document.getElementById(sliderInfo.id);
        const label = document.getElementById(sliderInfo.valId);
        if (slider && label) {
            slider.addEventListener("input", (e) => {
                label.textContent = e.target.value;
            });
        }
    });

    // -------------------------------------------------------------
    // 3. Single Prediction Form Submission
    // -------------------------------------------------------------
    const form = document.getElementById("prediction-form");
    const resultPlaceholder = document.getElementById("result-placeholder");
    const resultDisplay = document.getElementById("result-display");
    const satBadge = document.getElementById("satisfaction-badge");
    const badgeIcon = document.getElementById("badge-icon");
    const badgeText = document.getElementById("badge-text");
    const gaugeFill = document.getElementById("gauge-fill");
    const gaugePercentage = document.getElementById("gauge-percentage");
    const satisfiedProbText = document.getElementById("satisfied-probability");
    const satisfiedStatusWord = document.getElementById("satisfied-status-word");
    const labelSatProb = document.getElementById("label-sat-prob");
    const labelUnsatProb = document.getElementById("label-unsat-prob");
    const fillSatProb = document.getElementById("fill-sat-prob");
    const fillUnsatProb = document.getElementById("fill-unsat-prob");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // Gather Form Data
        const formData = new FormData(form);
        const payload = {};
        
        formData.forEach((value, key) => {
            // Convert numbers and ratings to appropriate numeric types
            if (["Age", "Flight Distance", "Departure Delay in Minutes", "Arrival Delay in Minutes"].includes(key)) {
                payload[key] = Number(value);
            } else if (sliders.some(s => s.id === key)) {
                payload[key] = parseInt(value, 10);
            } else {
                payload[key] = value;
            }
        });

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const origBtnHtml = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Processing...';
        submitBtn.disabled = true;

        try {
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Server error");
            }
            
            const result = await response.json();
            displayPrediction(result);
            
        } catch (error) {
            alert("Error generating prediction: " + error.message);
            console.error(error);
        } finally {
            submitBtn.innerHTML = origBtnHtml;
            submitBtn.disabled = false;
        }
    });

    function displayPrediction(res) {
        // Toggle view panels
        resultPlaceholder.classList.add("hidden");
        resultDisplay.classList.remove("hidden");
        
        const isSatisfied = res.prediction === 1;
        const probability = res.probability_satisfied;
        
        // Update Gauge & Badge
        const percentText = (probability * 100).toFixed(1) + "%";
        gaugePercentage.textContent = percentText;
        satisfiedProbText.textContent = percentText;
        
        // Set gauge circle stroke offset (stroke-dasharray is 251.2, which represents 100%)
        const maxOffset = 251.2;
        const offset = maxOffset - (probability * maxOffset);
        gaugeFill.style.strokeDashoffset = offset;
        
        if (isSatisfied) {
            resultDisplay.className = "result-display satisfied";
            satBadge.className = "satisfaction-badge satisfied";
            badgeIcon.className = "fa-solid fa-face-smile";
            badgeText.textContent = "Satisfied";
            satisfiedStatusWord.textContent = "satisfied";
            satisfiedStatusWord.style.color = "var(--success)";
        } else {
            resultDisplay.className = "result-display dissatisfied";
            satBadge.className = "satisfaction-badge dissatisfied";
            badgeIcon.className = "fa-solid fa-face-frown";
            badgeText.textContent = "Neutral / Dissatisfied";
            satisfiedStatusWord.textContent = "neutral or dissatisfied";
            satisfiedStatusWord.style.color = "var(--danger)";
        }
        
        // Update breakdown bars
        const satPercentStr = (res.probability_satisfied * 100).toFixed(1) + "%";
        const unsatPercentStr = (res.probability_dissatisfied * 100).toFixed(1) + "%";
        
        labelSatProb.textContent = satPercentStr;
        fillSatProb.style.width = satPercentStr;
        
        labelUnsatProb.textContent = unsatPercentStr;
        fillUnsatProb.style.width = unsatPercentStr;
    }

    // -------------------------------------------------------------
    // 4. Bulk CSV Predictor
    // -------------------------------------------------------------
    const uploadZone = document.getElementById("upload-zone");
    const fileInput = document.getElementById("csv-file-input");
    const fileDetails = document.getElementById("file-details");
    const fileName = document.getElementById("file-name");
    const fileSize = document.getElementById("file-size");
    const btnRemoveFile = document.getElementById("btn-remove-file");
    const btnPredictBulk = document.getElementById("btn-predict-bulk");
    const bulkProgress = document.getElementById("bulk-progress");
    const bulkDownload = document.getElementById("bulk-download");
    const btnDownloadResults = document.getElementById("btn-download-results");
    const downloadTemplate = document.getElementById("download-template");

    let selectedFile = null;
    let predictedCsvBlobUrl = null;

    // Trigger file select dialog
    uploadZone.addEventListener("click", () => fileInput.click());

    // Drag over effects
    uploadZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = "var(--primary)";
        uploadZone.style.background = "rgba(92, 100, 242, 0.04)";
    });

    uploadZone.addEventListener("dragleave", () => {
        uploadZone.style.borderColor = "var(--border-color)";
        uploadZone.style.background = "rgba(255, 255, 255, 0.005)";
    });

    uploadZone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadZone.style.borderColor = "var(--border-color)";
        uploadZone.style.background = "rgba(255, 255, 255, 0.005)";
        
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    function handleFile(file) {
        if (!file.name.endsWith(".csv")) {
            alert("Please select a valid CSV file.");
            return;
        }
        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = (file.size / 1024).toFixed(1) + " KB";
        
        // Show file details panel
        fileDetails.classList.remove("hidden");
        btnPredictBulk.classList.remove("hidden");
        uploadZone.classList.add("hidden");
        
        // Reset progress/downloads if uploading a new file
        bulkProgress.classList.add("hidden");
        bulkDownload.classList.add("hidden");
    }

    btnRemoveFile.addEventListener("click", (e) => {
        e.stopPropagation(); // prevent triggering uploadZone click
        selectedFile = null;
        fileInput.value = "";
        
        fileDetails.classList.add("hidden");
        btnPredictBulk.classList.add("hidden");
        uploadZone.classList.remove("hidden");
        bulkProgress.classList.add("hidden");
        bulkDownload.classList.add("hidden");
        
        if (predictedCsvBlobUrl) {
            URL.revokeObjectURL(predictedCsvBlobUrl);
            predictedCsvBlobUrl = null;
        }
    });

    btnPredictBulk.addEventListener("click", async () => {
        if (!selectedFile) return;
        
        // Show loading spinner
        btnPredictBulk.classList.add("hidden");
        fileDetails.classList.add("hidden");
        bulkProgress.classList.remove("hidden");
        
        const formData = new FormData();
        formData.append("file", selectedFile);
        
        try {
            const response = await fetch("/api/predict_bulk", {
                method: "POST",
                body: formData
            });
            
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || "Failed to process bulk predictions");
            }
            
            const blob = await response.blob();
            predictedCsvBlobUrl = URL.createObjectURL(blob);
            
            // Set up download button
            btnDownloadResults.href = predictedCsvBlobUrl;
            btnDownloadResults.download = "predicted_" + selectedFile.name;
            
            // Update UI
            bulkProgress.classList.add("hidden");
            bulkDownload.classList.remove("hidden");
            
        } catch (error) {
            alert("Bulk prediction error: " + error.message);
            console.error(error);
            // Re-show prediction button
            bulkProgress.classList.add("hidden");
            fileDetails.classList.remove("hidden");
            btnPredictBulk.classList.remove("hidden");
        }
    });

    // Generate Client-Side CSV Template
    downloadTemplate.addEventListener("click", (e) => {
        e.preventDefault();
        const headers = [
            "Gender", "Customer Type", "Age", "Type of Travel", "Class", "Flight Distance",
            "Inflight wifi service", "Departure/Arrival time convenient", "Ease of Online booking",
            "Gate location", "Food and drink", "Online boarding", "Seat comfort",
            "Inflight entertainment", "On-board service", "Leg room service", "Baggage handling",
            "Checkin service", "Inflight service", "Cleanliness", "Departure Delay in Minutes",
            "Arrival Delay in Minutes"
        ].join(",");
        
        const row1 = [
            "Female", "Loyal Customer", "41", "Business travel", "Business", "850",
            "4", "3", "4", "4", "5", "5", "5", "4", "4", "4", "4", "5", "5", "4", "15", "5"
        ].join(",");
        
        const row2 = [
            "Male", "disloyal Customer", "20", "Personal Travel", "Eco", "190",
            "2", "4", "2", "3", "2", "2", "2", "2", "3", "2", "3", "3", "4", "2", "0", "0"
        ].join(",");
        
        const csvContent = headers + "\n" + row1 + "\n" + row2;
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement("a");
        a.href = url;
        a.download = "aeropredict_passenger_sample_template.csv";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // -------------------------------------------------------------
    // 5. Load Model Insights & Performance Metrics
    // -------------------------------------------------------------
    let metricsLoaded = false;
    
    async function loadModelMetrics() {
        if (metricsLoaded) return; // Load only once
        
        try {
            const response = await fetch("/api/metrics");
            if (!response.ok) {
                throw new Error("Unable to fetch metrics");
            }
            
            const metrics = await response.json();
            
            // Map values to DOM card components
            document.getElementById("metric-accuracy").textContent = (metrics.accuracy * 100).toFixed(1) + "%";
            document.getElementById("metric-f1").textContent = (metrics.f1_score * 100).toFixed(1) + "%";
            document.getElementById("metric-precision").textContent = (metrics.precision * 100).toFixed(1) + "%";
            document.getElementById("metric-recall").textContent = (metrics.recall * 100).toFixed(1) + "%";
            
            // Cache loaded status
            metricsLoaded = true;
            
        } catch (error) {
            console.error("Error loading metrics:", error);
            // Keep values as '--' or set an error state
        }
    }
});
