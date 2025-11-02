// missile_money/static/js/finance_bot.js
(function () {
    const panel = document.getElementById("finance-bot-panel");
    const toggle = document.getElementById("finance-bot-toggle");
    const closeBtn = document.getElementById("finance-bot-close");
    const form = document.getElementById("finance-bot-form");
    const input = form?.querySelector("input");
    const messagesEl = document.getElementById("finance-bot-messages");
    const resetBtn = document.getElementById("finance-bot-reset");
  
    if (!panel || !toggle || !form || !messagesEl) return;

    const isPanelOpen = () => panel.classList.contains("is-open");
    const setPanelState = (isOpen) => {
      panel.classList.toggle("is-open", isOpen);
      panel.setAttribute("aria-hidden", isOpen ? "false" : "true");
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
      if (isOpen) {
        panel.focus?.();
        if (input) input.focus();
      } else {
        toggle.focus();
      }
    };
    const openPanel = () => setPanelState(true);
    const closePanel = () => setPanelState(false);

    const csrfToken =
      document.querySelector('meta[name="csrf-token"]')?.getAttribute("content") ||
      (document.cookie.match(/csrftoken=([^;]+)/) || [])[1];
  
    function appendMessage(role, text) {
      const bubble = document.createElement("div");
      bubble.className = `finance-bot-msg finance-bot-${role}`;
      bubble.textContent = text;
      messagesEl.appendChild(bubble);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return bubble;
    }
  
    async function postMessage(body) {
      const res = await fetch("/api/finance-bot/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify(body),
      });
      const contentType = res.headers.get("content-type") || "";
      let payload = null;
      if (contentType.includes("application/json")) {
        payload = await res.json();
      } else {
        const text = await res.text();
        payload = text ? { error: text } : null;
      }
      if (!res.ok) {
        const message = (payload && payload.error) || "Unable to reach the financial coach right now.";
        const error = new Error(message);
        error.details = payload;
        throw error;
      }
      return payload;
    }
  
    toggle.addEventListener("click", () => {
      if (isPanelOpen()) {
        closePanel();
      } else {
        openPanel();
      }
    });
  
    closeBtn?.addEventListener("click", () => closePanel());
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isPanelOpen()) {
        closePanel();
      }
    });
  
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const question = (input?.value || "").trim();
      if (!question) return;
      if (!isPanelOpen()) openPanel();

      appendMessage("user", question);
      if (input) {
        input.value = "";
        input.disabled = true;
      }
  
      const loading = appendMessage("assistant", "Thinking...");
      try {
        const data = await postMessage({ message: question });
        loading.remove();
        appendMessage("assistant", data.reply);
      } catch (err) {
        loading.textContent = "Sorry, something went wrong.";
        console.error(err);
      } finally {
        if (input) {
          input.disabled = false;
          input.focus();
        }
      }
    });
  
    resetBtn?.addEventListener("click", async () => {
      messagesEl.innerHTML = "";
      try {
        await postMessage({ reset: true });
        appendMessage("assistant", "Conversation cleared. How can I help now?");
      } catch (err) {
        console.error(err);
      }
    });
  })();