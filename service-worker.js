/* Service worker — caché para uso sin conexión (todo es de mismo origen, incluidas las fuentes). */
const VERSION = "daira-v3";
const CORE = [
  "./",
  "./index.html",
  "./plan_data.js",
  "./manifest.webmanifest",
  "./fonts/newsreader-latin.woff2",
  "./fonts/newsreader-latinext.woff2",
  "./fonts/newsreader-viet.woff2",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable.png",
  "./icons/icon-maskable-192.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-32.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(VERSION).then((cache) => cache.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // todo lo necesario es local

  // cache-first; al fallar la red, respaldo a index.html (navegación offline)
  event.respondWith(
    caches.match(req).then(
      (cached) =>
        cached ||
        fetch(req)
          .then((res) => {
            if (res && res.ok && res.status === 200) {
              const copy = res.clone();
              caches.open(VERSION).then((c) => c.put(req, copy)).catch(() => {});
            }
            return res;
          })
          .catch(() => caches.match("./index.html"))
    )
  );
});
