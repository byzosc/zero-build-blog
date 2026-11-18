// gen-posts.mjs 与 gen-static.mjs 共用的 frontmatter 解析。
// 与引擎 app.js 的 parseFrontmatter 保持一致：按第一个冒号切，去掉首尾引号，tags 支持 [a, b]

export function splitFrontmatter(md) {
  const src = md.replace(/^\uFEFF/, '');
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---[ \t]*(?:\r?\n|$)([\s\S]*)$/);
  if (!m) return { meta: {}, body: src };
  const meta = {};
  for (const line of m[1].split(/\r?\n/)) {
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

export function parseFrontmatter(md) {
  return splitFrontmatter(md).meta;
}

export function parseDir(name) {
  const m = name.match(/^(\d{4}-\d{2}-\d{2})-(.+)$/);
  return m ? { date: m[1], slug: m[2] } : { date: '', slug: name };
}

export function normalizeList(value) {
  return Array.isArray(value) ? value : value ? [value] : [];
}
