// Wait until full page is loaded
window.addEventListener("load", () => {
  document.documentElement.classList.add("loaded");
});

// Wait for DOM content before accessing elements
document.addEventListener("DOMContentLoaded", () => {

  const emailinput = document.getElementById("usergmail");
  const passwordinput = document.getElementById("userpassword");

  // If elements don't exist, stop execution safely
  if (!emailinput || !passwordinput) return;

  // ---------------------------
  // Gmail Validation
  // ---------------------------
  emailinput.addEventListener("input", () => {
    const value = emailinput.value.trim();
    const emailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;

    if (emailRegex.test(value)) {
      emailinput.setCustomValidity("");
    } else {
      emailinput.setCustomValidity("Please enter a valid Gmail address (example@gmail.com)");
    }
  });

  // ---------------------------
  // Password Validation
  // ---------------------------
  passwordinput.addEventListener("input", () => {
    const value = passwordinput.value.trim();
    const passwordRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;

    if (passwordRegex.test(value)) {
      passwordinput.setCustomValidity("");
    } else {
      passwordinput.setCustomValidity(
        "Password must be at least 8 characters long and include uppercase, lowercase, number, and special character."
      );
    }
  });

});
