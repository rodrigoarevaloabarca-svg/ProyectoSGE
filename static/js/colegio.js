// Tema claro / oscuro
function toggleTheme() {
  const h = document.documentElement, d = h.getAttribute('data-theme') === 'dark', n = d ? 'light' : 'dark';
  h.setAttribute('data-theme', n); localStorage.setItem('cae-theme', n); syncMobLabel(n);
}
function syncMobLabel(t) {
  const l = document.getElementById('mtl'), i = document.getElementById('mti');
  if (l) l.textContent = t === 'dark' ? 'claro' : 'oscuro';
  if (i) i.textContent = t === 'dark' ? 'light_mode' : 'dark_mode';
}
document.getElementById('tbtn').addEventListener('click', toggleTheme);
syncMobLabel(document.documentElement.getAttribute('data-theme'));

// Hamburger
const ham = document.getElementById('ham'), mob = document.getElementById('mob');
function closeMob() { ham.classList.remove('open'); mob.classList.remove('open'); ham.setAttribute('aria-expanded', 'false'); mob.setAttribute('aria-hidden', 'true') }
ham.addEventListener('click', () => { const o = ham.classList.toggle('open'); mob.classList.toggle('open', o); ham.setAttribute('aria-expanded', o); mob.setAttribute('aria-hidden', !o) });
document.addEventListener('click', e => { if (!ham.contains(e.target) && !mob.contains(e.target)) closeMob() });

// Scroll-to-top
const s2t = document.getElementById('s2t');
window.addEventListener('scroll', () => s2t.classList.toggle('vis', scrollY > 320), { passive: true });

// Scroll fade-in
const io = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } }) }, { threshold: .08, rootMargin: '0px 0px -30px 0px' });
document.querySelectorAll('.fu').forEach(el => {
  const s = [...(el.parentElement?.querySelectorAll(':scope > .fu') || [])], i = s.indexOf(el);
  if (i > 0) el.style.transitionDelay = (i * .1) + 's';
  io.observe(el);
});
