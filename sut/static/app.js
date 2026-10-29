"use strict";
// Progressive enhancement only. Server is authoritative for all business validation.
document.querySelectorAll("form").forEach((form) => {
  form.addEventListener("submit", () => {
    if (form.checkValidity()) form.setAttribute("aria-busy", "true");
  });
});
