(function () {
  var header = document.querySelector('.site-header');
  var btn = header && header.querySelector('.menu-btn');
  if (!btn) return;
  function setOpen(open) {
    header.classList.toggle('open', open);
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  btn.addEventListener('click', function () { setOpen(!header.classList.contains('open')); });
  header.querySelectorAll('.nav a').forEach(function (a) {
    a.addEventListener('click', function () { setOpen(false); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && header.classList.contains('open')) { setOpen(false); btn.focus(); }
  });
  document.addEventListener('click', function (e) {
    if (!header.contains(e.target)) setOpen(false);
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) setOpen(false);
  });
})();
