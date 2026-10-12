import { createRequire } from 'node:module';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';

const root=fileURLToPath(new URL('../',import.meta.url));
const dependencies=createRequire(path.join(process.env.ENCLOSURE_QA_DEPENDENCIES || process.cwd(),'package.json'));
const { chromium }=dependencies('playwright');
const html=path.join(root,'docs/reports/professor_research_2026-10-12_zh.html');
const output=path.join(root,'openspec/changes/discover-public-thermal-scenes-20261012/artifacts/qa');
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.ENCLOSURE_CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
try {
  const page=await browser.newPage();
  const errors=[];
  const externalRequests=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await page.route(/^https?:\/\//,route=>{externalRequests.push(route.request().url());return route.abort();});
  const checks={viewports:[],errors,externalRequests};
  for(const [name,width] of [['desktop',1440],['tablet',820],['mobile',390]]) {
    await page.setViewportSize({width,height:1000});
    await page.goto(pathToFileURL(html).href);
    await page.evaluate(()=>document.fonts.ready);
    const sizes=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
    if(sizes.scroll>sizes.width)throw new Error('Body overflow at '+width);
    await page.screenshot({path:path.join(output,name+'.png'),fullPage:true});
    await page.locator('#results').screenshot({path:path.join(output,name+'-results.png')});
    await page.locator('#lqr').screenshot({path:path.join(output,name+'-lqr.png')});
    await page.locator('#structure').screenshot({path:path.join(output,name+'-structure.png')});
    await page.locator('#online').screenshot({path:path.join(output,name+'-online.png')});
    if(name==='mobile') {
      const region=page.locator('#online .table-wrap').first();
      await region.focus();await page.keyboard.press('ArrowRight');await page.waitForTimeout(250);
      if(!await region.evaluate(e=>e.scrollLeft>0 && e.scrollWidth>e.clientWidth))throw new Error('Scene table keyboard scroll failed');
      await region.evaluate(e=>e.scrollLeft=e.scrollWidth);
      await page.locator('#online').screenshot({path:path.join(output,'mobile-online-right.png')});
      await region.evaluate(e=>e.scrollLeft=0);
      checks.sceneTableKeyboardScroll=true;
    }
    checks.viewports.push({name,width,...sizes});
  }
  const structure=await page.evaluate(()=>{
    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
    const links=[...document.querySelectorAll('a')].map(e=>e.getAttribute('href'));
    return {duplicateIds:ids.filter((id,i)=>ids.indexOf(id)!==i),links,
      anchors:[...document.querySelectorAll('nav a')].map(e=>e.getAttribute('href'))};
  });
  if(structure.duplicateIds.length)throw new Error('Duplicate IDs');
  for(const anchor of structure.anchors) {
    if(!await page.locator(anchor).count())throw new Error('Missing anchor '+anchor);
    await page.locator('nav a[href="'+anchor+'"]').click();
    if(new URL(page.url()).hash!==anchor)throw new Error('Anchor navigation failed');
  }
  const missing=[];
  for(const href of structure.links) {
    if(!href || href.startsWith('#') || /^https?:/.test(href))continue;
    const local=new URL(href,pathToFileURL(html));
    local.hash='';
    try {await fs.access(fileURLToPath(local));}catch{missing.push(href);}
  }
  if(missing.length)throw new Error('Missing local sources '+missing.join(', '));
  await page.locator('summary').first().focus();
  await page.keyboard.press('Enter');
  if(!await page.locator('details').first().getAttribute('open').then(v=>v!==null))throw new Error('Keyboard details failed');
  const before=await page.locator('#gain').textContent();
  await page.locator('#q').focus();await page.keyboard.press('ArrowRight');
  const after=await page.locator('#gain').textContent();
  if(before===after)throw new Error('Q slider keyboard interaction failed');
  await page.keyboard.press('ArrowLeft');
  await page.locator('#r').focus();await page.keyboard.press('ArrowRight');
  if(before===await page.locator('#gain').textContent())throw new Error('R slider failed');
  await page.keyboard.press('ArrowLeft');
  await page.setViewportSize({width:1440,height:1000});
  await page.evaluate(()=>document.querySelectorAll('details').forEach(e=>e.open=true));
  await page.emulateMedia({media:'print'});
  const printWidth=await page.evaluate(()=>({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
  if(printWidth.scroll>printWidth.width)throw new Error('Print overflow');
  await page.pdf({path:path.join(root,'docs/reports/professor_research_2026-10-12_zh.pdf'),format:'A4',printBackground:true,preferCSSPageSize:true});
  if(errors.length || externalRequests.length)throw new Error('Errors or external asset requests');
  checks.structure=structure;
  checks.missingLocalLinks=missing;
  checks.keyboardDetails=true;checks.qrKeyboardInteraction=true;
  checks.printExpandedDetails=true;checks.printWidth=printWidth;
  checks.observed_utc=new Date().toISOString();
  await fs.writeFile(path.join(output,'browser_checks.json'),JSON.stringify(checks,null,2)+'\n');
  console.log(JSON.stringify({viewports:checks.viewports,anchors:structure.anchors.length,localLinksChecked:structure.links.length,
    qrKeyboardInteraction:true,errors,externalRequests,print:'PDF generated; visual inspection still required'},null,2));
} finally {await browser.close();}
