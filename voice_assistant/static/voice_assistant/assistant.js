(function () {
  const form = document.querySelector("[data-assistant-form]");
  if (!form) return;
  const input = form.querySelector("textarea");
  const mic = form.querySelector("[data-mic]");
  const messages = document.querySelector("[data-messages]");
  const welcome = document.querySelector("[data-welcome]");
  const status = document.querySelector("[data-status]");
  const suggestions = document.querySelector("[data-suggestions]");
  const autoSpeak = document.querySelector("[data-auto-speak]");
  let recorder = null;
  let chunks = [];

  function addMessage(role, text, meta) {
    welcome.hidden = true;
    const article = document.createElement("article");
    article.className = "voice-message voice-message-" + role;
    const p = document.createElement("p");
    p.textContent = text;
    article.appendChild(p);
    if (meta) {
      const small = document.createElement("small");
      small.textContent = meta;
      article.appendChild(small);
    }
    messages.appendChild(article);
    article.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function speak(text, lang) {
    if (!autoSpeak.checked || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === "ar" ? "ar-TN" : lang === "en" ? "en-US" : "fr-FR";
    window.speechSynthesis.speak(utterance);
  }

  async function send(audio) {
    const question = input.value.trim();
    if (!question && !audio) return;
    if (question) addMessage("user", question);
    const data = new FormData(form);
    if (audio) data.append("audio", audio, "question.webm");
    status.textContent = form.dataset.thinking;
    form.classList.add("is-busy");
    try {
      const response = await fetch(form.action, { method: "POST", body: data,
        headers: { "X-Requested-With": "XMLHttpRequest" } });
      const result = await response.json();
      if (!response.ok) throw new Error(result.erreur || form.dataset.error);
      if (audio && result.transcription) addMessage("user", result.transcription, "🎙");
      addMessage("assistant", result.reponse, result.source === "GEMINI" ? "Gemini" : "Mode local");
      input.value = "";
      suggestions.replaceChildren();
      (result.suggestions || []).forEach(function (text) {
        const button = document.createElement("button");
        button.type = "button"; button.textContent = text; suggestions.appendChild(button);
      });
      speak(result.reponse, result.langue);
      status.textContent = "";
    } catch (error) {
      addMessage("error", error.message || form.dataset.error);
      status.textContent = "";
    } finally { form.classList.remove("is-busy"); }
  }

  form.addEventListener("submit", function (event) { event.preventDefault(); send(null); });
  suggestions.addEventListener("click", function (event) {
    if (event.target.tagName !== "BUTTON") return;
    input.value = event.target.textContent; send(null);
  });
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(null); }
  });

  mic.addEventListener("click", async function () {
    if (recorder && recorder.state === "recording") { recorder.stop(); return; }
    if (!navigator.mediaDevices || !window.MediaRecorder) {
      addMessage("error", "Micro non pris en charge par ce navigateur."); return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/webm";
      recorder = new MediaRecorder(stream, { mimeType: mime }); chunks = [];
      recorder.ondataavailable = function (event) { if (event.data.size) chunks.push(event.data); };
      recorder.onstop = function () {
        stream.getTracks().forEach(function (track) { track.stop(); });
        mic.classList.remove("is-recording"); mic.setAttribute("aria-label", form.dataset.mic);
        status.textContent = ""; send(new Blob(chunks, { type: "audio/webm" }));
      };
      recorder.start(); mic.classList.add("is-recording");
      mic.setAttribute("aria-label", form.dataset.stop); status.textContent = form.dataset.listening;
      setTimeout(function () { if (recorder && recorder.state === "recording") recorder.stop(); }, 30000);
    } catch (error) { addMessage("error", "Accès au micro refusé ou indisponible."); }
  });
})();
