function collapse() {
    activitySubmit.classList.toggle("collapse");
}

let activitySubmit = document.getElementsByClassName('activity-submit')[0];

window.addEventListener("load", function () {
    // svg scripts

    let tri = document.getElementsByClassName('tri');

    var mind = "{{ all_daily.daily_mind.0 }}";
    var body = "{{ all_daily.daily_body.0 }}";
    var soul = "{{ all_daily.daily_soul.0 }}";

    let activities = [mind, body, soul];

    for (var i = 0; i < 3; i++)
    {
        if (activities[i])
        {
            tri[i].classList.add("completed_act");
        }
    }

    // activity-form scripts/logic
    let activityLabel = document.getElementsByClassName("activity-label");
    var activityInput = document.getElementById("id_description");
    let activityTypes = ["Mind", "Body", "Soul"];

    function revertColor() {
        for (let i = 0; i < 3; i++) {
            activityLabel[i].style.background = "#eee";
        }
    }

    for (let i = 0; i < 3; i++) {

        activityLabel[i].addEventListener("click", function () {

            let labelSelected = false;

            for (let j = 0; j < 3; j++) {
                if (activityLabel[j].style.background == "gray") {
                    labelSelected = true;
                    revertColor();
                    break;
                }
            }
            if (labelSelected != true) {
                activityLabel[i].style.background = "gray";
                activityInput.placeholder = `Describe Your ${activityTypes[i]} Activity..`;
            }
        }, false);
    }


    // daily activity fade in
    var daily_acts = document.getElementsByClassName("activity-card-content");

    for (let i = 0; i < daily_acts.length; i++) {
        if (daily_acts[i].innerHTML) {
            daily_acts[i].classList.toggle("text-fade");
        }
    }
});

// testing manage-form functionality
function toggleFormDisplay(clickedBtn) {
    var formToDisplay = clickedBtn.getAttribute("data-form");
    var form = document.getElementsByClassName(formToDisplay)[0];

    form.classList.toggle("show-form");
}
