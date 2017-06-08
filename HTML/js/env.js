document.addEventListener('DOMContentLoaded', defEnv);

function defEnv () {
    if (sessionStorage.length == 0) {
        window.location.href = "login.html";
    } else {
        var logout = document.getElementById("logout");
        logout.addEventListener('click', function(event) {
            sessionStorage.clear();        
        });
        var user = sessionStorage.getItem('user');
        if (user) {
            document.getElementById('username').innerHTML = user
        }
    }
}
