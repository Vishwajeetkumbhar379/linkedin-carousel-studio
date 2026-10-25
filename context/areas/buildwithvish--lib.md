# buildwithvish/lib

Automate Instagram direct messages and comment replies using keyword matching, DM templates, and HMAC verification.

- `lib/ig-autodm/config.json`: JSON: _note, site, public_reply, keywords, dm, public
- `lib/ig-autodm/core.mjs`: Exports keyword matcher, DM builder, HMAC signature verifier, and Instagram comment change handler for private replies. (uses config.json, ig-webhook.js)
