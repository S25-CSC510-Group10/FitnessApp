const { load } = require("mime");
var timerInterval = null;
var timeLeft = 0;
var totalTime = 0;
console.log(timeLeft)

function addToLocalStorage(key,data){
    localStorage.setItem(key) = data;
}

function retrieveFromLocalStorage(key){
    return localStorage.getItem(key)
}

function logout(){
    $.ajax({
        type: "POST",
        url: "/logout",
        success: function(data) {
            console.log(data)
            window.location.href = "login";
        }
    });
}

function history(e){
    const form = new FormData(e.target);
    date = form.get("date")
    console.log(date)
    $.ajax({
        type: "POST",
        url: "/ajaxhistory",
        data:{
            "date":date
        },
        success: function(response){
            console.log(response)
            resdata = JSON.parse(response)
            
            $("#date_legend").empty().append("Date: ")
            $("#date").empty().append(resdata.date)

            $("#calories_legend").empty().append("Calories: ")
            $("#calories").empty().append(resdata.calories)

            $("#burnout_legend").empty().append("Burnout: ")
            $("#burnout").empty().append(resdata.burnout)

            $("#history-data").empty().append(JSON.stringify(response));
        }
    })
}

function sendRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxsendrequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function cancelRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxcancelrequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function approveRequest(e,clickedId){
    $.ajax({
        type: "POST",
        url: "/ajaxapproverequest",
        data:{
            "receiver":clickedId
        },
        success: function(response){
            location.reload()
            console.log(JSON.parse(response))
        }
    })
}

function dashboard(e, email){
    $.ajax({
        type: "POST",
        url: "/ajaxdashboard",
        data:{
            "email":email
        },
        success: function(response){
            console.log(response)
            resdata = JSON.parse(response)
            
            $("#enroll_legend").empty().append("ENrolled: ")
            $("#enroll").empty().append(resdata.enroll)
        }
    })
}


function openModal() {
    document.getElementById("timerModal").style.display = "block";
    resetTimer(); // Initialize the timer
}

function closeModal() {
    document.getElementById("timerModal").style.display = "none";
    pauseTimer();
}

function startTimer() {
    if (!timerInterval) {
        timerInterval = setInterval(() => {
            if (timeLeft > 0) {
                timeLeft--;
                updateClock();
                updateProgressBar();
            } else {
                clearInterval(timerInterval);
                timerInterval = null;
                alert("Time's up!");
            }
        }, 1000);
    }
}

function pauseTimer() {
    clearInterval(timerInterval);
    timerInterval = null;
}

function resetTimer() {
    pauseTimer();
    const timeInput = document.getElementById("timeInput").value;
    totalTime = timeLeft = timeInput * 60 || 0;
    updateClock();
    updateProgressBar();
}

function setTime() {
    const timeInput = document.getElementById("timeInput").value;
    totalTime = timeLeft = timeInput * 60 || 0;
    updateClock();
    updateProgressBar();
}

function updateClock() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    document.getElementById("clockDisplay").textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
}

function updateProgressBar() {
    const progress = document.querySelector(".progress");
    const percentage = ((totalTime - timeLeft) / totalTime) * 360; // Convert to degrees
    progress.style.background = `conic-gradient(#4caf50 ${percentage}deg, #ccc 0deg)`;
}
