(function () {
  'use strict';
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Header: scrolled state, mobile menu ---------- */
  var header = document.querySelector('[data-header]');
  var toTop = document.querySelector('[data-to-top]');
  function onScroll() {
    var y = window.scrollY;
    header.classList.toggle('is-scrolled', y > 40);
    toTop.classList.toggle('is-visible', y > window.innerHeight * 0.8);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  var burger = document.querySelector('[data-burger]');
  var nav = document.getElementById('site-nav');
  function setMenu(open) {
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    nav.classList.toggle('is-open', open);
  }
  burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  nav.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') setMenu(false); });

  /* current section highlight in nav */
  var navLinks = Array.prototype.slice.call(nav.querySelectorAll('ul a[href^="#"]'));
  if ('IntersectionObserver' in window) {
    var secObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var href = '#' + en.target.id;
        navLinks.forEach(function (a) {
          if (en.isIntersecting) a.classList.toggle('is-current', a.getAttribute('href') === href);
          else if (a.getAttribute('href') === href) a.classList.remove('is-current');
        });
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    navLinks.forEach(function (a) { var s = document.querySelector(a.getAttribute('href')); if (s) secObs.observe(s); });
  }

  /* ---------- Hero video ---------- */
  var video = document.querySelector('[data-hero-video]');
  var hero = document.querySelector('.hero');
  if (video) {
    var mobileMq = window.matchMedia('(max-width: 960px)');
    /* mobile shows a gradient instead of the background video, so only load it on larger screens */
    var loadBg = function () {
      if (mobileMq.matches || video.getAttribute('src')) return;
      video.src = video.dataset.srcDesktop;
      if (!reduceMotion) { var pp = video.play(); if (pp && pp.catch) pp.catch(function () {}); }
    };
    loadBg();
    if (mobileMq.addEventListener) mobileMq.addEventListener('change', loadBg);
    /* respect reduced motion: no autoplay for people who ask for less movement */
    if (reduceMotion) video.removeAttribute('autoplay');
  }
  if (hero) requestAnimationFrame(function () { requestAnimationFrame(function () { hero.classList.add('is-in'); }); });


  /* ---------- Video lightbox (hero and Total Body Mapping play buttons) ---------- */
  var lb = document.querySelector('[data-lightbox]');
  var lbOpeners = document.querySelectorAll('[data-lightbox-open]');
  if (lb && lbOpeners.length) {
    var lbFrame = lb.querySelector('[data-lightbox-frame]');
    var lbClose = lb.querySelector('.lightbox__close');
    var bgWasPlaying = false;
    var lastOpener = null;
    var openLb = function (opener) {
      lastOpener = opener;
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + opener.dataset.videoId + '?autoplay=1&rel=0&modestbranding=1';
      f.title = 'Total Body Mapping at Sunstate Family Practice';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      f.allowFullscreen = true;
      lbFrame.appendChild(f);
      lb.hidden = false;
      document.body.classList.add('has-lightbox');
      if (video && !video.paused) { bgWasPlaying = true; video.pause(); }
      lbClose.focus();
    };
    var closeLb = function () {
      if (lb.hidden) return;
      lb.hidden = true;
      lbFrame.innerHTML = '';
      document.body.classList.remove('has-lightbox');
      if (video && bgWasPlaying) { video.play(); bgWasPlaying = false; }
      if (lastOpener) lastOpener.focus();
    };
    lbOpeners.forEach(function (o) { o.addEventListener('click', function () { openLb(o); }); });
    lb.querySelectorAll('[data-lightbox-close]').forEach(function (el) { el.addEventListener('click', closeLb); });
    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') closeLb();
      if (e.key === 'Tab') { e.preventDefault(); lbClose.focus(); }
    });
  }


  /* ---------- Inline hero video (mobile) ----------
     A self-hosted clip plays muted with no player chrome (YouTube's iOS player
     always shows its own buttons). "Watch with sound" swaps in the YouTube video. */
  var inline = document.querySelector('[data-inline-video]');
  if (inline) {
    var clip = inline.querySelector('video');
    if (window.matchMedia('(max-width: 960px)').matches) {
      clip.src = clip.dataset.src;
      if (!reduceMotion) { var cp = clip.play(); if (cp && cp.catch) cp.catch(function () {}); }
    }
    inline.querySelector('.hero__inline-sound').addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + inline.dataset.videoId + '?autoplay=1&playsinline=1&rel=0&modestbranding=1';
      f.title = 'Total Body Mapping at Sunstate Family Practice';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      f.allowFullscreen = true;
      inline.innerHTML = '';
      inline.appendChild(f);
    });
  }

  /* ---------- Image reveals ---------- */
  /* observe the unclipped parent: a fully clipped target may never report as intersecting */
  var reveals = document.querySelectorAll('.reveal-img');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var rObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.querySelectorAll('.reveal-img').forEach(function (el) { el.classList.add('is-visible'); });
        rObs.unobserve(en.target);
      });
    }, { threshold: 0.15 });
    var parents = [];
    reveals.forEach(function (el) { if (parents.indexOf(el.parentElement) < 0) parents.push(el.parentElement); });
    parents.forEach(function (p) { rObs.observe(p); });
  } else {
    reveals.forEach(function (el) { el.classList.add('is-visible'); });
  }

  /* ---------- Today's consulting hours (clinic time is Australia/Brisbane, no daylight saving) ---------- */
  var clinicNow = function () {
    try {
      var parts = new Intl.DateTimeFormat('en-AU', { timeZone: 'Australia/Brisbane', weekday: 'short', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' }).formatToParts(new Date());
      var get = function (t) { return parts.filter(function (p) { return p.type === t; })[0].value; };
      return { day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(get('weekday')), min: +get('hour') * 60 + +get('minute') };
    } catch (e) { var d = new Date(); return { day: d.getDay(), min: d.getHours() * 60 + d.getMinutes() }; }
  };
  var now = clinicNow();
  document.querySelectorAll('[data-hours] tr').forEach(function (tr) {
    if (tr.dataset.days.split(',').indexOf(String(now.day)) > -1) tr.classList.add('is-today');
  });

  /* ---------- Life stages rail: buttons, drag to scroll, progress ---------- */
  var rail = document.querySelector('[data-rail]');
  if (rail) {
    var bar = document.querySelector('[data-rail-bar]');
    var prev = document.querySelector('[data-rail-prev]');
    var next = document.querySelector('[data-rail-next]');
    var step = function () { var c = rail.querySelector('.stage'); return c ? c.getBoundingClientRect().width + 22 : 300; };
    var sync = function () {
      var max = rail.scrollWidth - rail.clientWidth;
      var p = max > 0 ? rail.scrollLeft / max : 1;
      bar.style.width = (Math.max(rail.clientWidth / rail.scrollWidth, 0.12) * 100 + p * (1 - rail.clientWidth / rail.scrollWidth) * 100).toFixed(1) + '%';
      prev.disabled = rail.scrollLeft < 4;
      next.disabled = rail.scrollLeft > max - 4;
    };
    prev.addEventListener('click', function () { rail.scrollBy({ left: -step(), behavior: reduceMotion ? 'auto' : 'smooth' }); });
    next.addEventListener('click', function () { rail.scrollBy({ left: step(), behavior: reduceMotion ? 'auto' : 'smooth' }); });
    rail.addEventListener('scroll', function () { requestAnimationFrame(sync); }, { passive: true });
    window.addEventListener('resize', sync);
    rail.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); next.click(); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); prev.click(); }
    });
    var down = null;
    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse') return;
      down = { x: e.clientX, left: rail.scrollLeft, moved: false };
    });
    window.addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - down.x;
      if (Math.abs(dx) > 4) { down.moved = true; rail.classList.add('is-dragging'); }
      rail.scrollLeft = down.left - dx;
    });
    window.addEventListener('pointerup', function () {
      if (!down) return;
      down = null;
      rail.classList.remove('is-dragging');
      /* let scroll-snap settle on the nearest card */
      var s = step(); rail.scrollTo({ left: Math.round(rail.scrollLeft / s) * s, behavior: reduceMotion ? 'auto' : 'smooth' });
    });
    sync();
  }

  /* ---------- Services explorer ---------- */
  var svcTabs = Array.prototype.slice.call(document.querySelectorAll('[data-svc]'));
  var selectSvc = function (tab, focus) {
    var key = tab.dataset.svc;
    svcTabs.forEach(function (t) {
      var on = t === tab;
      t.classList.toggle('is-active', on);
      t.setAttribute('aria-selected', String(on));
      t.tabIndex = on ? 0 : -1;
      var panel = document.getElementById(t.getAttribute('aria-controls'));
      panel.hidden = !on;
      panel.classList.toggle('is-active', on);
    });
    document.querySelectorAll('[data-svc-bg]').forEach(function (img) { img.classList.toggle('is-active', img.dataset.svcBg === key); });
    if (focus) tab.focus();
  };
  svcTabs.forEach(function (t, i) {
    t.addEventListener('click', function () { selectSvc(t); });
    t.addEventListener('keydown', function (e) {
      var dir = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
      if (dir) { e.preventDefault(); selectSvc(svcTabs[(i + dir + svcTabs.length) % svcTabs.length], true); }
    });
  });

  /* ---------- 15-minute dial: draw ticks, sweep once when seen ---------- */
  var minutes = document.querySelector('[data-minutes]');
  if (minutes) {
    var ticks = minutes.querySelector('.minutes__ticks');
    for (var tk = 0; tk < 12; tk++) {
      var a = tk * Math.PI / 6;
      var ln = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      ln.setAttribute('x1', 60 + 40 * Math.sin(a)); ln.setAttribute('y1', 60 - 40 * Math.cos(a));
      ln.setAttribute('x2', 60 + 45 * Math.sin(a)); ln.setAttribute('y2', 60 - 45 * Math.cos(a));
      ticks.appendChild(ln);
    }
    if ('IntersectionObserver' in window && !reduceMotion) {
      var mObs = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { minutes.classList.add('is-on'); mObs.disconnect(); }
      }, { threshold: 0.6 });
      mObs.observe(minutes);
    } else { minutes.classList.add('is-on'); }
  }

  /* ---------- Mission / vision / values panels ---------- */
  var mvv = document.querySelector('[data-mvv]');
  if (mvv) {
    var panels = Array.prototype.slice.call(mvv.querySelectorAll('.mvv__panel'));
    var openPanel = function (p) {
      panels.forEach(function (x) {
        var on = x === p;
        x.classList.toggle('is-open', on);
        x.querySelector('.mvv__head').setAttribute('aria-expanded', String(on));
      });
    };
    panels.forEach(function (p) {
      p.querySelector('.mvv__head').addEventListener('click', function () { openPanel(p); });
      p.addEventListener('mouseenter', function () { if (window.matchMedia('(hover: hover) and (min-width: 901px)').matches) openPanel(p); });
    });
  }

  /* ---------- Dr Ganter portrait pops in after the team photo ---------- */
  var principal = document.querySelector('[data-principal]');
  if (principal) {
    if ('IntersectionObserver' in window && !reduceMotion) {
      var pObs = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { principal.classList.add('is-visible'); pObs.disconnect(); }
      }, { threshold: 0.3 });
      pObs.observe(principal);
    } else { principal.classList.add('is-visible'); }
  }

  /* ---------- Team cards: stagger in ---------- */
  var team = document.querySelector('.team');
  if (team) {
    team.querySelectorAll('.mate').forEach(function (m, i) { m.style.setProperty('--i', i); });
    if ('IntersectionObserver' in window && !reduceMotion) {
      var tObs = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { team.classList.add('is-visible'); tObs.disconnect(); }
      }, { threshold: 0.1 });
      tObs.observe(team);
    } else { team.classList.add('is-visible'); }
  }

  /* ---------- Process steps ---------- */
  var steps = document.querySelectorAll('.step');
  var stepImgs = document.querySelectorAll('[data-step-img]');
  if ('IntersectionObserver' in window) {
    var stObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var n = en.target.dataset.step;
        steps.forEach(function (s) { s.classList.toggle('is-active', s === en.target); });
        stepImgs.forEach(function (im) { im.classList.toggle('is-active', im.dataset.stepImg === n); });
      });
    }, { rootMargin: '-45% 0px -45% 0px' });
    steps.forEach(function (s) { stObs.observe(s); });
  }

  /* ---------- Parallax on full-bleed images ---------- */
  var para = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  if (para.length && !reduceMotion) {
    var ticking = false;
    var update = function () {
      var vh = window.innerHeight;
      para.forEach(function (img) {
        var r = img.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        var progress = (r.top + r.height / 2 - vh / 2) / (vh + r.height);
        img.style.transform = 'translate3d(0,' + (progress * -16 - 8).toFixed(2) + '%,0)';
      });
      ticking = false;
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  /* ---------- Back to top (the #top header is sticky, so jump to 0 explicitly) ---------- */
  document.querySelectorAll('a[href="#top"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: reduceMotion ? 'auto' : 'smooth' });
      if (history.replaceState) history.replaceState(null, '', location.pathname + location.search);
    });
  });

  /* ---------- Contact form ----------
     Posts JSON to data-endpoint when one is configured. Until a delivery
     service is connected, it offers email or phone instead so nothing is lost. */
  var form = document.querySelector('[data-contact-form]');
  if (form) {
    var status = form.querySelector('[data-form-status]');
    var submitBtn = form.querySelector('button[type="submit"]');
    var fields = Array.prototype.slice.call(form.querySelectorAll('input[required], textarea[required], select[required]'));
    var emailOk = function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v); };
    var check = function (el) {
      var v = el.value.trim();
      var ok = el.type === 'email' ? emailOk(v) : el.type === 'tel' ? v.replace(/\D/g, '').length >= 8 : v !== '';
      var wrap = el.closest('.field');
      wrap.classList.toggle('is-invalid', !ok);
      el.setAttribute('aria-invalid', String(!ok));
      if (!ok) el.setAttribute('aria-describedby', el.id + '-err'); else el.removeAttribute('aria-describedby');
      return ok;
    };
    fields.forEach(function (el) {
      el.addEventListener('blur', function () { if (el.value.trim() !== '') check(el); });
      el.addEventListener('input', function () { if (el.closest('.field').classList.contains('is-invalid')) check(el); });
      el.addEventListener('change', function () { if (el.tagName === 'SELECT') check(el); });
    });
    var setStatus = function (cls, html) { status.className = 'contact__status ' + cls; status.innerHTML = html; };
    var escapeHtml = function (t) { return t.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var firstBad = null;
      fields.forEach(function (el) { if (!check(el) && !firstBad) firstBad = el; });
      if (firstBad) { firstBad.focus(); return; }
      if (form.querySelector('.hp').value) return;
      var data = {};
      new FormData(form).forEach(function (v, k) { if (k !== '_honey') data[k] = String(v).trim(); });
      var endpoint = form.dataset.endpoint;
      if (!endpoint) {
        var body = 'Name: ' + data.first_name + ' ' + data.last_name + '\nEmail: ' + data.email + '\nPhone: ' + data.phone +
          '\nHow did you hear about us: ' + data.heard_about_us + '\n\n' + data.message;
        var mailto = 'mailto:reception@sunstatefamilypractice.com.au?subject=' + encodeURIComponent('Website enquiry from ' + data.first_name + ' ' + data.last_name) +
          '&body=' + encodeURIComponent(body);
        setStatus('is-pending', 'Online enquiries aren’t connected yet. <a href="' + escapeHtml(mailto) + '">Send your message by email</a> (we’ve filled it in for you) or call us on <a href="tel:+61732077744">(07) 3207 7744</a>.');
        return;
      }
      submitBtn.disabled = true;
      submitBtn.textContent = 'Sending…';
      fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error(r.status); })
        .then(function () {
          form.reset();
          fields.forEach(function (el) { el.closest('.field').classList.remove('is-invalid'); });
          setStatus('is-success', 'Message sent. Thanks, ' + escapeHtml(data.first_name) + '. Our reception team will get back to you during opening hours.');
        })
        .catch(function () {
          setStatus('is-error', 'Your message didn’t send. Check your connection and try again, or call us on <a href="tel:+61732077744">(07) 3207 7744</a>.');
        })
        .then(function () { submitBtn.disabled = false; submitBtn.textContent = 'Send message'; });
    });
  }

  /* ---------- Year ---------- */
  var yr = document.querySelector('[data-year]');
  if (yr) yr.textContent = new Date().getFullYear();
})();
