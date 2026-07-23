#!/usr/bin/env node
/**
 * Generate hook title PNG from input.json + style.json.
 * Usage: node gen_hook.js <input.json> <style.json> <output.png>
 */
const { chromium } = require('playwright');
const fs = require('fs');

async function main() {
  const [inputPath, stylePath, outputPath] = process.argv.slice(2);
  if (!inputPath || !stylePath || !outputPath) {
    console.error('Usage: node gen_hook.js <input.json> <style.json> <output.png>');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));
  const style = JSON.parse(fs.readFileSync(stylePath, 'utf-8'));
  const h = style.hook;
  const hook = data.hook;

  // Replace accent word with colored span
  const enHtml = hook.en.replace(hook.accent, `<span class="accent">${hook.accent}</span>`);

  const html = `<style>
    * { margin:0; padding:0; box-sizing:border-box }
    body { background:transparent }
    .hook { background:${h.bg}; border-radius:${h.radius}px; padding:${h.padding}; display:inline-block }
    .hook-text { color:${h.color}; font-size:${h.size}px; font-weight:bold; font-family:${h.font}; letter-spacing:1px }
    .hook-text .accent { color:${h.accent_color} }
  </style>
  <div class="hook"><span class="hook-text">${enHtml} — ${hook.zh}</span></div>`;

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1000, height: 200 } });
  await page.setContent(html);
  await page.waitForTimeout(300);
  const el = await page.$('div.hook');
  await el.screenshot({ path: outputPath, omitBackground: true });
  await browser.close();
  console.log('✅ Hook PNG generated');
}

main().catch(e => { console.error(e); process.exit(1); });
