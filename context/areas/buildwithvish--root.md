# buildwithvish/(root)

Configure, build, and deploy the Vish site using Cloudflare Workers and Netlify functions.

- `README.md`: Describes project structure, build process, Netlify deployment, and newsletter submission handling. (uses build.py, welcome-series.md, style.css, scene.js, sound.js, portfolio-scene.js)
- `netlify.toml`: Sets Netlify build publish folder to site and functions directory to netlify/functions. (uses build.py)
- `wrangler.toml`: Wrangler config for Cloudflare Worker build, assets, secrets, and deployment settings. (uses build.py, index.js)
