const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/t.html');await p.waitForTimeout(300);
for(const e of await p.$$('.c')){const id=await e.getAttribute('id');await e.screenshot({path:id+'.png'});}await b.close();})();
