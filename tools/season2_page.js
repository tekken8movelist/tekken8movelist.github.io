(() => {
  const notationButtons = {gfx: 'ng', nn: 'nn', txt: 'nt'};
  function setNotation(mode) {
    if (!notationButtons[mode]) mode = 'gfx';
    document.body.classList.toggle('txt-mode', mode === 'txt');
    document.body.classList.toggle('nn-mode', mode === 'nn');
    Object.entries(notationButtons).forEach(([key, id]) => {
      const active = key === mode;
      const button = document.getElementById(id);
      button.classList.toggle('on', active);
      button.setAttribute('aria-pressed', String(active));
    });
    try { localStorage.setItem('tk-notation', mode); } catch (_) {}
  }
  let notation = 'gfx';
  try { notation = localStorage.getItem('tk-notation') || 'gfx'; } catch (_) {}
  setNotation(notation);
  Object.entries(notationButtons).forEach(([mode, id]) => {
    document.getElementById(id).addEventListener('click', () => setNotation(mode));
  });

  const themeButtons = {dark: 'thd', light: 'thl'};
  function setTheme(theme) {
    if (!themeButtons[theme]) theme = 'dark';
    document.documentElement.classList.toggle('dark', theme === 'dark');
    Object.entries(themeButtons).forEach(([key, id]) => {
      const active = key === theme;
      const button = document.getElementById(id);
      button.classList.toggle('on', active);
      button.setAttribute('aria-pressed', String(active));
    });
    try { localStorage.setItem('tk-theme', theme); } catch (_) {}
  }
  let theme = 'dark';
  try { theme = localStorage.getItem('tk-theme') || 'dark'; } catch (_) {}
  setTheme(theme);
  Object.entries(themeButtons).forEach(([themeName, id]) => {
    document.getElementById(id).addEventListener('click', () => setTheme(themeName));
  });
})();
