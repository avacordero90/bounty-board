document.addEventListener('DOMContentLoaded', bindButton);

// Form elements
var postButton = document.getElementById("postButton");
var inputTitle = document.getElementById("inputTitle");
var inputCity = document.getElementById("inputCity");
var inputState = document.getElementById("inputState");
var inputAddress = document.getElementById("inputAddress");
var inputDescription = document.getElementById("inputDescription");
var inputEstimate = document.getElementById("inputEstimate");
var inputPay = document.getElementById("inputPay");
var inputPayType = document.getElementById("inputAddress");
var inputHourly = document.getElementById("inputHourly");
var inputDaily = document.getElementById("inputDaily");

// Dummy variables
var inputPosterName = "John Smith";
var reputationScore = 4.1;

function bindButton() {
    
    postButton.addEventListener('click', function(event) {

        //If required values are not provided, print error message
        if (inputPosterName == "" || inputPosterName == null || inputTitle.value == "" || inputTitle.value == null || reputationScore == null) {
            var message = document.getElementById("message");
            message.classname = "errorMessage";
            message.textContent = "Job Title is a required field.";
            return;
        }

        try {
            // Declare API request address
            var req = new XMLHttpRequest();
            var url = "https://postskynetbountyboard.appspot.com/job";

            // Create data object to send with POST
            var data = {poster_name:null, job_title:null, job_description:null, reputation_score:null, pay_rate:null,
                is_hourly: null, time_estimate: null, city: null, state: null, street_address: null
            };

            // Assign form information to data object
            if (inputPosterName != null)
                data.poster_name = inputPosterName;                              // Dummy variable
            if (inputTitle.value != "" || inputTitle.value != null)
                data.job_title = inputTitle.value;
            if (inputDescription.value != "" || inputDescription.value != null)
                data.job_description = inputDescription.value;
            if (reputationScore != null)
                data.reputation_score = reputationScore;                         // Dummy variable
            if (inputPay.value != "" || inputPay.value != null)
                data.pay_rate = parseFloat(inputPay.value);
            if (inputEstimate.value != "" || inputEstimate.value != null)
                data.time_estimate = inputEstimate.value;
            if (inputCity.value != "" || inputCity.value != null)
                data.city = inputCity.value;
            if (inputAddress.value != "" || inputAddress.value != null)
                data.street_address = inputAddress.value;

            // Set isHourly and state from options selected
            data.is_hourly = inputHourly.checked ? true : false;
            data.state = inputState.options[inputState.selectedIndex].value;

            req.open("POST", url, true);
            req.setRequestHeader('Content-Type', 'application/json');
            req.addEventListener('load', function () {
                if (req.status >= 200 && req.status < 400) {
                    var response = JSON.parse(req.responseText);
                    var length = response.length;
                    var message = document.getElementById("message");
                    message.classname = "errorMessage";
                    message.textContent = "Job posted successfully.";
                } else {
                    console.log("Error from request: " + req.statusText);
                }
            });
            req.send(JSON.stringify(data));
        } catch (e) {
            alert(e);
        }
    })
}