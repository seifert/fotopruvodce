var Fp = function(setPreferenceUrl) {

    this.setPreferenceUrl = setPreferenceUrl;

    this.setPreference = function(name, value) {
        var xhttp = new XMLHttpRequest();
        xhttp.open("POST", this.setPreferenceUrl, true);
        xhttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
        xhttp.setRequestHeader('X-CSRFToken', this.csrfCookie());
        xhttp.send("name=" + name + "&value=" + JSON.stringify(value));
    }

    this.csrfCookie = function() {
        var cookieValue = null,
        name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

}
