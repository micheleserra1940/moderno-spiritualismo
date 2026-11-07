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
        if tag=='br':self.parts.append(' ')
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
assert len([item for item in r.outline if isinstance(item,dict)])==15
assert sum(len(item) for item in r.outline if isinstance(item,list))==2
assert len(r.pages[2].get('/Annots',[]))==17
appendix_pages=0
for stem,expected in [('appendice-lewis-en',34),('appendice-fox-en',3)]:
    source=(root/'sources'/'appendici'/(stem+'.txt')).read_text(encoding='utf-8-sig')
    sections=source.split('\f')
    assert len(sections)==expected
    for section in sections:
        section=re.sub(r'^\s*(?:FRONTESPIZIO|PAGINA \d+ DEL PDF DI ORIGINE)\s*\n=+\s*\n','',section).strip()
        for paragraph in re.split(r'\n\s*\n',section):
            text=re.sub(r'\s+',' ',paragraph).strip()
            assert text in reader_text,('Missing English passage',stem,text[:80])
    facsimile=PdfReader(root/'site'/'assets'/(stem+'.pdf'))
    assert len(facsimile.pages)==expected
    appendix_pages+=expected
assert len(r.pages)==131+appendix_pages
assert 'Questi documenti non sono quindi inclusi' not in reader_text
assert all(len(p.extract_text().strip())>30 for p in r.pages)
assert all('\ufffd' not in ''.join(p.parts) for p in pages.values())
print(json.dumps({'source_paragraphs_verified':count,'chapters':15,'english_documents':2,'appendix_source_pages':appendix_pages,'pdf_pages':len(r.pages),'toc_links':17,'local_links':'OK','empty_pages':0},indent=2))
