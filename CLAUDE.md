# Sunstate Family Practice website

## The site must not be indexed by search engines

This site must stay out of search results until the owner explicitly says otherwise. Every change must keep all three layers below in place:

1. **HTTP header:** `vercel.json` sends `X-Robots-Tag: noindex, nofollow` on every path. Don't remove or narrow it.
2. **Meta tag:** every HTML page, template and layout includes
   `<meta name="robots" content="noindex, nofollow">` in its `<head>`. If you use a framework, put it in the root layout so no page can miss it.
3. **No sitemap:** don't generate a `sitemap.xml` or submit the site to search consoles.

Don't add `Disallow: /` to `robots.txt`. A crawler that is blocked from fetching a page never sees its noindex header or tag, so the URL can still show up in results. If you add a `robots.txt`, leave crawling allowed.
