// Isolated local Chrome QA; no user profile, server, or network dependencies.
import {createRequire} from 'node:module';
import {readFile, mkdir, writeFile, access} from 'node:fs/promises';
import {resolve, dirname, relative} from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const deps=process.env.ENCLOSURE_QA_DEPENDENCIES;
if(!deps) throw Error('Set ENCLOSURE_QA_DEPENDENCIES to the installed Node dependency root.');
const {chromium}=createRequire(resolve(deps,'package.json'))('playwright');
const out=resolve(root,'openspec/changes/diagnose-enclosure-lqr-20261019/artifacts/reporting/html_qa');
await mkdir(out,{recursive:true});
const files=['docs/reports/professor_weekly_2026-10-19_zh.html','docs/papers/conference_review_2026-10-19/manuscript_zh.html'];
const receipt={status:'PASS',mode:'isolated Chrome; offline file URLs',files:[],checks:[],errors:[]};
const browser=await chromium.launch({executablePath:process.env.ENCLOSURE_CHROME_PATH||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try {
  const context=await browser.newContext({offline:true,deviceScaleFactor:1});
  await context.route(/^https?:/,route=>route.abort());
  for(const [i,file] of files.entries()) {
    const path=resolve(root,file),url=pathToFileURL(path).href;
    const page=await context.newPage();
    page.on('pageerror',e=>receipt.errors.push(String(e)));
    page.on('console',m=>{if(m.type()==='error')receipt.errors.push(m.text());});
    const hash=createHash('sha256').update(await readFile(path)).digest('hex');
    receipt.files.push({path:file,sha256:hash});
    for(const width of [1440,820,390]) {
      await page.setViewportSize({width,height:1000});
      await page.goto(url);await page.evaluate(()=>document.fonts.ready);
      const state=await page.evaluate(()=>({
        title:document.title,overflow:document.documentElement.scrollWidth>innerWidth,
        tables:document.querySelectorAll('table').length,
        math:[...document.querySelectorAll('math')].map(m=>({width:m.getBoundingClientRect().width,height:m.getBoundingClientRect().height})),
        links:[...document.querySelectorAll('a[href]')].map(a=>a.href),
        brokenFragments:[...document.querySelectorAll('a[href^="#"]')].map(a=>a.hash.slice(1)).filter(id=>!document.getElementById(id)),
        brokenImages:[...document.images].filter(im=>!im.complete||!im.naturalWidth).length,
        rawTex:/\\\(|\\\[|\$\$/.test(document.body.innerText),
      }));
      if(state.overflow||state.brokenFragments.length||state.rawTex||state.brokenImages)throw Error(JSON.stringify({file,width,state}));
      if(i===1 && (state.math.length!==3||state.math.some(m=>m.height<10)))throw Error('Missing MathML');
      const wrapper=page.locator('.table-wrap').first();await wrapper.focus();
      const before=await wrapper.evaluate(e=>e.scrollLeft);
      await page.keyboard.press('ArrowRight');await page.waitForTimeout(150);
      const after=await wrapper.evaluate(e=>e.scrollLeft);
      if(width===390&&after<=before)throw Error('Keyboard table scrolling failed');
      await wrapper.evaluate(e=>e.scrollLeft=0);
      await page.evaluate(()=>window.scrollTo(0,0));
      const shot=`${i===0?'weekly':'paper'}-${width}.png`;
      await page.screenshot({path:resolve(out,shot),fullPage:true});
      await page.screenshot({path:resolve(out,shot.replace('.png','-top.png'))});
      if(i===1)await page.locator('.math').screenshot({path:resolve(out,`formulas-${width}.png`)});
      else {await page.locator('#results').screenshot({path:resolve(out,`comparison-${width}.png`)});await page.locator('#diagnostic').screenshot({path:resolve(out,`diagnostic-${width}.png`)});}
      let diagnosticInteractions=null;
      if(i===0) {
        const detail=page.locator('#diagnostic details');
        await detail.locator('summary').click();
        if(!await detail.evaluate(e=>e.open))throw Error('Diagnostic details failed to open');
        await detail.screenshot({path:resolve(out,`diagnostic-pairs-${width}.png`)});
        const chart=page.locator('.figure-wrap').first();await chart.focus();
        const chartBefore=await chart.evaluate(e=>e.scrollLeft);
        await page.keyboard.press('ArrowRight');await page.waitForTimeout(150);
        const chartAfter=await chart.evaluate(e=>e.scrollLeft);
        if(width===390&&chartAfter<=chartBefore)throw Error('Chart keyboard scrolling failed');
        diagnosticInteractions={detailsOpened:true,chartKeyboardScroll:chartAfter>chartBefore};
        await chart.evaluate(e=>e.scrollLeft=0);
        await detail.locator('summary').click();
      }
      receipt.checks.push({file,width,...state,keyboardScroll:after>before,diagnosticInteractions,screenshot:shot});
      if(width===1440) {
        for(const link of state.links.filter(x=>x.startsWith('file:'))) {
          const u=new URL(link),fragment=decodeURIComponent(u.hash.slice(1));u.hash='';
          const target=fileURLToPath(u);await access(target);
          if(fragment && target.endsWith('.html')) {
            const html=await readFile(target,'utf8');
            if(!html.includes(`id="${fragment}"`)&&!html.includes(`id='${fragment}'`))throw Error(`Missing anchor ${link}`);
          }
        }
      }
    }
    await page.emulateMedia({media:'print'});
    await page.setViewportSize({width:794,height:1123});
    await page.evaluate(()=>window.scrollTo(0,0));
    await page.waitForTimeout(100);
    await page.screenshot({path:resolve(out,`${i===0?'weekly':'paper'}-print-top.png`)});
    await page.screenshot({path:resolve(out,`${i===0?'weekly':'paper'}-print.png`),fullPage:true});
    const printOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
    if(printOverflow)throw Error(`Print overflow: ${file}`);
    receipt.checks.push({file,media:'print',overflow:printOverflow});
    await page.close();
  }
  if(receipt.errors.length)throw Error(JSON.stringify(receipt.errors));
} catch(error) {receipt.status='FAIL';receipt.errors.push(String(error));}
finally {await browser.close();}
await writeFile(resolve(out,'receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({status:receipt.status,files:receipt.files,checks:receipt.checks.length,errors:receipt.errors}));
if(receipt.status!=='PASS')process.exitCode=1;
