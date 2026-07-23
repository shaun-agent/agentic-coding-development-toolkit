#!/usr/bin/env node
/**
 * Generate learning card PNGs from input.json + style.json.
 * Groups cards by seg_index (same segment = one PNG).
 * Usage: node gen_cards.js <input.json> <style.json> <output_dir>
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const [inputPath, stylePath, outputDir] = process.argv.slice(2);
  if (!inputPath || !stylePath || !outputDir) {
    console.error('Usage: node gen_cards.js <input.json> <style.json> <output_dir>');
    process.exit(1);
  }

  const data = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));
  const style = JSON.parse(fs.readFileSync(stylePath, 'utf-8'));
  fs.mkdirSync(outputDir, { recursive: true });

  // Group cards by seg_index
  const groups = {};
  for (const card of data.cards) {
    const key = card.seg_index;
    if (!groups[key]) groups[key] = [];
    groups[key].push(card);
  }

  const sortedKeys = Object.keys(groups).map(Number).sort((a, b) => a - b);
  const s = style.card;
  const sw = style.card_word;
  const sz = style.card_zh;
  const sr = style.card_row;
  const sl = style.card_label;

  const browser = await chromium.launch();

  for (let i = 0; i < sortedKeys.length; i++) {
    const items = groups[sortedKeys[i]];
    const cardsHtml = items.map(item => {
      const title = item.type === 'pattern' ? item.title : item.highlight;
      return `
      <div class="card">
        <div><span class="word">${title}</span><span class="zh">${item.zh}</span></div>
        <div class="row"><span class="label">用法：</span>${item.usage}</div>
        <div class="row"><span class="label">例句：</span>${item.example}</div>
      </div>
    `}).join('');

    const html = `<style>
      * { margin:0; padding:0; box-sizing:border-box }
      body { background:transparent }
      .wrap { display:inline-block }
      .card { background:${s.bg}; border-radius:${s.radius}px; padding:${s.padding}; width:${s.max_width}px }
      .card + .card { margin-top:12px }
      .word { color:${sw.color}; font-size:${sw.size}px; font-weight:bold; font-family:${sw.font}; display:inline }
      .zh { color:${sz.color}; font-size:${sz.size}px; margin-left:8px; font-family:${sz.font}; display:inline }
      .row { margin-top:8px; color:${sr.color}; font-size:${sr.size}px; line-height:1.5; font-family:${sr.font} }
      .label { color:${sl.color}; font-size:${sl.size}px }
    </style><div class="wrap">${cardsHtml}</div>`;

    const page = await browser.newPage({ viewport: { width: 700, height: 500 } });
    await page.setContent(html);
    await page.waitForTimeout(300);
    const el = await page.$('div.wrap');
    await el.screenshot({ path: path.join(outputDir, `card_${i + 1}.png`), omitBackground: true });
    await page.close();
  }

  await browser.close();
  console.log(`✅ Generated ${sortedKeys.length} card PNGs`);
}

main().catch(e => { console.error(e); process.exit(1); });
