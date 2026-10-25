# buildwithvish/worker

Route API requests to newsletter, partner, and Instagram webhook handlers in a Cloudflare Worker.

- `worker/index.js`: Cloudflare Worker router for /api/*, delegating to newsletter, partner, ig-webhook modules. (uses newsletter.js, partner.js, ig-webhook.js, newsletter.js, partner.js, ig-webhook.js)
