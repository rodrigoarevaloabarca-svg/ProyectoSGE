// ── Dark mode toggle ──────────────────────────────────────
const html = document.documentElement;
const themeToggle = document.getElementById('theme-toggle');

// Persist preference
if (localStorage.getItem('theme') === 'dark' ||
    (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
  html.classList.add('dark');
}

themeToggle.addEventListener('click', () => {
  html.classList.toggle('dark');
  localStorage.setItem('theme', html.classList.contains('dark') ? 'dark' : 'light');
});

// ── Hamburger menu ────────────────────────────────────────
const hamburgerBtn = document.getElementById('hamburger-btn');
const hamburgerIcon = document.getElementById('hamburger-icon');
const mobileMenu = document.getElementById('mobile-menu');
let menuOpen = false;

hamburgerBtn.addEventListener('click', () => {
  menuOpen = !menuOpen;
  mobileMenu.classList.toggle('open', menuOpen);
  hamburgerIcon.textContent = menuOpen ? 'close' : 'menu';
  hamburgerBtn.setAttribute('aria-expanded', menuOpen);
});

// Close menu on link click
mobileMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    menuOpen = false;
    mobileMenu.classList.remove('open');
    hamburgerIcon.textContent = 'menu';
    hamburgerBtn.setAttribute('aria-expanded', false);
  });
});

// ── Scroll-to-top button ──────────────────────────────────
const scrollBtn = document.getElementById('scroll-top-btn');

window.addEventListener('scroll', () => {
  scrollBtn.classList.toggle('visible', window.scrollY > 400);
}, { passive: true });