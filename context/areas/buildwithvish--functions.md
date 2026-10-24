# buildwithvish/functions

Handle external API endpoints for Instagram webhook, partner form, and newsletter subscription processing.

- `functions/api/ig-webhook.js`: Cloudflare function forwarding Instagram webhook requests to ig-autodm handler. (uses core.mjs, core.mjs)
- `functions/api/newsletter.js`: Accepts POST, validates email, posts unconfirmed subscriber to MailerLite API, returns 200 OK or appropriate error.
- `functions/api/partner.js`: Processes partner form POST, validates name/email/message, sends formatted email via Cloudflare email binding, responds 200 OK or error. (uses wrangler.toml)
