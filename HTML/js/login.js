document.addEventListener('DOMContentLoaded', bindButton);

//function to attempt to login the user
//this auth process should be done on a server via real auth protocols
//input: user validated via filterUsername()
function attemptLogin(user) {   
    
    // if password == user.password 
    // these passwords should not be stored in plain text accessible via db query
    if (inputPassword.value == user[0].password) {
        // allow access
        console.log("success")
        // Save data to sessionStorage
        sessionStorage.setItem('user', user[0].username);
        window.location.href = "main.html";
    } else {
        // deny access
        console.log("Access denied")
        alert("Access Denied!")
        // uncomment for password hack
         console.log("please disable hack:"+user[0].password)
    }   
};

function bindButton() {
    var loginButton = document.getElementById("loginButton");
    loginButton.addEventListener('click', function (event) {

        //this will not work until API function is built out!
        // get user by username
        // password CANNOT be passed off in plain-text in final version
        // password CANNOT be retrievable/visible by querying the db
        
        console.log("In filter username");
        
        var inputUsername = document.getElementById("inputUsername");
        var inputPassword = document.getElementById("inputPassword");
            
        try {
            // init api call
            var req = new XMLHttpRequest();
            var url = "https://postskynetbountyboard.appspot.com/user/username";

            // Create json object to post
            var data = {
                username: null
            };

            // input form information
            if (inputUsername.value == "" || inputUsername.value == null)
                console.log("No username provided");

            else
                data.username = inputUsername.value;

            req.open("POST", url);
            req.setRequestHeader('Content-Type', 'application/json');
            req.addEventListener('load', function () {
                if (req.status >= 200 && req.status < 400) {
                    var response = JSON.parse(req.responseText);
                    // attempt login
                    attemptLogin(response);
                    
                } else {
                    console.log("Error from request: " + req.statusText);
                }
            });
            req.send(JSON.stringify(data));
        } catch (e) {
            alert(e);
        }
    })
};