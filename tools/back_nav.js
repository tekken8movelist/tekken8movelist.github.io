/* ---- back navigation: character page -> hub -------------------------
   Shared verbatim by both page families (36 generator pages via
   build_season2.py, 5 legacy pipeline pages via patch_legacy_back_nav.py).
   Nothing here is required for the breadcrumb to work -- that is a plain
   <a>, and the reveal bar stays parked off-screen when this never runs.
   ------------------------------------------------------------------- */
(() => {
  const HOME = 'index.html';

  // Only when the visitor actually arrived from the hub: going back instead of
  // navigating restores its scroll position and search term. A fresh visit
  // (bookmark, search result, shared link) still needs a real navigation.
  //
  // Any same-origin index.html counts, not just one in this page's own
  // directory. The site has exactly three and they are all hubs, and the five
  // Simplified-only pipeline pages are reached from /en/ and /zh-Hant/ as
  // ../name.html -- requiring the same directory sent those visitors back to
  // the Simplified hub, losing both their language and their scroll position.
  function cameFromHub() {
    if (!document.referrer) return false;
    let referrer;
    try {
      referrer = new URL(document.referrer, location.href);
    } catch (_) {
      return false;
    }
    if (referrer.origin !== location.origin) return false;
    const leaf = referrer.pathname.slice(referrer.pathname.lastIndexOf('/') + 1);
    return leaf === '' || leaf === HOME;
  }

  document.querySelectorAll('[data-home]').forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.defaultPrevented || event.button !== 0) return;
      // never hijack open-in-new-tab / new-window
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      if (history.length < 2 || !cameFromHub()) return;
      event.preventDefault();
      history.back();
    });
  });

  const bar = document.querySelector('.revealbar');
  if (!bar) return;

  // "Has the banner left the viewport" is the exact question, and unlike a
  // pixel threshold it is unaffected by the 1.25 screen zoom on <body>.
  const banner = document.getElementById('top');
  const observable = Boolean(banner) && 'IntersectionObserver' in window;
  let pastBanner = false;
  if (observable) {
    new IntersectionObserver((entries) => {
      pastBanner = !entries[0].isIntersecting;
      if (!pastBanner) bar.classList.remove('show');
    }).observe(banner);
  }

  let previousY = window.scrollY;
  let queued = false;

  function update() {
    queued = false;
    const y = window.scrollY;
    // Scrolling up means "I am looking for navigation". Only a deliberate
    // downward move puts the bar away again, so jitter cannot make it blink.
    if (!(observable ? pastBanner : y > 220)) bar.classList.remove('show');
    else if (y < previousY - 4) bar.classList.add('show');
    else if (y > previousY + 4) bar.classList.remove('show');
    previousY = y;
  }

  addEventListener('scroll', () => {
    if (queued) return;
    queued = true;
    requestAnimationFrame(update);
  }, { passive: true });
})();
