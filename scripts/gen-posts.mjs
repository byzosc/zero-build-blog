#!/usr/bin/env node
// 生成静态文章清单 posts.json（零依赖，Node 原生）。
//
// 用法：node scripts/gen-posts.mjs
//
// 扫描 posts/<slug>/index.md 的 frontmatter（title / date / summary / tags），
// 按日期倒序写出根目录 posts.json。首页引擎优先读它 —— 不调用 GitHub API，
// 因此不会再撞匿名接口的限流（每小时 60 次/IP，会导致首页 403）。
//
// 由 .github/workflows/build-posts.yml 在每次 push 时自动跑并提交，作者照常只管 push。

import { access, readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { normalizeList, parseDir, parseFrontmatter } from './frontmatter.mjs';

const ROOT = process.cwd();
const POSTS = 'posts';

async function exists(file) {
  try {
    await access(file);
    return true;
  } catch {
    return false;
  }
}

let entries;
try {
  entries = await readdir(path.join(ROOT, POSTS), { withFileTypes: true });
} catch {
  entries = [];
}

const posts = [];
for (const e of entries) {
  if (!e.isDirectory()) continue;
  let md;
  try {
    md = await readFile(path.join(ROOT, POSTS, e.name, 'index.md'), 'utf8');
  } catch {
    continue;
  }
  const fm = parseFrontmatter(md);
  const { date, slug } = parseDir(e.name);
  const translations = normalizeList(fm.translations);
  const localized = {};
  for (const code of translations) {
    try {
      const lmd = await readFile(path.join(ROOT, POSTS, e.name, `index.${code}.md`), 'utf8');
      const lfm = parseFrontmatter(lmd);
      localized[code] = {
        title: lfm.title || '',
        short_title: lfm.short_title || '',
        summary: lfm.summary || '',
        tags: normalizeList(lfm.tags),
      };
    } catch {
      // A declared translation can be added later; keep the index usable meanwhile.
    }
  }
  const cover = fm.cover || ((await exists(path.join(ROOT, POSTS, e.name, 'cover.png'))) ? 'cover.png' : '');
  posts.push({
    dir: e.name,
    title: fm.title || slug,
    short_title: fm.short_title || '',
    date: fm.date || date,
    summary: fm.summary || '',
    tags: normalizeList(fm.tags),
    cover,
    lang: fm.lang || 'en',
    translations,
    localized,
  });
}

posts.sort((a, b) => String(b.date).localeCompare(String(a.date)));

await writeFile(path.join(ROOT, 'posts.json'), JSON.stringify(posts, null, 2) + '\n');
console.log(`posts.json 已生成：${posts.length} 篇`);
