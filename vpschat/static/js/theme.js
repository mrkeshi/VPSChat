(function(){
  const key = "chat_theme";
  const btn = document.getElementById("themeBtn");
  function apply(t){
    if(t === "dark") document.body.classList.add("dark");
    else document.body.classList.remove("dark");
    if(btn){
      btn.textContent = (t === "dark") ? "☀️" : "🌙";
      btn.title = (t === "dark") ? "حالت روز" : "حالت شب";
      btn.setAttribute("aria-label", btn.title);
    }
  }
  function current(){
    const stored = localStorage.getItem(key);
    if(stored === "dark" || stored === "light") return stored;
    // default: follow system
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    return prefersDark ? "dark" : "light";
  }
  function toggle(){
    const t = document.body.classList.contains("dark") ? "light" : "dark";
    localStorage.setItem(key, t);
    apply(t);
  }
  apply(current());
  if(btn) btn.addEventListener("click", toggle);
})();