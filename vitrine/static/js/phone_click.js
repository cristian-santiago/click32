/**
 * Configura eventos de clique para links de telefone com rastreamento.
 */
document.addEventListener("DOMContentLoaded", () => {
  const phoneLinks = document.querySelectorAll(".phone-link");

  // Configura o evento de clique para cada link de telefone
  phoneLinks.forEach(link => {
    link.addEventListener("click", event => {
      event.preventDefault();

      const trackUrl = link.dataset.trackUrl;
      const phoneNumber = link.dataset.phone;

      if (!trackUrl || !phoneNumber) return;

      // Sends POST request to track the click
      fetch(trackUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": CSRF_TOKEN,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ type: "phone_link" })
      })
      .finally(() => {
        // Redirects to phone call without opening a new tab
        window.location.href = "tel:" + phoneNumber;
      });
    });
  });
});