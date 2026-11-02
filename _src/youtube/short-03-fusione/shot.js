const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+process.cwd()+'/t.html');await p.waitForTimeout(300);
for(const id of ['a','b','c','d','e','f']){await (await p.$('#'+id)).screenshot({path:id+'.png'});}await b.close();})();
