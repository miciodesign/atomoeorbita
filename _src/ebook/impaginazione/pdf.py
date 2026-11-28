from playwright.sync_api import sync_playwright
import sys
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page()
    pg.goto("file:///home/claude/ebook/guida.html", wait_until="networkidle")
    pg.wait_for_timeout(500)
    pg.pdf(path=sys.argv[1], prefer_css_page_size=True, print_background=True, display_header_footer=True,
      header_template="<span></span>",
      footer_template='<div style="width:100%;font:7px monospace;letter-spacing:1.5px;color:#6B655A;padding:0 20mm;display:flex;justify-content:space-between"><span>ATOMO E ORBITA · NUCLEARE E SPAZIO, SPIEGATI BENE</span><span class="pageNumber"></span></div>')
    b.close()
