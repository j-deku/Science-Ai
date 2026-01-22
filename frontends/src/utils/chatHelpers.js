
export function smartGreeting(name = "") {
  const hour = new Date().getHours();
  let base;

  if (hour >= 4 && hour < 11) base = "🌅 Good morning";
  else if (hour >= 11 && hour < 16) base = "🌞 Good afternoon";
  else if (hour >= 16 && hour < 20) base = "🌇 Good evening";
  else base = "🌙 Night Wolf!";

  return name ? `${base}, ${name}!` : `${base}!`;   
}

// utils/chatHelpers.js
export function simulateTyping(setMessages, fullText, speed = 25, onTypeChar) {
  return new Promise((resolve) => {
    let i = 0;

    const interval = setInterval(() => {
      setMessages((prev) => {
        const updated = [...prev];

        // Ensure there is at least one message
        if (!updated.length) {
          updated.push({ role: "assistant", text: "" });
        }

        updated[updated.length - 1].text = fullText.slice(0, i);
        return updated;
      });

      // Play typing sound per character
      if (onTypeChar && i < fullText.length) {
        onTypeChar();
      }

      i++;

      if (i > fullText.length) {
        clearInterval(interval);
        resolve();
      }
    }, speed);
  });
}

export function scrollToBottom() {
  setTimeout(() => {
    window.scrollTo(0, document.body.scrollHeight);
  }, 50);
}
