// Native forms remain authoritative. No browser persistence or private caching.
for (const form of document.querySelectorAll("form")) {
  form.addEventListener("submit", () => form.setAttribute("aria-busy", "true"));
}
