import {createRequire} from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';

const root=fileURLToPath(new URL('../',import.meta.url));
const require=createRequire(path.join(process.env.ENCLOSURE_QA_DEPENDENCIES || process.cwd(),'package.json'));
const {chromium}=require('playwright');
const out=path.join(root,'docs/reports/qa/professor_comparison_2026-10-12');
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.ENCLOSURE_CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const results=[];
try {
  for(const stem of ['professor_comparison_2026-10-12_zh','conference_shortlist_2026-10-12_zh']) {
    const html=path.join(root,'docs/reports',stem+'.html');
    const page=await browser.newPage(); const errors=[],external=[];
    page.on('pageerror',e=>errors.push(String(e)));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    await page.route(/^https?:\/\//,r=>{external.push(r.request().url());return r.abort();});
    const record={artifact:path.relative(root,html),sha256:createHash('sha256').update(await fs.readFile(html)).digest('hex'),viewports:[],errors,external};
    for(const [name,width] of [['desktop',1440],['tablet',820],['mobile',390]]) {
      await page.setViewportSize({width,height:900});
      await page.goto(pathToFileURL(html).href); await page.evaluate(()=>document.fonts.ready);
      const geometry=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
      if(geometry.scroll>geometry.width)throw new Error(stem+': body overflow '+name);
      await page.screenshot({path:path.join(out,stem+'-'+name+'.png'),fullPage:true});
      await page.screenshot({path:path.join(out,stem+'-'+name+'-top.png')});
      if(stem.startsWith('conference')) {
        await page.getByRole('heading',{name:'CSME：近期最符合地區、語言與篇幅的選項'}).scrollIntoViewIfNeeded();
        await page.screenshot({path:path.join(out,'conference-'+name+'-csme.png')});
      }
      if(stem.startsWith('professor')) {
        for(const id of ['numbers','reasons','models','conclusion']) {
          await page.locator('#'+id).screenshot({path:path.join(out,name+'-'+id+'.png')});
        }
        const summary=page.locator('summary');await summary.focus();await page.keyboard.press('Enter');
        if(!await page.locator('details').evaluate(e=>e.open))throw new Error('Keyboard disclosure failed');
        if(await page.locator('details tbody tr').count()!==32)throw new Error('Expected 32 paired episode rows');
      }
      if(name==='mobile') {
        const table=page.locator('.table-wrap').first();await table.focus();await page.keyboard.press('ArrowRight');await page.waitForTimeout(250);
        if(!await table.evaluate(e=>e.scrollLeft>0))throw new Error('Keyboard table scroll failed');
        await table.evaluate(e=>e.scrollLeft=e.scrollWidth);
        await table.screenshot({path:path.join(out,stem+'-mobile-table-right.png')});
      }
      record.viewports.push({name,...geometry});
    }
    const links=await page.locator('a').evaluateAll(es=>es.map(e=>e.getAttribute('href')));
    for(const href of links) {
      if(/^https?:/.test(href))continue;
      const url=new URL(href,pathToFileURL(html));const fragment=url.hash;url.hash='';
      const target=fileURLToPath(url);await fs.access(target);
      if(fragment && target.endsWith('.html')) {
        const source=await fs.readFile(target,'utf8');
        if(!source.includes('id="'+fragment.slice(1)+'"'))throw new Error('Missing target anchor '+href);
      }
    }
    record.localLinksChecked=links.filter(h=>!/^https?:/.test(h)).length;
    await page.emulateMedia({media:'print'});await page.setViewportSize({width:794,height:1123});
    await page.evaluate(()=>document.querySelectorAll('details').forEach(e=>e.open=true));
    record.printCss=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
    if(record.printCss.scroll>record.printCss.width)throw new Error('Print CSS overflow');
    await page.screenshot({path:path.join(out,stem+'-print-css.png'),fullPage:true});
    if(errors.length || external.length)throw new Error('Runtime errors or external asset dependency');
    results.push(record);await page.close();
  }
} finally {await browser.close();}
await fs.writeFile(path.join(out,'browser_checks.json'),JSON.stringify({status:'PASS',scope:'local isolated Chrome; print CSS only, no paginated PDF export',results},null,2)+'\n');
console.log('PASS: both HTML files, three viewports, local links, keyboard interaction and offline rendering');
