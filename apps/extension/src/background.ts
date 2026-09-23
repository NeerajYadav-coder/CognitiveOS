// EMERGENCY BRIDGE V2
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log("[BRIDGE] Message received:", message.type);

  if (message.type === "PROCESS_THOUGHT") {
    // Immediate ACK to content script that bridge is alive
    // (Wait, we can't send multiple responses, so we'll just proceed)

    fetch("http://127.0.0.1:8000/api/v1/process", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(message.payload)
    })
    .then(r => {
      if (!r.ok) throw new Error(`Brain Error: ${r.status}`);
      return r.json();
    })
    .then(data => {
      sendResponse({ success: true, data });
    })
    .catch(err => {
      console.error("[BRIDGE] Error:", err.message);
      sendResponse({ success: false, error: err.message });
    });

    return true; // Keep alive
  }
});
