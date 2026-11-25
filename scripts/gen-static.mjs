#!/usr/bin/env node
// 预渲染静态页：每篇文章每个语言版一个 index.html，外加首页文章列表、sitemap.xml、feed.xml。
//
// 用法：node scripts/gen-posts.mjs && node scripts/gen-static.mjs
//
// 读 posts.json（文章清单与顺序）和 posts/<dir>/index[.<lang>].md（正文），
// 用 marked 在构建时渲染正文，让不跑 JS 的爬虫也能读到文章。
// 产出：posts/<dir>/index.html、posts/<dir>/<lang>/index.html、
//       index.html 中 <!-- posts:start --> 与 <!-- posts:end --> 之间的列表、sitemap.xml、feed.xml。
// 幂等：内容没变就不写文件。由 .github/workflows/build-posts.yml 在 push 时自动跑并提交。

import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { marked } from 'marked';
import { splitFrontmatter } from './frontmatter.mjs';

const ROOT = process.cwd();
const POSTS = 'posts';
const SITE = 'https://blog.zosc.com';
const SITE_NAME = 'zosc blog';
const OG_DEFAULT = 'https://zosc.com/media/images/common/brand/og-default.png';
const FEED_SUBTITLE = 'The blog of zosc — self-hosting, AI, motion tools and experiments. zosc 的博客。';
const AUTHOR = { '@type': 'Person', '@id': 'https://zosc.com/#person', name: 'zosc', url: 'https://zosc.com/' };
const PUBLISHER = { '@type': 'Organization', '@id': 'https://zosc.com/#organization', name: 'zosc', url: 'https://zosc.com/' };

const HREFLANG = { en: 'en', zh: 'zh-CN' };
const LANG_LABEL = { en: 'English', zh: '中文', 'zh-CN': '中文', ja: '日本語' };
const STR = {
  en: { back: '← Back to posts', older: '← Older', newer: 'Newer →',
        footer: 'Plain Markdown · no build · push to publish.', theme: 'Light', themeLabel: 'Switch to light mode' },
  zh: { back: '← 返回列表', older: '← 更早', newer: '更新 →',
        footer: '纯 Markdown · 免构建 · push 即发布。', theme: '亮色', themeLabel: '切换到亮色模式' },
};
const t = (k, lang) => (STR[lang] && STR[lang][k]) || STR.en[k];

const normalizeLang = code => (code === 'zh-CN' ? 'zh' : code);
const hreflang = code => HREFLANG[code] || code;

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
function escapeXml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[c]));
}
const jsonLd = obj => JSON.stringify(obj).replace(/</g, '\\u003c');

async function writeIfChanged(rel, content) {
  const file = path.join(ROOT, rel);
  let old = null;
  try { old = await readFile(file, 'utf8'); } catch {}
  if (old === content) return false;
  await mkdir(path.dirname(file), { recursive: true });
  await writeFile(file, content);
  return true;
}

// 每篇的语言版本：主语言（index.md）在前，译文（index.<code>.md，需在 localized 里出现）在后
function postVersions(post) {
  const primary = normalizeLang(post.lang || 'en');
  const versions = [{ code: primary, file: 'index.md', urlPath: `/${POSTS}/${post.dir}/`, primary: true }];
  for (const code of post.translations || []) {
    const c = normalizeLang(code);
    if (c === primary || !(post.localized || {})[code]) continue;
    versions.push({ code: c, file: `index.${code}.md`, urlPath: `/${POSTS}/${post.dir}/${c}/`, primary: false, key: code });
  }
  return versions;
}

function versionFor(post, lang) {
  const versions = postVersions(post);
  return versions.find(v => v.code === lang) || versions[0];
}

function postView(post, lang) {
  const v = versionFor(post, lang);
  const loc = v.primary ? null : post.localized[v.key];
  return {
    title: (loc && loc.title) || post.title,
    listTitle: (loc && (loc.short_title || loc.title)) || post.short_title || post.title,
    summary: (loc && loc.summary) || post.summary || '',
    tags: loc && loc.tags && loc.tags.length ? loc.tags : (post.tags || []),
  };
}

function coverPath(post) {
  const cover = post.cover || '';
  if (!cover) return '';
  if (/^(https?:|\/\/|\/|data:)/.test(cover)) return cover;
  return `/${POSTS}/${post.dir}/${cover}`;
}
const absUrl = p => (/^(https?:)?\/\//.test(p) ? p : SITE + p);

// 对应 app.js 原先的 fixRelativeUrls：相对媒体与链接改为文章目录下的根绝对路径
function fixRelativeUrls(html, base) {
  const isRelative = v => v && !/^(https?:|\/\/|\/|#|data:|blob:)/.test(v);
  const getAttr = (tag, name) => {
    const m = tag.match(new RegExp(`\\s${name}="([^"]*)"`));
    return m ? m[1] : null;
  };
  const setAttr = (tag, name, value) => tag.replace(new RegExp(`(\\s${name}=")[^"]*(")`), (_, a, b) => a + value + b);
  const addAttr = (tag, attrs) => tag.replace(/\s*(\/?)>$/, ` ${attrs}$1>`);
  return html.replace(/<(img|video|audio|source|a)\b[^>]*>/g, (tag, name) => {
    if (name === 'a') {
      const href = getAttr(tag, 'href');
      if (href && !/^(https?:|\/\/|\/|#|mailto:)/.test(href)) tag = setAttr(tag, 'href', base + href);
      if (/^https?:/.test(getAttr(tag, 'href') || '') && getAttr(tag, 'target') === null) {
        tag = addAttr(tag, 'target="_blank" rel="noopener"');
      }
      return tag;
    }
    const src = getAttr(tag, 'src');
    if (isRelative(src)) tag = setAttr(tag, 'src', base + src);
    if (name === 'video') {
      const poster = getAttr(tag, 'poster');
      if (isRelative(poster)) tag = setAttr(tag, 'poster', base + poster);
    }
    if (name === 'img' && getAttr(tag, 'loading') === null) tag = addAttr(tag, 'loading="lazy"');
    return tag;
  });
}

function renderBody(md, base) {
  const html = marked.parse(md).replace(/<!--[\s\S]*?-->\n?/g, '');
  return fixRelativeUrls(html, base).trim();
}

function themeInitScript() {
  return `<script>
    (() => {
      try {
        const theme = localStorage.getItem('theme');
        if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme;
      } catch (e) {}
    })();
  </script>`;
}

function renderPostPage(post, version, versions, posts, index, bodyHtml) {
  const lang = version.code;
  const view = postView(post, lang);
  const url = SITE + version.urlPath;
  const primaryUrl = SITE + versions[0].urlPath;
  const cover = coverPath(post);
  const image = cover ? absUrl(cover) : OG_DEFAULT;
  const title = `${view.title} · ${SITE_NAME}`;

  const alternates = versions
    .map(v => `  <link rel="alternate" hreflang="${hreflang(v.code)}" href="${SITE + v.urlPath}">`)
    .concat(`  <link rel="alternate" hreflang="x-default" href="${primaryUrl}">`)
    .join('\n');

  const ld = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: view.title,
    description: view.summary,
    datePublished: post.date,
    inLanguage: hreflang(lang),
    image,
    url,
    mainEntityOfPage: { '@type': 'WebPage', '@id': url },
    author: AUTHOR,
    publisher: PUBLISHER,
    isPartOf: { '@id': `${SITE}/#blog` },
  };

  const switcher = versions.length < 2 ? '' : `<div class="lang-switch">` + versions.map(v =>
    `<a data-lang="${v.code}" class="${v.code === lang ? 'active' : ''}" href="${v.urlPath}" hreflang="${hreflang(v.code)}">${LANG_LABEL[v.code] || v.code}</a>`
  ).join('') + '</div>';

  const older = posts[index + 1] || null;
  const newer = index > 0 ? posts[index - 1] : null;
  const cell = (p, side, label) => p
    ? `<a class="${side}" href="${versionFor(p, lang).urlPath}"><span class="post-nav-label">${label}</span><span class="post-nav-title">${escapeHtml(postView(p, lang).listTitle)}</span></a>`
    : `<span class="${side}"></span>`;
  const nav = older || newer
    ? `<nav class="post-nav">${cell(older, 'prev', t('older', lang))}${cell(newer, 'next', t('newer', lang))}</nav>`
    : '';

  return `<!DOCTYPE html>
<html lang="${hreflang(lang)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <meta name="description" content="${escapeHtml(view.summary)}">
  <link rel="canonical" href="${url}">
${alternates}
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="${SITE_NAME}">
  <meta property="og:title" content="${escapeHtml(view.title)}">
  <meta property="og:description" content="${escapeHtml(view.summary)}">
  <meta property="og:url" content="${url}">
  <meta property="og:image" content="${escapeHtml(image)}">
  <meta property="article:published_time" content="${escapeHtml(post.date)}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="author" href="https://zosc.com/">
  <link rel="alternate" type="application/atom+xml" title="${SITE_NAME}" href="/feed.xml">
  <script type="application/ld+json">${jsonLd(ld)}</script>
  ${themeInitScript()}
  <link rel="icon" href="/assets/brand/zosc-mark-32.png" sizes="32x32" type="image/png">
  <link rel="icon" href="/assets/brand/zosc-mark-192.png" sizes="192x192" type="image/png">
  <link rel="apple-touch-icon" href="/assets/brand/zosc-mark-180.png">
  <link id="hljs-light" rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/styles/github.min.css" media="not all">
  <link id="hljs-dark" rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/styles/github-dark.min.css" media="all">
  <link rel="preload" href="/assets/fonts/montserrat-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/assets/fonts/mulish-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
  <header class="site-header">
    <a class="brand" href="/" aria-label="zosc blog home">
      <img class="brand-mark" src="/assets/brand/zosc-mark-32.png" alt="" width="24" height="24">
      <span>zosc&nbsp;blog</span>
    </a>
    <nav class="site-nav">
      <a class="nav-site" href="https://zosc.com/#code">Code</a>
      <a class="nav-site" href="https://zosc.com/#motion">Motion</a>
      <a class="nav-site" href="https://zosc.com/#visual">Visual</a>
      <a class="nav-site" href="https://zosc.com/about/">About</a>
      <a class="nav-site" href="/" aria-current="page">Blog</a>
      <a class="nav-home" href="https://zosc.com/" rel="author">zosc.com</a>
      <button class="theme-toggle" type="button" data-theme-toggle aria-label="${t('themeLabel', lang)}">${t('theme', lang)}</button>
    </nav>
  </header>

  <main id="app"><article class="post" data-giscus-term="${escapeHtml(post.dir)}"><a class="back" href="/">${t('back', lang)}</a>${switcher}<div class="post-body">
${bodyHtml}
</div>${nav}</article></main>

  <footer class="site-footer">
    © <span id="year"></span> <a href="https://zosc.com/" rel="author">zosc</a> · <a href="https://x.com/byzosc" rel="me">X</a> · <a href="https://github.com/byzosc" rel="me">GitHub</a> · <span id="tagline">${t('footer', lang)}</span> · <a href="https://github.com/byzosc/zero-build-blog" target="_blank" rel="noopener">zero-build-blog</a>
  </footer>

  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11/build/highlight.min.js"></script>
  <script src="/assets/app.js"></script>
</body>
</html>
`;
}

// 结构照抄 app.js 的 renderList（默认语言 en）
function renderList(posts, lang = 'en') {
  const found = new Set();
  posts.forEach(p => postVersions(p).forEach(v => found.add(v.code)));
  const ordered = ['en', 'zh'].filter(c => found.has(c));
  const langs = ordered.concat([...found].filter(c => !ordered.includes(c)));
  const switcher = langs.length < 2 ? '' : `<div class="lang-switch list-lang-switch">` + langs.map(code =>
    `<button data-lang="${code}" class="${code === lang ? 'active' : ''}">${LANG_LABEL[code] || code}</button>`
  ).join('') + '</div>';
  const copy = lang === 'zh'
    ? { kicker: 'zosc 的笔记', title: '最新文章' }
    : { kicker: "zosc's notebook", title: 'Recent writing' };
  const items = posts.map(p => {
    const view = postView(p, lang);
    const cover = coverPath(p);
    const tagLabel = view.tags.length ? view.tags[0] : 'note';
    return `
      <li class="post-card${cover ? ' has-cover' : ''}">
        <a class="post-card-link" href="${versionFor(p, lang).urlPath}">
          ${cover
            ? `<img class="post-card-visual post-card-cover" src="${escapeHtml(cover)}" alt="" loading="lazy">`
            : `<div class="post-card-visual post-card-fallback" aria-hidden="true"><span>Z</span><small>${escapeHtml(tagLabel)}</small></div>`}
          <div class="post-card-body">
            <h2>${escapeHtml(view.listTitle)}</h2>
            <div class="post-meta">${escapeHtml(p.date)}${view.tags.length ? ' · ' + view.tags.map(escapeHtml).join(' / ') : ''}</div>
            ${view.summary ? `<p class="post-summary">${escapeHtml(view.summary)}</p>` : ''}
          </div>
        </a>
      </li>`;
  }).join('');
  return `<section class="list-hero">
        <div>
          <p class="list-kicker">${escapeHtml(copy.kicker)}</p>
          <h1>${escapeHtml(copy.title)}</h1>
        </div>
        ${switcher}
      </section>
      <ul class="post-list">${items}</ul>`;
}

function renderSitemap(posts, latest) {
  const urls = [`  <url>\n    <loc>${SITE}/</loc>${latest ? `\n    <lastmod>${latest}</lastmod>` : ''}\n  </url>`];
  for (const post of posts) {
    const versions = postVersions(post);
    const links = versions.length < 2 ? [] : versions
      .map(v => `    <xhtml:link rel="alternate" hreflang="${hreflang(v.code)}" href="${SITE + v.urlPath}"/>`)
      .concat(`    <xhtml:link rel="alternate" hreflang="x-default" href="${SITE + versions[0].urlPath}"/>`);
    for (const v of versions) {
      urls.push(`  <url>\n    <loc>${SITE + v.urlPath}</loc>${post.date ? `\n    <lastmod>${escapeXml(post.date)}</lastmod>` : ''}${links.length ? '\n' + links.join('\n') : ''}\n  </url>`);
    }
  }
  return `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls.join('\n')}
</urlset>
`;
}

// Atom 要求完整时间戳；frontmatter 只有日期，按 UTC 零点
const atomDate = d => (/^\d{4}-\d{2}-\d{2}$/.test(d) ? `${d}T00:00:00Z` : d);

function renderFeed(posts, latest) {
  const entries = posts.map(post => {
    const url = SITE + postVersions(post)[0].urlPath;
    const date = atomDate(post.date);
    return `  <entry>
    <title>${escapeXml(post.title)}</title>
    <link rel="alternate" type="text/html" href="${url}"/>
    <id>${url}</id>
    <published>${date}</published>
    <updated>${date}</updated>
    <summary>${escapeXml(post.summary || '')}</summary>
  </entry>`;
  });
  return `<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>${SITE_NAME}</title>
  <subtitle>${escapeXml(FEED_SUBTITLE)}</subtitle>
  <link rel="alternate" type="text/html" href="${SITE}/"/>
  <link rel="self" type="application/atom+xml" href="${SITE}/feed.xml"/>
  <id>${SITE}/</id>
  <updated>${atomDate(latest)}</updated>
  <author>
    <name>zosc</name>
    <uri>https://zosc.com/</uri>
  </author>
${entries.join('\n')}
</feed>
`;
}

const posts = JSON.parse(await readFile(path.join(ROOT, 'posts.json'), 'utf8'));
const latest = posts.reduce((max, p) => (String(p.date) > max ? String(p.date) : max), '');
const changed = [];

for (const [i, post] of posts.entries()) {
  const versions = postVersions(post);
  const base = `/${POSTS}/${post.dir}/`;
  for (const v of versions) {
    const md = await readFile(path.join(ROOT, POSTS, post.dir, v.file), 'utf8');
    const body = renderBody(splitFrontmatter(md).body, base);
    const rel = path.join(v.urlPath.slice(1), 'index.html');
    if (await writeIfChanged(rel, renderPostPage(post, v, versions, posts, i, body))) changed.push(rel);
  }
}

const indexHtml = await readFile(path.join(ROOT, 'index.html'), 'utf8');
const marker = /(<!-- posts:start -->)[\s\S]*?(<!-- posts:end -->)/;
if (!marker.test(indexHtml)) throw new Error('index.html 缺少 <!-- posts:start --> / <!-- posts:end --> 标记');
const nextIndex = indexHtml.replace(marker, (_, a, b) => `${a}${renderList(posts)}${b}`);
if (await writeIfChanged('index.html', nextIndex)) changed.push('index.html');
if (await writeIfChanged('sitemap.xml', renderSitemap(posts, latest))) changed.push('sitemap.xml');
if (await writeIfChanged('feed.xml', renderFeed(posts, latest))) changed.push('feed.xml');

console.log(`静态页已生成：${posts.length} 篇；本次改动 ${changed.length} 个文件`);
for (const f of changed) console.log('  ' + f);
