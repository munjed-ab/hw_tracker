// Set placeholders for SVU ID and password fields
var form_fields = document.getElementsByTagName("input");
form_fields[1].placeholder = "name_id";
form_fields[2].placeholder = "*******";

document.addEventListener("htmx:configRequest", (event) => {
  // Show the loading spinner when the form is submitted
  document.getElementById("loading-spinner").style.display = "block";
});

document.addEventListener("htmx:afterRequest", (event) => {
  // Hide the loading spinner once the response is received
  document.getElementById("loading-spinner").style.display = "none";
});

// Initialize modals and event listeners
document.addEventListener("DOMContentLoaded", () => {
  initializeModals();
});

function initializeModals() {
  // Remove existing modal data to prevent conflicts
  //    $('.modal').on('hidden.bs.modal', function () {
  //      $(this).removeData('bs.modal');
  //      $(this).find('.modal-content').html('');
  //    });

  // Ensure modals are properly shown when triggered by HTMX
  document.addEventListener("htmx:afterSwap", (event) => {
    const modalElement = event.detail.target.closest(".modal");
    if (modalElement) {
      $(modalElement).modal("show");
    }
  });
}

// Clean up after HTMX requests
document.addEventListener("htmx:afterSwap", (event) => {
  const modals = document.querySelectorAll(".modal");
  modals.forEach((modal) => {
    $(modal).modal("hide");
  });

  const backdrops = document.querySelectorAll(".modal-backdrop");
  backdrops.forEach((backdrop) => backdrop.remove());

  document.body.classList.remove("modal-open");
  document.body.style = "";
});

document.body.addEventListener("htmx:afterSwap", (event) => {
  if (
    event.detail.target.id === "course-modal" ||
    event.detail.target.id === "delete-course-modal"
  ) {
    const modal = new bootstrap.Modal(event.detail.target.closest(".modal"));
    modal.show();
  }
});

document.body.addEventListener("htmx:afterSwap", (event) => {
  if (event.detail.target.closest(".modal")) {
    const modal = new bootstrap.Modal(event.detail.target.closest(".modal"));
    modal.show();
  }
});
