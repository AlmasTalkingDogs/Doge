var feedSocket = null;
var randomNumElem = null;

var label = 0;

function getWebSocketURI(socketName) {
    var loc = window.location, new_uri;
    if (loc.protocol === 'https:') {
        new_uri = 'wss:';
    }
    else {
        new_uri = 'ws:';
    }
    new_uri += '//' + loc.host;
    new_uri += socketName;
    return new_uri;
}

function updateNumber(number) {    
    randomNumElem.innerHTML = "<b>" + number + "</b>";
}

function handleMessage(event) {
    var clock = new Date();
    console.log("Recieved feed update from server at " + clock.getTime());
    var blob = JSON.parse(event.data);
    console.log(blob);
    updateNumber(blob['number']);
}

function sendMessage(value) {
    feedSocket.send(value);
}

function initFeed() {
    randomNumElem = document.getElementById('number');
    
    feedSocket = new WebSocket(getWebSocketURI("ws/feed"));
    feedSocket.onmessage = handleMessage;
}

function toggle() {
    if (label == 0) {
        label = 1
    } else if (label == 1) {
        label = 0
    }
    document.getElementById('label_switch').innerHTML = label;
    sendMessage(label);
}

var state = 0
function initIngestor() {
    if (state != 0) {
        return;
    }
    console.log("The state is good");
    ing_id = document.getElementById('ing_id');

    // Create ingestor
    state = 1;
    const Http = new XMLHttpRequest();
    const url='/rsrc/ing/' + ing_id.value;
    Http.open("POST", url);
    Http.send();

    Http.onreadystatechange = (e) => {
        console.log(Http.responseText);
        response = JSON.parse(Http.responseText)
        if (state != 1) {
            return
        }
        state = 2
        status_indicator = document.getElementById('status');
        status_indicator.innerHTML = "LOADING..."
        console.log("Checking")
        if (response["success"] === true) {
            console.log("Worked")
            status_indicator.innerHTML = "connected"
            feedSocket = new WebSocket(getWebSocketURI("/ws/ing/" + ing_id.value + "/0"));
            feedSocket.onmessage = handleMessage;
            feedSocket.onclose = function(event) {
                status_indicator.innerHTML = "No Connection"
                state = 0
                console.log("Closed again")
            }
        } else {
            console.log("Failed")
            status_indicator.innerHTML = "Failed"
            console.log(Http.responseText)
            state = 0
        }
    }
}
