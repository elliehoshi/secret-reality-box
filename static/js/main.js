const socket = new WebSocket('ws://localhost:21489/ws');

const root = document.getElementById('root');

socket.onopen = () => {
  console.log('[open] Connection established');
  console.log('Sending to server');
};

socket.onmessage = (event) => {
  root.innerText = event.data;
};

socket.onclose = function (event) {
  if (event.wasClean) {
    console.log(
      `[close] Connection closed cleanly, code=${event.code} reason=${event.reason}`
    );
  } else {
    console.log('[close] Connection died');
  }
};

socket.onerror = function (event) {
  console.error(`[error] ${event.toString()}`);
};


// sound the alarm!!!
// function soundTheAlarm() {
//   socket.send('cuckoo');
// }

// hide/display GUI states
// TODO: Refactor to DRY up the toggle logic
function toggleView(showStatus) {
  const scanSuccessWrapper = document.getElementById("scan-successful-wrapper");
  const defaultWrapper = document.getElementById("default-wrapper");
  const scanningWrapper = document.getElementById("scanning-wrapper");
  const scanFailedWrapper = document.getElementById("scan-failed-wrapper");
  const checkmark = document.getElementsByClassName("checkmark")[0];
  const uiError = document.getElementsByClassName("ui-error")[0];

  if ( !showStatus ) {
    scanSuccessWrapper.classList.remove("show");
    scanFailedWrapper.classList.remove("show");
    defaultWrapper.classList.add("show");
    checkmark.classList.add("hide");
    uiError.classList.remove("show");
    scanningWrapper.classList.remove("show");
  } else if ( showStatus == "success" ) {
    defaultWrapper.classList.remove("show");
    scanFailedWrapper.classList.remove("show");
    scanSuccessWrapper.classList.add("show");
    scanningWrapper.classList.remove("show");
    checkmark.classList.remove("hide");
    checkmark.classList.add("show");
    uiError.classList.remove("show");
  } else if ( showStatus == "scanning" ) {
    defaultWrapper.classList.remove("show");
    scanFailedWrapper.classList.remove("show");
    scanSuccessWrapper.classList.remove("show");
    scanningWrapper.classList.add("show");
  } else if ( showStatus == "fail" ) {
    defaultWrapper.classList.remove("show");
    scanSuccessWrapper.classList.remove("show");
    scanFailedWrapper.classList.add("show");
    checkmark.classList.add("hide");
    uiError.classList.add("show");
    scanningWrapper.classList.remove("show");
  } else {
    console.log('toggleView ', showStatus);
  }
}