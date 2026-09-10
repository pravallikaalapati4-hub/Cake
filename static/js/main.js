document.addEventListener('DOMContentLoaded', () => {
  // Navbar scroll effect
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    });
  }

  // Mobile menu
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      mobileMenu.classList.toggle('open');
      hamburger.classList.toggle('active');
    });
    mobileMenu.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => mobileMenu.classList.remove('open'));
    });
  }

  // Flash auto-dismiss
  document.querySelectorAll('.flash').forEach(flash => {
    const close = flash.querySelector('.close-flash');
    if (close) close.addEventListener('click', () => flash.remove());
    setTimeout(() => {
      flash.style.opacity = '0';
      flash.style.transform = 'translateX(100%)';
      setTimeout(() => flash.remove(), 300);
    }, 4500);
  });

  // Password toggle
  document.querySelectorAll('.toggle-pw').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.parentElement.querySelector('input');
      if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '🙈';
      } else {
        input.type = 'password';
        btn.innerHTML = '👁️';
      }
    });
  });

  // FAQ accordion
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const wasOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });

  // Quantity selectors
  document.querySelectorAll('.qty-selector').forEach(sel => {
    const input = sel.querySelector('input');
    const minus = sel.querySelector('[data-action="minus"]');
    const plus = sel.querySelector('[data-action="plus"]');
    if (minus) minus.addEventListener('click', () => {
      let v = parseInt(input.value) || 1;
      if (v > 1) input.value = v - 1;
    });
    if (plus) plus.addEventListener('click', () => {
      let v = parseInt(input.value) || 1;
      input.value = v + 1;
    });
  });

  // Smooth add-to-cart feedback
  document.querySelectorAll('form[data-ajax-cart]').forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      try {
        const res = await fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        if (data.status === 'ok') {
          const badge = document.querySelector('.badge-count.cart');
          if (badge) badge.textContent = data.cart_count;
          showToast(data.message || 'Added to cart!');
        }
      } catch {
        form.submit();
      }
    });
  });

  // Wishlist toggle AJAX
  document.querySelectorAll('[data-wishlist-toggle]').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const url = btn.dataset.url;
      try {
        const res = await fetch(url, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        const data = await res.json();
        btn.classList.toggle('active', data.status === 'added');
        showToast(data.status === 'added' ? 'Added to wishlist' : 'Removed from wishlist');
      } catch {
        window.location.href = url;
      }
    });
  });

  // Fade-in on scroll
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
});

function showToast(msg) {
  const container = document.querySelector('.flash-container') || (() => {
    const c = document.createElement('div');
    c.className = 'flash-container';
    document.body.appendChild(c);
    return c;
  })();
  const flash = document.createElement('div');
  flash.className = 'flash flash-success';
  flash.innerHTML = `<span>${msg}</span><button class="close-flash">&times;</button>`;
  container.appendChild(flash);
  flash.querySelector('.close-flash').addEventListener('click', () => flash.remove());
  setTimeout(() => flash.remove(), 3000);
}
