document.addEventListener('DOMContentLoaded', bindButton);

// Form elements
var checkUsers = document.getElementById("checkusers");
var registerButton = document.getElementById("registerButton");
var inputName = document.getElementById("inputName");
var inputEmail = document.getElementById("inputEmail");
var inputCity = document.getElementById("inputCity");
var inputState = document.getElementById("inputState");
var inputAddress = document.getElementById("inputAddress");
var inputZip = document.getElementById("inputZip");
var inputUsername = document.getElementById("inputUsername");
var inputPassword = document.getElementById("inputPassword");
var inputConfirm = document.getElementById("inputConfirm");

function bindButton() {

    registerButton.addEventListener('click', function (event) {

        //If required values are not provided, print error message
        if (inputName == "" || inputName == null || inputUsername.value == "" || inputUsername.value == null || inputPassword.value == "" || 
            inputPassword.value == null || inputConfirm.value == "" || inputConfirm.value == null || inputEmail.value == "" || inputEmail.value == null) {
            var message = document.getElementById("message");
            message.classname = "errorMessage";
            message.textContent = "Name, Username, Password, and E-mail are all required fields.";
            return;
        }

        if (inputPassword.value != inputConfirm.value) {
            var message = document.getElementById("message");
            message.classname = "errorMessage";
            message.textContent = "Passwords do not match.";
            return;
        }

        try {
            // Declare API request address
            var req = new XMLHttpRequest();
            var url = "https://postskynetbountyboard.appspot.com/user";

            // Create data object to send with POST
            var data = {
                real_name: null, username: null, password: null, email: null, city: null,
                state: null, street_address: null, zip: null
            };

            // Assign form information to data object
            data.real_name = inputName.value;
            data.username = inputUsername.value;
            data.password = inputPassword.value;
            data.email = inputEmail.value;

            if (inputCity.value != "" || inputCity.value != null)
                data.city = inputCity.value;
            if (inputAddress.value != "" || inputAddress.value != null)
                data.street_address = inputAddress.value;
            if (inputZip.value != "" || inputZip.value != null)
                data.zip = inputZip.value;

            data.state = inputState.options[inputState.selectedIndex].value;

            req.open("POST", url, true);
            req.setRequestHeader('Content-Type', 'application/json');
            req.addEventListener('load', function () {
                if (req.status >= 200 && req.status < 400) {
                    var response = JSON.parse(req.responseText);
                    var length = response.length;
                    var message = document.getElementById("message");
                    message.classname = "errorMessage";
                    message.textContent = "User registered successfully.";
                } else {
                    console.log("Error from request: " + req.statusText);
                }
            });
            req.send(JSON.stringify(data));
        } catch (e) {
            alert(e);
        }
    })

    checkUsers.addEventListener('click', function (event) {

        var req = new XMLHttpRequest();
        var url = "https://postskynetbountyboard.appspot.com/user";

        req.open("GET", url, true);
        req.addEventListener('load', function () {
            if (req.status >= 200 && req.status < 400) {
                var response = JSON.parse(req.responseText);
                var length = response.length;
                console.log(response);

            } else {
                console.log("Error from request: " + req.statusText);
            }
        });

        req.send(null);
    })
}