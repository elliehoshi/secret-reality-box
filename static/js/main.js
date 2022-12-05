// hide/display GUI states
// TODO: Refactor to DRY up the toggle logic
function toggleView(showStatus) {
  const scanSuccessWrapper = document.getElementById("scan-successful-wrapper");
  const defaultWrapper = document.getElementById("default-wrapper");
  const scanningWrapper = document.getElementById("scanning-wrapper");
  const checkmark = document.getElementsByClassName("checkmark")[0];

  if ( !showStatus ) {
    scanSuccessWrapper.classList.remove("show");
    defaultWrapper.classList.add("show");
    checkmark.classList.add("hide");
    scanningWrapper.classList.remove("show");
  } else if ( showStatus == "success" ) {
    defaultWrapper.classList.remove("show");
    scanSuccessWrapper.classList.add("show");
    scanningWrapper.classList.remove("show");
    checkmark.classList.remove("hide");
    checkmark.classList.add("show");
  } else if ( showStatus == "scanning" ) {
    defaultWrapper.classList.remove("show");
    scanSuccessWrapper.classList.remove("show");
    scanningWrapper.classList.add("show");
  } else {
    console.log('toggleView ', showStatus);
  }
}