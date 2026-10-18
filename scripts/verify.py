"""Check local links, manuscript coverage and the PDF navigation."""
from html.parser import HTMLParser
from pathlib import Path
from pypdf import PdfReader
from docx import Document
import json, re

root=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.links=[];self.ids=set();self.parts=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a:self.links.append(a[key])
    def handle_data(self,data): self.parts.append(data)
pages={p.name:Page(p.read_text(encoding='utf-8')) for p in (root/'site').glob('*.html')}
for name,page in pages.items():
    for link in page.links:
        if link.startswith(('https:','http:','data:','mailto:')):continue
        target,_,anchor=link.partition('#')
        target=target or name
        assert (root/'site'/target).exists(),(name,link)
        if anchor:assert anchor in pages[target].ids,(name,link)
assert len([x for x in pages['leggi.html'].ids if x.startswith('capitolo-')])==15
reader_text=re.sub(r'\s+',' ',''.join(pages['leggi.html'].parts))
doc=Document(next(root.glob('HYD*.docx')))
headings={17,76,297,333,344,358,377,390,394,430,437,455,514,544,559}
count=0
for i,p in enumerate(doc.paragraphs):
    if i<17 or i>=551 or i in headings:continue
    text=re.sub(r'\s+',' ',re.sub(r'_{8,}','',p.text)).strip()
    if text:assert text in reader_text,('Missing source paragraph',i);count+=1
r=PdfReader(root/'site/assets/hydesville-linizio.pdf')
assert len(r.outline)==15
assert len(r.pages[2].get('/Annots',[]))==15
assert all(len(p.extract_text().strip())>30 for p in r.pages)
assert all('\ufffd' not in ''.join(p.parts) for p in pages.values())
print(json.dumps({'source_paragraphs_verified':count,'chapters':15,'pdf_pages':len(r.pages),'pdf_bookmarks':len(r.outline),'toc_links':15,'local_links':'OK','empty_pages':0},indent=2))
