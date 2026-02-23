importScripts('/sw-config.js');

const CACHE_NAME = 'click32-' + self.CACHE_VERSION;

console.log('Service Worker iniciado com CACHE_NAME:', CACHE_NAME);

/* =========================
   INSTALL
========================= */
self.addEventListener('install', event => {
  console.log('Service Worker instalado');
  self.skipWaiting();
});

/* =========================
   ACTIVATE
========================= */
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

/* =========================
   FETCH (Network Only)
========================= */
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      // Aqui você pode colocar fallback se quiser no futuro
      return caches.match(event.request);
    })
  );
});

/* =========================
   MESSAGE (apenas skip waiting)
========================= */
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});