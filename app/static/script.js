const form = document.getElementsByTagName("form");

form[0].addEventListener("submit", () => {
  document.getElementById("submit").style.display = "None";
  const loader = document.getElementsByClassName("loader")[0];

  if (loader) {
    loader.style.display = "block";
  }
});
