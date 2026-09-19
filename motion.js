/* Motion. Progressive enhancement, in the strict sense: this file adds the
   `js` class, and the stylesheet only hides anything when that class is
   present. If this script fails to parse, fails to run, or runs in a browser
   without IntersectionObserver, nothing is ever hidden and the page is simply
   the page.

   Everything here is also a no-op under prefers-reduced-motion — the CSS
   neutralises the classes this file sets, so there is no second code path to
   keep in sync. */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduced = window.matchMedia &&
                window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Without IntersectionObserver there is no way to un-hide on scroll, so
  // never hide in the first place.
  if (!('IntersectionObserver' in window)) return;
  root.classList.add('js');

  function stagger(nodes, step, base) {
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].setAttribute('data-rise', '');
      nodes[i].style.setProperty('--rise-delay', (base + i * step) + 'ms');
    }
  }

  // ---- hero: arrives on load, in reading order -------------------------
  var hero = document.querySelector('.hero-main');
  if (hero) {
    stagger(hero.children, 70, 60);
    var portrait = document.querySelector('.hero-portrait');
    if (portrait) stagger([portrait], 0, 40);
  }

  // ---- sections: arrive on scroll --------------------------------------
  var groups = document.querySelectorAll(
    '.evidence .ev, .section > .sec-label, .case, .mini, .band-item, ' +
    '.entry, .bg-col, .contact-line, .contact-note, .links');
  for (var i = 0; i < groups.length; i++) groups[i].setAttribute('data-rise', '');

  // Within the evidence strip and the focus band the items are peers, so
  // they stagger against each other rather than each arriving alone.
  ['.evidence .ev', '.band-item'].forEach(function (sel) {
    var row = document.querySelectorAll(sel);
    for (var j = 0; j < row.length; j++) {
      row[j].style.setProperty('--rise-delay', (j * 70) + 'ms');
    }
  });

  var reveal = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      reveal.unobserve(e.target);           // arrival is one-way
    });
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });

  for (var k = 0; k < groups.length; k++) reveal.observe(groups[k]);

  // The hero is above the fold; show it immediately rather than waiting for
  // a scroll event that may never come.
  requestAnimationFrame(function () {
    var up = document.querySelectorAll('.hero-main [data-rise], .hero-portrait[data-rise]');
    for (var n = 0; n < up.length; n++) up[n].classList.add('is-in');
  });

  // ---- the chart draws itself ------------------------------------------
  var charts = document.querySelectorAll('.chart');
  for (var c = 0; c < charts.length; c++) {
    var bars = charts[c].querySelectorAll('.g-bar');
    for (var bi = 0; bi < bars.length; bi++) bars[bi].style.setProperty('--i', bi);
    var ticks = charts[c].querySelectorAll('.g-tick');
    for (var ti = 0; ti < ticks.length; ti++) ticks[ti].style.setProperty('--i', ti);
    var spans = charts[c].querySelectorAll('.g-span');
    for (var si = 0; si < spans.length; si++) spans[si].style.setProperty('--i', si);
  }
  var chartWatch = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('is-in');
      chartWatch.unobserve(e.target);
    });
  }, { threshold: 0.35 });
  for (var d = 0; d < charts.length; d++) chartWatch.observe(charts[d]);

  // ---- sticky header gains a shadow once it is actually sticking -------
  var bar = document.querySelector('.topbar');
  var sentinel = document.querySelector('.hero');
  if (bar && sentinel) {
    new IntersectionObserver(function (entries) {
      bar.classList.toggle('is-stuck', !entries[0].isIntersecting);
    }, { rootMargin: '-72px 0px 0px 0px', threshold: 0 }).observe(sentinel);
  }

  // ---- theme toggle cross-fade ------------------------------------------
  // app.js owns the toggle; this only paints the transition over it, and
  // removes the class afterwards so the rule never sits on the page during
  // ordinary scrolling.
  if (!reduced) {
    document.addEventListener('click', function (e) {
      var hit = e.target.closest && e.target.closest('[data-theme-toggle]');
      if (!hit) return;
      root.classList.add('theme-shift');
      window.setTimeout(function () { root.classList.remove('theme-shift'); }, 260);
    }, true);
  }
})();
