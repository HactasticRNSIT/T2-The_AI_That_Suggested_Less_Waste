document.addEventListener("DOMContentLoaded", () => {
  const button = document.getElementById("themeToggle");
  const savedTheme = localStorage.getItem("ecowise_theme");
  if (savedTheme === "dark") document.body.classList.add("dark-mode");

  if (button) {
    button.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
      localStorage.setItem("ecowise_theme", document.body.classList.contains("dark-mode") ? "dark" : "light");
    });
  }
});
