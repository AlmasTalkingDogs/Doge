var feedSocket = null;
var randomNumElem = null;

function getWebSocketURI(socketName) {
    var loc = window.location, new_uri;
    if (loc.protocol === 'https:') {
        new_uri = 'wss:';
    }
    else {
        new_uri = 'ws:';
    }
    new_uri += '//' + loc.host;
    new_uri += loc.pathname + socketName;
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

function initFeed() {
    randomNumElem = document.getElementById('number');
    
    feedSocket = new WebSocket(getWebSocketURI("ws/feed"));
    feedSocket.onmessage = handleMessage;
}