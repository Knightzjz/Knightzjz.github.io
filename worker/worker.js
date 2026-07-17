/**
 * Cloudflare Worker — Google Scholar proxy for knightzjz.github.io
 *
 * Deploy: npx wrangler deploy
 * Then replace the PROXIES array in index.html with your worker URL.
 */

export default {
  async fetch(request, env, ctx) {
    // Allowed origins (your site + local dev)
    const ALLOWED = [
      'https://knightzjz.github.io',
      'http://localhost:3000',
      'http://127.0.0.1:3000'
    ];

    const origin = request.headers.get('Origin') || '';
    const isAllowed = ALLOWED.includes(origin);

    // CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: {
          'Access-Control-Allow-Origin': isAllowed ? origin : ALLOWED[0],
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Max-Age': '86400'
        }
      });
    }

    // Only allow GET
    if (request.method !== 'GET') {
      return new Response('Method not allowed', { status: 405 });
    }

    const url = new URL(request.url);
    const target = url.searchParams.get('url');

    if (!target) {
      return new Response('Missing ?url= parameter', { status: 400 });
    }

    // Only proxy Google Scholar
    if (!target.startsWith('https://scholar.google.com/')) {
      return new Response('Only scholar.google.com is allowed', { status: 403 });
    }

    const cacheKey = new Request(target, { method: 'GET' });
    const cache = caches.default;

    // Try Cloudflare cache first (30 min)
    let response = await cache.match(cacheKey);
    if (response) {
      response = new Response(response.body, response);
      response.headers.set('X-Cache', 'HIT');
    } else {
      response = await fetch(target, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; ScholarProxy/1.0)'
        }
      });

      if (!response.ok) {
        return new Response('Upstream fetch failed', { status: 502 });
      }

      // Clone before caching
      const toCache = new Response(response.body, response);
      toCache.headers.set('Cache-Control', 'public, max-age=1800');
      ctx.waitUntil(cache.put(cacheKey, toCache));

      response = new Response(response.body, response);
      response.headers.set('X-Cache', 'MISS');
    }

    // Set CORS headers on response
    response.headers.set('Access-Control-Allow-Origin', isAllowed ? origin : ALLOWED[0]);
    response.headers.set('Access-Control-Expose-Headers', 'X-Cache');
    response.headers.set('Vary', 'Origin');

    return response;
  }
};
