/* Zerb's Blog — 零构建博客引擎
 * 三个借鉴来的概念，自己重写、更简洁：
 *   1) GitHub Pages + 预渲染：CI 用 scripts/gen-static.mjs 把 posts/<dir>/index.md 渲染成静态页，本文件只管主题、列表和评论
 *   2) GitHub 做评论系统：用 Giscus（基于 GitHub Discussions）
 *   3) 文章列表自动生成：读 GitHub API 列出 posts/ 下的文件夹，无需手维护索引
 * 改仓库名后，只改下面 CONFIG.repo / giscus.repo 即可。 */
const CONFIG = {
  repo: 'byzosc/zero-build-blog',   // ← owner/repo，改名仓库后改这里
  branch: 'main',
  postsDir: 'posts',
  giscus: {
    repo: 'byzosc/zero-build-blog',
    repoId: 'R_kgDOTA_3bA',                 // data-repo-id
    category: 'Announcements',
    categoryId: 'DIC_kwDOTA_3bM4C_qMH',     // data-category-id（Announcements 分类）
  },
};

const app = document.getElementById('app');
document.getElementById('year').textContent = new Date().getFullYear();
// 文章页由 scripts/gen-static.mjs 预渲染，带 data-giscus-term；没有它就是首页
const postEl = document.querySelector('article.post[data-giscus-term]');
const postLang = postEl ? (document.documentElement.lang === 'zh-CN' ? 'zh' : 'en') : null;

// 站点 UI 文案：文章页跟随页面语言，首页跟随当前阅读语言（localStorage 'lang'，默认英文）
function currentLang() { return postLang || (localStorage.getItem('lang') === 'zh' ? 'zh' : 'en'); }
const THEME_KEY = 'theme';
// 2026-11-23: dark is the default whatever the system prefers — one look with zosc.com, which is
// dark only. A reader who picks light keeps it (localStorage).
function systemTheme() {
  return 'dark';
}
function savedTheme() {
  const theme = localStorage.getItem(THEME_KEY);
  return theme === 'light' || theme === 'dark' ? theme : '';
}
function currentTheme() {
  return savedTheme() || systemTheme();
}
const STR = {
  en: { loadingList: 'Loading posts…', empty: 'No posts yet.',
        listErr: 'Failed to load list: ', rate: 'If this is GitHub API rate limiting (60/hr for anonymous), just try again shortly.',
        footer: 'Plain Markdown · no build · push to publish.' },
  zh: { loadingList: '加载文章列表…', empty: '还没有文章。',
        listErr: '列表加载失败：', rate: '若是 GitHub API 限流（匿名每小时 60 次），稍后再试即可。',
        footer: '纯 Markdown · 免构建 · push 即发布。' },
};
function t(k, lang = currentLang()) { return (STR[lang] && STR[lang][k]) || STR.en[k] || k; }
function applyChrome(lang) {
  const f = document.getElementById('tagline'); if (f) f.textContent = t('footer', lang);
  document.documentElement.lang = (lang || currentLang()) === 'zh' ? 'zh-CN' : 'en';
  updateThemeToggleLabel(currentTheme(), lang || currentLang());
}

function updateHighlightTheme(theme) {
  const light = document.getElementById('hljs-light');
  const dark = document.getElementById('hljs-dark');
  if (!light || !dark) return;
  light.media = theme === 'light' ? 'all' : 'not all';
  dark.media = theme === 'dark' ? 'all' : 'not all';
}

function updateGiscusTheme(theme) {
  const frame = document.querySelector('iframe.giscus-frame');
  if (!frame || !frame.contentWindow) return;
  frame.contentWindow.postMessage({ giscus: { setConfig: { theme } } }, 'https://giscus.app');
}

function updateThemeToggleLabel(theme, lang = currentLang()) {
  const button = document.querySelector('[data-theme-toggle]');
  if (!button) return;
  const next = theme === 'dark' ? 'light' : 'dark';
  button.textContent = lang === 'zh'
    ? (next === 'dark' ? '暗色' : '亮色')
    : (next === 'dark' ? 'Dark' : 'Light');
  button.setAttribute('aria-label', lang === 'zh'
    ? `切换到${next === 'dark' ? '暗色' : '亮色'}模式`
    : `Switch to ${next} mode`);
  button.setAttribute('title', button.getAttribute('aria-label'));
}

function applyTheme(theme = currentTheme()) {
  document.documentElement.dataset.theme = theme;
  updateHighlightTheme(theme);
  updateThemeToggleLabel(theme);
  updateGiscusTheme(theme);
}

function setupThemeToggle() {
  applyTheme();
  const button = document.querySelector('[data-theme-toggle]');
  if (button) {
    button.addEventListener('click', () => {
      const next = currentTheme() === 'dark' ? 'light' : 'dark';
      localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
    });
  }
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (!savedTheme()) applyTheme(systemTheme());
    });
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

// 解析 YAML frontmatter（只需支持简单 key: value 与 tags: [a, b]）
function parseFrontmatter(md) {
  const m = md.match(/^---\s*\n([\s\S]*?)\n---\s*\n?([\s\S]*)$/);
  if (!m) return { meta: {}, body: md };
  const meta = {};
  for (const line of m[1].split('\n')) {
    const i = line.indexOf(':');
    if (i === -1) continue;
    const key = line.slice(0, i).trim();
    let val = line.slice(i + 1).trim();
    if (val.startsWith('[') && val.endsWith(']')) {
      val = val.slice(1, -1).split(',').map(s => s.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
    } else {
      val = val.replace(/^["']|["']$/g, '');
    }
    meta[key] = val;
  }
  return { meta, body: m[2] };
}

// "2026-06-21-some-slug" -> { date, slug }
function parseDir(name) {
  const m = name.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
  return m ? { date: m[1], slug: m[2] } : { date: '', slug: name };
}

async function fetchText(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(url.split('/').pop() + ' → ' + r.status);
  return r.text();
}

async function listPosts() {
  // 首选：静态 posts.json（push 时由 GitHub Action 生成）——不调用 GitHub API，永不被限流
  try {
    const r0 = await fetch('posts.json', { cache: 'no-cache' });
    if (r0.ok) {
      const list = await r0.json();
      if (Array.isArray(list)) {
        try { localStorage.setItem('postsCache', JSON.stringify(list)); } catch (e) {}
        return list;
      }
    }
  } catch (e) { /* 没有 posts.json：退回 GitHub API */ }

  try {
    const api = `https://api.github.com/repos/${CONFIG.repo}/contents/${CONFIG.postsDir}?ref=${CONFIG.branch}`;
    const r = await fetch(api, { headers: { Accept: 'application/vnd.github+json' } });
    if (!r.ok) throw new Error('GitHub API ' + r.status);
    const items = await r.json();
    const dirs = items.filter(it => it.type === 'dir').map(it => it.name);
    const posts = await Promise.all(dirs.map(async name => {
      const { date, slug } = parseDir(name);
      let meta = {};
      try { meta = parseFrontmatter(await fetchText(`${CONFIG.postsDir}/${name}/index.md`)).meta; } catch (e) {}
      const translations = Array.isArray(meta.translations) ? meta.translations
                         : (meta.translations ? [meta.translations] : []);
      const localized = {};
      await Promise.all(translations.map(async code => {
        try {
          const lmeta = parseFrontmatter(await fetchText(`${CONFIG.postsDir}/${name}/index.${code}.md`)).meta;
          localized[code] = {
            title: lmeta.title || '',
            short_title: lmeta.short_title || '',
            summary: lmeta.summary || '',
            tags: Array.isArray(lmeta.tags) ? lmeta.tags : (lmeta.tags ? [lmeta.tags] : []),
          };
        } catch (e) {}
      }));
      return {
        dir: name,
        title: meta.title || slug,
        short_title: meta.short_title || '',
        date: meta.date || date,
        summary: meta.summary || '',
        tags: Array.isArray(meta.tags) ? meta.tags : [],
        cover: meta.cover || '',
        lang: meta.lang || 'en',
        translations,
        localized,
      };
    }));
    posts.sort((a, b) => String(b.date).localeCompare(String(a.date)));
    try { localStorage.setItem('postsCache', JSON.stringify(posts)); } catch (e) {}
    return posts;
  } catch (e) {
    // API 限流（匿名每小时 60 次）或网络失败时，回退到上次成功加载的列表，避免首页报错
    const cached = localStorage.getItem('postsCache');
    if (cached) { try { return JSON.parse(cached); } catch (_) {} }
    throw e;
  }
}

let _postsCache = null;
// 列表缓存：同一会话里重复渲染列表时复用，省 GitHub API 调用（匿名每小时 60 次）。
async function getPosts() {
  if (!_postsCache) _postsCache = await listPosts();
  return _postsCache;
}

function normalizeLang(code) {
  return code === 'zh-CN' ? 'zh' : code;
}

function postLangs(post) {
  const langs = new Set([normalizeLang(post.lang || 'en')]);
  (post.translations || []).forEach(code => langs.add(normalizeLang(code)));
  Object.keys(post.localized || {}).forEach(code => langs.add(normalizeLang(code)));
  return Array.from(langs);
}

function listLangs(posts) {
  const found = new Set();
  posts.forEach(post => postLangs(post).forEach(code => found.add(code)));
  const ordered = ['en', 'zh'].filter(code => found.has(code));
  return ordered.concat(Array.from(found).filter(code => !ordered.includes(code)));
}

function langSwitchHtml(langs, active, className = '') {
  if (langs.length < 2) return '';
  return `<div class="lang-switch ${className}">` + langs.map(code =>
    `<button data-lang="${code}" class="${code === active ? 'active' : ''}">${LANG_LABEL[code] || code}</button>`
  ).join('') + '</div>';
}

function listCopy(lang) {
  return lang === 'zh'
    ? { kicker: 'zosc 的笔记', title: '最新文章' }
    : { kicker: "zosc's notebook", title: 'Recent writing' };
}

function localizedMeta(post, lang) {
  const localized = post.localized || {};
  const normalized = normalizeLang(lang);
  return localized[lang] || localized[normalized] ||
    Object.entries(localized).find(([code]) => normalizeLang(code) === normalized)?.[1] || null;
}

function postListView(post, lang) {
  const localized = localizedMeta(post, lang);
  const tags = localized && localized.tags && localized.tags.length ? localized.tags : (post.tags || []);
  return {
    title: (localized && (localized.short_title || localized.title)) || post.short_title || post.title,
    summary: (localized && localized.summary) || post.summary || '',
    tags,
  };
}

function postCoverSrc(post) {
  const cover = post.cover || '';
  if (!cover) return '';
  if (/^(https?:|\/\/|\/|data:)/.test(cover)) return cover;
  return `${CONFIG.postsDir}/${post.dir}/${cover}`;
}

// 文章静态页网址：当前语言是 zh 且该文有 zh 版时指向 /posts/<dir>/zh/
function postHref(dir, post, lang = currentLang()) {
  const base = `/${CONFIG.postsDir}/${encodeURIComponent(dir)}/`;
  const primary = post ? normalizeLang(post.lang || 'en') : 'en';
  return post && lang !== primary && postLangs(post).includes(lang) ? `${base}${lang}/` : base;
}

async function renderList() {
  const lang = currentLang();
  applyChrome(lang);
  if (!app.querySelector('.post-list')) app.innerHTML = `<p class="state">${t('loadingList', lang)}</p>`;
  try {
    const posts = await getPosts();
    document.title = "zosc blog";
    if (!posts.length) { app.innerHTML = `<p class="empty">${t('empty', lang)}</p>`; return; }
    const langs = listLangs(posts);
    const copy = listCopy(lang);
    app.innerHTML = `<section class="list-hero">
        <div>
          <p class="list-kicker">${escapeHtml(copy.kicker)}</p>
          <h1>${escapeHtml(copy.title)}</h1>
        </div>
        ${langSwitchHtml(langs, lang, 'list-lang-switch')}
      </section>
      <ul class="post-list">` + posts.map(p => {
        const view = postListView(p, lang);
        const cover = postCoverSrc(p);
        const tagLabel = view.tags.length ? view.tags[0] : 'note';
        return `
      <li class="post-card${cover ? ' has-cover' : ''}">
        <a class="post-card-link" href="${postHref(p.dir, p, lang)}">
          ${cover
            ? `<img class="post-card-visual post-card-cover" src="${escapeHtml(cover)}" alt="" loading="lazy">`
            : `<div class="post-card-visual post-card-fallback" aria-hidden="true"><span>Z</span><small>${escapeHtml(tagLabel)}</small></div>`}
          <div class="post-card-body">
            <h2>${escapeHtml(view.title)}</h2>
            <div class="post-meta">${escapeHtml(p.date)}${view.tags.length ? ' · ' + view.tags.map(escapeHtml).join(' / ') : ''}</div>
            ${view.summary ? `<p class="post-summary">${escapeHtml(view.summary)}</p>` : ''}
          </div>
        </a>
      </li>`;
      }).join('') + '</ul>';
    app.querySelectorAll('.list-lang-switch button').forEach(btn =>
      btn.addEventListener('click', () => {
        localStorage.setItem('lang', btn.getAttribute('data-lang'));
        renderList();
      }));
    window.scrollTo(0, 0);
  } catch (e) {
    app.innerHTML = `<p class="error">${t('listErr', lang)}${escapeHtml(e.message)}</p>
      <p class="state"><small>${t('rate', lang)}</small></p>`;
  }
}

function mountGiscus(term) {
  const g = CONFIG.giscus;
  if (!g.repoId || !g.categoryId) return; // 还没配置就先不挂
  const wrap = document.createElement('div');
  wrap.className = 'giscus';
  app.appendChild(wrap);
  const s = document.createElement('script');
  s.src = 'https://giscus.app/client.js';
  const attrs = {
    'data-repo': g.repo, 'data-repo-id': g.repoId,
    'data-category': g.category, 'data-category-id': g.categoryId,
    'data-mapping': 'specific', 'data-term': term,
    'data-reactions-enabled': '1', 'data-emit-metadata': '0',
    'data-theme': currentTheme(), 'data-lang': currentLang() === 'zh' ? 'zh-CN' : 'en', 'data-loading': 'lazy',
  };
  for (const [k, v] of Object.entries(attrs)) s.setAttribute(k, v);
  s.crossOrigin = 'anonymous'; s.async = true;
  wrap.appendChild(s);
}

const LANG_LABEL = { en: 'English', zh: '中文', 'zh-CN': '中文', ja: '日本語' };

function setupPost() {
  if (window.hljs) hljs.highlightAll();
  postEl.querySelectorAll('.lang-switch a[data-lang]').forEach(a =>
    a.addEventListener('click', () => { try { localStorage.setItem('lang', a.getAttribute('data-lang')); } catch (e) {} }));
  mountGiscus(postEl.getAttribute('data-giscus-term'));
}

// 旧网址 #/post/<dir> 跳到静态页
async function router() {
  const m = location.hash.replace(/^#/, '').match(/^\/post\/(.+)$/);
  if (!m) return renderList();
  const dir = decodeURIComponent(m[1]);
  let post = null;
  try { post = (await getPosts()).find(p => p.dir === dir) || null; } catch (e) {}
  location.replace(postHref(dir, post));
}

setupThemeToggle();
applyChrome();
if (postEl) setupPost();
else {
  window.addEventListener('hashchange', router);
  router();
}
