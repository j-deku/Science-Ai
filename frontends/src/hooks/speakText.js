export function speakText(text, lang = "en-US") {
  if (!window.speechSynthesis) return;

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang; 
  utterance.pitch = 1;
  utterance.rate = 1;
  window.speechSynthesis.speak(utterance);
}
