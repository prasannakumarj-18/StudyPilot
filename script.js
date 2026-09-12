let currentPlanId = null;


async function generatePlan() {

    const subject = document.getElementById("subject").value;
    const days = document.getElementById("days").value;
    const hours = document.getElementById("hours_per_day").value;

    const response = await fetch("http://127.0.0.1:8001/studyplan", {
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
}


async function completeDay(planId, dayNumber) {

    const response = await fetch(
        "http://127.0.0.1:8001/progress/" +
        planId +
        "/" +
        dayNumber,
        {
            method: "PUT"
        }
    );

    const data = await response.json();

    if (!response.ok) {
        alert("Failed to update progress");
        return;
    }

    // Reload the complete progress from Oracle
    await loadProgress();
}
async function updateProgress(planId) {

    const response = await fetch(
        "http://127.0.0.1:8001/progress/" +
        planId
    );

    const data = await response.json();

    document.getElementById("progress").innerHTML =
        "Progress: " +
        data.progress_percentage +
        "%";

    document.getElementById("progressBar").value =
        data.progress_percentage;
}
async function loadProgress() {

    const planId = document.getElementById("plan_id").value;

    if (!planId) {
        alert("Please enter a Plan ID");
        return;
    }

    const response = await fetch(
        "http://127.0.0.1:8001/progress-details/" + planId
    );

    const data = await response.json();

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

        html += "<div>";

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

    document.getElementById("plan").innerHTML = html;
}
async function loadSavedPlan() {

    const planId = document.getElementById("plan_id").value;

    if (!planId) {
        alert("Please enter a Plan ID");
        return;
    }

    const response = await fetch(
        "http://127.0.0.1:8001/studyplan/" + planId
    );

    const data = await response.json();

    if (data.message) {
        alert(data.message);
        return;
    }

    const plan = JSON.parse(data.study_plan);

    let html = "<h2>Saved Study Plan - " +
               data.subject +
               "</h2>";
    
    html += "<p><b>Plan ID:</b> " +
            data.plan_id +
            "</p>";

    html += "<div id='progressBox'>";
    html += "<h3 id='progress'>Progress: 0%</h3>";
    html += "<progress id='progressBar' value='0' max='100'></progress>";
    html += "</div>";

    plan.days.forEach(function(day) {

        html += "<div>";

        html += "<h3>Day " +
                day.day +
                "</h3>";

        html += "<h4>" +
                day.topic +
                "</h4>";

        html += "<p><b>Study Time:</b> " +
                day.study_time +
                " hours</p>";

        html += "<p><b>Task:</b> " +
                day.task +
                "</p>";

        html += "</div>";
    });

    document.getElementById("plan").innerHTML = html;

    await updateProgress(planId);
}