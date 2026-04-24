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

// Modal confirmación formulario
function openFormModal() {
  const m = document.getElementById('form-modal');
  m.classList.add('open');
  m.setAttribute('aria-hidden', 'false');
}
function closeFormModal() {
  const m = document.getElementById('form-modal');
  m.classList.remove('open');
  m.setAttribute('aria-hidden', 'true');
}
document.getElementById('form-modal').addEventListener('click', e => {
  if (e.target === e.currentTarget) closeFormModal();
});

// Envío AJAX del formulario de contacto
const contactForm = document.querySelector('.scon form');
if (contactForm) {
  contactForm.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = contactForm.querySelector('.fsub');
    const original = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Enviando…';
    try {
      const res = await fetch('https://formsubmit.co/ajax/adm.alonsodeercilla@gmail.com', {
        method: 'POST',
        headers: { 'Accept': 'application/json' },
        body: new FormData(contactForm)
      });
      const data = await res.json();
      if (data.success === 'true' || data.success === true) {
        contactForm.reset();
        openFormModal();
      }
    } catch {
      contactForm.submit();
    } finally {
      btn.disabled = false;
      btn.textContent = original;
    }
  });
}

// Scroll fade-in
const io = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) } }) }, { threshold: .08, rootMargin: '0px 0px -30px 0px' });
document.querySelectorAll('.fu').forEach(el => {
  const s = [...(el.parentElement?.querySelectorAll(':scope > .fu') || [])], i = s.indexOf(el);
  if (i > 0) el.style.transitionDelay = (i * .1) + 's';
  io.observe(el);
});
