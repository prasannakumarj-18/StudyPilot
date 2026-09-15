let currentPlanId = null;

const API_URL = "https://studypilot-app.onrender.com";

// ==============================
// Generate Study Plan
// ==============================
async function generatePlan() {

    const subject = document.getElementById("subject").value;
    const days = document.getElementById("days").value;
    const hours = document.getElementById("hours_per_day").value;

    if (!subject || !days || !hours) {
        alert("Please fill all fields");
        return;
    }

    try {

        const response = await fetch(API_URL + "/studyplan", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                subject: subject,
                days: Number(days),
                hours_per_day: Number(hours)
            })
        });

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Failed to generate study plan");
            return;
        }

        currentPlanId = data.plan_id;

        const plan = JSON.parse(data.study_plan);

        let html = "<h2>Study Plan - " + subject + "</h2>";

        html += "<p><b>Plan ID:</b> " + data.plan_id + "</p>";

        html += "<div id='progressBox'>";
        html += "<h3 id='progress'>Progress: 0%</h3>";
        html += "<progress id='progressBar' value='0' max='100'></progress>";
        html += "</div>";

        plan.days.forEach(function(day) {

            html += "<div id='day-" + day.day + "'>";

            html += "<h3>Day " + day.day + "</h3>";

            html += "<h4>" + day.topic + "</h4>";

            html += "<p><b>Study Time:</b> " +
                    day.study_time +
                    " hours</p>";

            html += "<p><b>Task:</b> " +
                    day.task +
                    "</p>";

            html += "<button id='button-" + day.day +
                    "' onclick=\"completeDay(" +
                    data.plan_id +
                    "," +
                    day.day +
                    ")\">✓ Complete Day</button>";

            html += "<hr>";

            html += "</div>";
        });

        document.getElementById("plan").innerHTML = html;

        await updateProgress(data.plan_id);

    } catch (error) {

        console.error(error);
        alert("Cannot connect to StudyPilot server.");

    }
}


// ==============================
// Complete Day
// ==============================
async function completeDay(planId, dayNumber) {

    try {

        const response = await fetch(
            API_URL +
            "/progress/" +
            planId +
            "/" +
            dayNumber,
            {
                method: "PUT"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Failed to update progress");
            return;
        }

        await loadProgressForPlan(planId);

    } catch (error) {

        console.error(error);
        alert("Cannot connect to StudyPilot server.");

    }
}


// ==============================
// Update Progress
// ==============================
async function updateProgress(planId) {

    try {

        const response = await fetch(
            API_URL + "/progress/" + planId
        );

        const data = await response.json();

        if (!response.ok) {
            return;
        }

        const progressElement =
            document.getElementById("progress");

        const progressBar =
            document.getElementById("progressBar");

        if (progressElement) {

            progressElement.innerHTML =
                "Progress: " +
                data.progress_percentage +
                "%";
        }

        if (progressBar) {

            progressBar.value =
                data.progress_percentage;
        }

    } catch (error) {

        console.error(error);

    }
}


// ==============================
// Load Progress
// ==============================
async function loadProgress() {

    const planId =
        document.getElementById("plan_id").value;

    if (!planId) {

        alert("Please enter a Plan ID");
        return;
    }

    await loadProgressForPlan(planId);
}


// ==============================
// Load Progress Details
// ==============================
async function loadProgressForPlan(planId) {

    try {

        const response = await fetch(
            API_URL +
            "/progress-details/" +
            planId
        );

        const data = await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Failed to load progress"
            );

            return;
        }

        if (data.message) {

            alert(data.message);
            return;
        }

        let html = "<h2>Study Progress</h2>";

        html += "<div id='progressBox'>";

        html += "<h3>Progress: " +
                data.progress_percentage +
                "%</h3>";

        html += "<progress value='" +
                data.progress_percentage +
                "' max='100'></progress>";

        html += "<p>Completed Days: " +
                data.completed_days +
                " / " +
                data.total_days +
                "</p>";

        html += "</div>";

        data.days.forEach(function(day) {

            html += "<div id='progress-day-" +
                    day.day_number +
                    "'>";

            html += "<h3>Day " +
                    day.day_number +
                    "</h3>";

            if (day.status === "COMPLETED") {

                html += "<p><b>✓ Completed</b></p>";

            } else {

                html += "<p><b>Status:</b> Pending</p>";

                html += "<button onclick=\"completeDay(" +
                        planId +
                        "," +
                        day.day_number +
                        ")\">";

                html += "Mark Completed";

                html += "</button>";
            }

            html += "<hr>";

            html += "</div>";
        });

        document.getElementById("plan").innerHTML =
            html;

    } catch (error) {

        console.error(error);

        alert("Cannot connect to StudyPilot server.");

    }
}


// ==============================
// Load Saved Study Plan
// ==============================
async function loadSavedPlan() {

    const planId =
        document.getElementById("plan_id").value;

    if (!planId) {

        alert("Please enter a Plan ID");
        return;
    }

    try {

        const response = await fetch(
            API_URL +
            "/studyplan/" +
            planId
        );

        const data = await response.json();

        if (!response.ok) {

            alert(
                data.detail ||
                "Failed to load study plan"
            );

            return;
        }

        if (data.message) {

            alert(data.message);
            return;
        }

        currentPlanId = data.plan_id;

        const plan = JSON.parse(data.study_plan);

        let html =
            "<h2>Saved Study Plan - " +
            data.subject +
            "</h2>";

        html +=
            "<p><b>Plan ID:</b> " +
            data.plan_id +
            "</p>";

        html += "<div id='progressBox'>";

        html +=
            "<h3 id='progress'>Progress: 0%</h3>";

        html +=
            "<progress id='progressBar' value='0' max='100'></progress>";

        html += "</div>";

        plan.days.forEach(function(day) {

            html +=
                "<div id='day-" +
                day.day +
                "'>";

            html +=
                "<h3>Day " +
                day.day +
                "</h3>";

            html +=
                "<h4>" +
                day.topic +
                "</h4>";

            html +=
                "<p><b>Study Time:</b> " +
                day.study_time +
                " hours</p>";

            html +=
                "<p><b>Task:</b> " +
                day.task +
                "</p>";

            html +=
                "<button onclick=\"completeDay(" +
                data.plan_id +
                "," +
                day.day +
                ")\">";

            html += "✓ Complete Day";

            html += "</button>";

            html += "<hr>";

            html += "</div>";
        });

        document.getElementById("plan").innerHTML =
            html;

        await updateProgress(data.plan_id);

    } catch (error) {

        console.error(error);

        alert("Cannot connect to StudyPilot server.");

    }
}