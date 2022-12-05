// hide/display GUI states
// TODO: Refactor to DRY up the toggle logic
function toggleView(showStatus) {
  const scanSuccessWrapper = document.getElementById("scan-successful-wrapper");
  const defaultWrapper = document.getElementById("default-wrapper");
  const scanningWrapper = document.getElementById("scanning-wrapper");
  const communityWrapper = document.getElementById("community-wrapper");
  const checkmark = document.getElementsByClassName("checkmark")[0];

  if ( !showStatus ) {
    // Default screen
    scanSuccessWrapper.classList.remove("show");
    defaultWrapper.classList.add("show");
    checkmark.classList.add("hide");
    scanningWrapper.classList.remove("show");
  } else if ( showStatus == "scanning" ) {
    // Show "scanning..." animation
    defaultWrapper.classList.remove("show");
    scanningWrapper.classList.add("show");
    // After 5 seconds, show Success screen
    setTimeout(() => {
      scanSuccessWrapper.classList.add("show");
      scanningWrapper.classList.remove("show");
      checkmark.classList.remove("hide");
      checkmark.classList.add("show");
    }, 5000)
    // Then, after 4 more seconds, show "Join the Community" screen
    setTimeout(() => {
      scanSuccessWrapper.classList.remove("show");
      checkmark.classList.add("hide");
      communityWrapper.classList.add("show");
    }, 9000)
    // Wait a few more seconds, then return to the Default screen
    setTimeout(() => {
      communityWrapper.classList.remove("show");
      defaultWrapper.classList.add("show");
    }, 25000)
  } else {
    console.log('toggleView ', showStatus);
  }
}