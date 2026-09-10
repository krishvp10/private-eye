/**
 * Ground-Truth Debug Overlay for Judges and Evaluators.
 * When URL contains ?debug=1, highlights all sensitive PII bounding boxes.
 */
document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (!urlParams.has("debug")) return;

  // Render debug banner
  const banner = document.createElement("div");
  banner.className = "debug-banner";
  banner.innerText = "DEBUG MODE: Ground-Truth PII Boxes Active";
  document.body.appendChild(banner);

  // Find all elements marked data-sensitive
  const sensitiveElements = document.querySelectorAll("[data-sensitive='true']");
  sensitiveElements.forEach((el) => {
    const rect = el.getBoundingClientRect();
    const category = el.getAttribute("data-category") || "sensitive";

    const box = document.createElement("div");
    box.className = "debug-box";
    box.style.left = `${rect.left + window.scrollX}px`;
    box.style.top = `${rect.top + window.scrollY}px`;
    box.style.width = `${rect.width}px`;
    box.style.height = `${rect.height}px`;
    box.innerText = category.toUpperCase();

    document.body.appendChild(box);
  });
});
