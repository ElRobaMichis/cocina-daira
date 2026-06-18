/* Service worker — offline + actualización confiable.
   Contenido que cambia (HTML, datos, manifest) = network-first (siempre fresco con internet).
   Assets estáticos (fuentes, iconos) = cache-first (rápidos).
   Caché siempre como respaldo sin conexión. */
const VERSION = "daira-v5";
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
  if (url.origin !== self.location.origin) return;

  const isStatic = url.pathname.includes("/fonts/") || url.pathname.includes("/icons/");

  if (isStatic) {
    // cache-first para fuentes e iconos (no cambian casi nunca)
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
            .catch(() => undefined)
      )
    );
    return;
  }

  // network-first para HTML, plan_data.js y manifest (siempre la versión más reciente)
  const isHTML =
    req.mode === "navigate" || (req.headers.get("accept") || "").includes("text/html");
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(VERSION).then((c) => c.put(isHTML ? "./index.html" : req, copy)).catch(() => {});
        }
        return res;
      })
      .catch(() =>
        caches.match(req).then((c) => c || (isHTML ? caches.match("./index.html") : caches.match("./")))
      )
  );
});
