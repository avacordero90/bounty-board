document.addEventListener('DOMContentLoaded', defEnv);

function defEnv () {
    var logout = document.getElementById("logout");
    logout.addEventListener('click', function(event) {
        sessionStorage.clear();        
    });
    
    var user = sessionStorage.getItem('user');
    if (user) {
        document.getElementById('username').innerHTML = user
    }
}
