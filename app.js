/* Theme toggle — persists per-browser, falls back gracefully. */
(function () {
  var root = document.documentElement;
  var KEY = 'qnd-theme';

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }
  function save(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }
  function systemDark() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  }
  function current() {
    var s = root.getAttribute('data-theme');
    if (s === 'dark' || s === 'light') return s;
    return systemDark() ? 'dark' : 'light';
  }
  function apply(v) {
    root.setAttribute('data-theme', v);
    var btns = document.querySelectorAll('[data-theme-toggle] .tstate');
    for (var i = 0; i < btns.length; i++) {
      btns[i].textContent = v === 'dark' ? 'LIGHT' : 'DARK';
    }
  }

  // init from stored choice (system default left un-stamped otherwise)
  var s = stored();
  if (s === 'dark' || s === 'light') apply(s);

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target.closest('[data-theme-toggle]') : null;
    if (!t) return;
    var next = current() === 'dark' ? 'light' : 'dark';
    apply(next);
    save(next);
  });

  // sync label on load for un-stamped (system) state
  document.addEventListener('DOMContentLoaded', function () {
    var btns = document.querySelectorAll('[data-theme-toggle] .tstate');
    var label = current() === 'dark' ? 'LIGHT' : 'DARK';
    for (var i = 0; i < btns.length; i++) btns[i].textContent = label;
  });
})();
