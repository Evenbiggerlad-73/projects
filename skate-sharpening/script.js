document.getElementById("year").textContent = new Date().getFullYear();

document.getElementById("contact-form").addEventListener("submit", (event) => {
  event.preventDefault();

  const note = document.getElementById("form-note");
  note.hidden = false;
  event.target.reset();
});
