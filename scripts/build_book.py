"""Build the reading edition and PDF directly from the supplied Word manuscript."""
from pathlib import Path
import re, json, html, math
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
ASSETS = SITE / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
(ROOT / 'tmp' / 'qa').mkdir(parents=True, exist_ok=True)
SOURCE = next(ROOT.glob('HYD*.docx'))
doc = Document(SOURCE)
chapters = [(17,'Prefazione del traduttore'),(76,'Un rapporto dei rumori misteriosi'),(297,'Commento sul valore delle testimonianze'),(333,'Ulteriore sviluppo dei fatti di Hydesville'),(344,'Valore della testimonianza del giornalista E. W. Cabron'),(358,'Confessione di Margaret Fox Kane'),(377,'Valore della confessione di Margaret'),(390,'Margaret Fox ritratta'),(394,'Commento sulla medianità delle sorelle Fox'),(430,'Ritrovamento del corpo'),(437,'Deduzioni di E. Bozzano in relazione all’errore commesso dallo spirito'),(455,'Commento di M. Polidoro sulla medianità delle sorelle Fox'),(514,'Faziosità delle affermazioni di M. Polidoro'),(544,'Commento conclusivo'),(559,'Appendice')]
note = 'Nel manoscritto fornito l’appendice è indicata nell’indice, ma non contiene i testi originali inglesi del rapporto e della confessione di Margaret Fox. Questi documenti non sono quindi inclusi nella presente edizione.'
def clean(s):
    s = re.sub(r'_{8,}', '', s)
    return re.sub(r'\s+', ' ', s).strip()
def markup(p):
    out = ''
    for r in p.runs:
        t = html.escape(re.sub(r'_{8,}', '', r.text))
        if r.italic: t = '<i>'+t+'</i>'
        if r.bold: t = '<b>'+t+'</b>'
        out += t
    return re.sub(r'\s+', ' ', out).strip()
sections=[]
for n,(start,title) in enumerate(chapters):
    end=chapters[n+1][0] if n+1<len(chapters) else 564
    paras=[]
    for i in range(start+1,end):
        p=doc.paragraphs[i]
        t=clean(p.text)
        if t: paras.append({'i':i,'text':t,'html':markup(p),'subhead':t.lower().startswith('dichiarazione ') or i in (280,291)})
    if start==559: paras=[{'i':559,'text':note,'html':html.escape(note),'subhead':False}]
    sections.append({'id':f'capitolo-{n+1:02}','number':n+1,'title':title,'paragraphs':paras})
(ROOT/'tmp'/'book.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2),encoding='utf-8')

# Original, vector-drawn cover: the same geometry is used in the PDF and SVG.
cover_svg='''<svg xmlns="http://www.w3.org/2000/svg" width="620" height="920" viewBox="0 0 620 920"><rect width="620" height="920" fill="#153c3b"/><path d="M32 0v920" stroke="#b9b99c" stroke-opacity=".25"/><text x="64" y="76" fill="#d6cba9" font-family="Arial,sans-serif" font-size="15" letter-spacing="4">MODERNO SPIRITUALISMO</text><text x="61" y="205" fill="#f7f3e8" font-family="Georgia,serif" font-size="69">Hydesville</text><text x="64" y="272" fill="#d6cba9" font-family="Georgia,serif" font-style="italic" font-size="48">l’inizio</text><text x="65" y="327" fill="#e0e4d9" font-family="Arial,sans-serif" font-size="17">Un rapporto dei rumori misteriosi</text>'''
for k in range(12):
    x=118+k*14; y=430+k*10; w=384-k*28; h=332-k*11
    cover_svg+=f'<path d="M{x} {y+h} V{y+w/2} A{w/2} {w/2} 0 0 1 {x+w} {y+w/2} V{y+h}" fill="none" stroke="#c5ba93" stroke-width="1.2" opacity="{.35+k*.04}"/>'
cover_svg+='''<circle cx="310" cy="667" r="5" fill="#e5d3a1"/><text x="65" y="828" fill="#f7f3e8" font-family="Arial,sans-serif" font-size="21">E. E. Lewis</text><text x="65" y="863" fill="#c6d1c7" font-family="Arial,sans-serif" font-size="15">Traduzione e commenti di Michele Serra</text><text x="550" y="77" fill="#d6cba9" font-family="Arial,sans-serif" font-size="15">01</text></svg>'''
(ASSETS/'hydesville-copertina.svg').write_text(cover_svg,encoding='utf-8')

for name,file in [('Georgia','georgia.ttf'),('Georgia-Bold','georgiab.ttf'),('Georgia-Italic','georgiai.ttf'),('Georgia-BoldItalic','georgiaz.ttf'),('UI','arial.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Georgia',normal='Georgia',bold='Georgia-Bold',italic='Georgia-Italic',boldItalic='Georgia-BoldItalic')
W,H=439.37,651.97
def cover(c):
    c.saveState(); c.scale(W/620,H/920)
    c.setFillColor(HexColor('#153c3b')); c.rect(0,0,620,920,fill=1,stroke=0)
    c.setStrokeColor(HexColor('#52695c')); c.line(32,0,32,920)
    def label(x,y,s,size,font,color):
        c.setFillColor(HexColor(color)); c.setFont(font,size); c.drawString(x,920-y,s)
    label(64,76,'MODERNO SPIRITUALISMO',15,'UI','#d6cba9')
    label(61,205,'Hydesville',69,'Georgia','#f7f3e8')
    label(64,272,'l’inizio',48,'Georgia-Italic','#d6cba9')
    label(65,327,'Un rapporto dei rumori misteriosi',17,'UI','#e0e4d9')
    c.setStrokeColor(HexColor('#a5a381'));c.setLineWidth(1)
    for k in range(12):
        x=118+k*14; y=430+k*10; w=384-k*28; h=332-k*11
        p=c.beginPath();p.moveTo(x,920-y-h);p.lineTo(x,920-y-w/2)
        p.curveTo(x,920-y+w/6,x+w,920-y+w/6,x+w,920-y-w/2)
        p.lineTo(x+w,920-y-h);c.drawPath(p)
    c.setFillColor(HexColor('#e5d3a1'));c.circle(310,920-667,5,fill=1,stroke=0)
    label(65,828,'E. E. Lewis',21,'UI','#f7f3e8')
    label(65,863,'Traduzione e commenti di Michele Serra',15,'UI','#c6d1c7')
    label(550,77,'01',15,'UI','#d6cba9');c.restoreState()

body=ParagraphStyle('Body',fontName='Georgia',fontSize=10.5,leading=15.7,alignment=TA_JUSTIFY,spaceAfter=7,textColor=HexColor('#242b29'),allowWidows=0,allowOrphans=0)
small=ParagraphStyle('Small',parent=body,fontSize=8.7,leading=12,alignment=0,textColor=HexColor('#5b645e'))
heading=ParagraphStyle('Heading',fontName='Georgia',fontSize=23,leading=29,spaceAfter=24,textColor=HexColor('#000000'))
subhead=ParagraphStyle('Subheading',parent=body,fontName='Georgia-Bold',fontSize=11.3,leading=16,spaceBefore=16,spaceAfter=8,keepWithNext=True,alignment=0)
class Cover(Flowable):
    def __init__(self): Flowable.__init__(self);self.width=0;self.height=0
    def draw(self): pass
class BookDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable,'chapter_id'):
            self.canv.bookmarkPage(flowable.chapter_id)
            self.canv.addOutlineEntry(flowable.getPlainText(),flowable.chapter_id,0)
            self.chapter_pages[flowable.chapter_id]=self.page
def footer(c,d):
    if d.page==1: cover(c);return
    c.saveState();c.setFillColor(HexColor('#67736d'));c.setFont('UI',7)
    c.drawString(48,H-29,'HYDESVILLE  /  L’INIZIO')
    c.drawRightString(W-48,27,str(d.page));c.restoreState()

pdf=ASSETS/'hydesville-linizio.pdf'
page_map={}
for attempt in range(3):
    book=BookDoc(str(pdf),pagesize=(W,H),rightMargin=48,leftMargin=48,topMargin=57,bottomMargin=48,title='Hydesville, l’inizio',author='E. E. Lewis; traduzione e commenti di Michele Serra',pageCompression=1)
    book.chapter_pages={}
    story=[Cover(),PageBreak(),Spacer(1,45),Paragraph('Hydesville<br/><i>l’inizio</i>',heading),Paragraph('Un rapporto dei rumori misteriosi',body),Spacer(1,25),Paragraph('E. E. Lewis',body),Paragraph('Traduzione e commenti di<br/>Michele Serra',body),Spacer(1,80),Paragraph('Moderno Spiritualismo · Biblioteca digitale',small),Paragraph('Edizione digitale dal manoscritto fornito. Testo e attribuzioni conservati; impaginazione e indice rinnovati.',small),PageBreak(),Paragraph('Indice',heading)]
    for s in sections:
        page=page_map.get(s['id'],'—')
        story.append(Paragraph(f'<link href="#{s["id"]}" color="#242b29">{s["number"]:02}. {html.escape(s["title"])} <font size="8">· {page}</font></link>',ParagraphStyle('Toc',parent=small,spaceAfter=10,leading=13)))
    for s in sections:
        story += [PageBreak(),Paragraph(f'{s["number"]:02} /',small),Spacer(1,13)]
        p=Paragraph(html.escape(s['title']),heading);p.chapter_id=s['id'];story.append(p)
        # Original 1848 title page, epigraph and imprint are preserved as a separate opening.
        for p in s['paragraphs']:
            style=subhead if p['subhead'] else body
            if 77<=p['i']<=103: style=small
            story.append(Paragraph(p['html'],style))
    book.build(story,onFirstPage=footer,onLaterPages=footer)
    if page_map==book.chapter_pages: break
    page_map=book.chapter_pages

render=pdfium.PdfDocument(str(pdf))
render[0].render(scale=2).to_pil().save(ASSETS/'hydesville-copertina.png')
for idx in [1,2,3,4,18,39,len(render)-2,len(render)-1]:
    if idx<len(render):render[idx].render(scale=1.5).to_pil().save(ROOT/'tmp'/'qa'/f'page-{idx+1:03}.png')
from PIL import Image,ImageOps,ImageDraw
thumbs=[]
for idx in range(len(render)):
    im=render[idx].render(scale=.4).to_pil().convert('RGB');im.thumbnail((176,261))
    tile=Image.new('RGB',(196,291),'#d8d8d4');tile.paste(im,((196-im.width)//2,8));ImageDraw.Draw(tile).text((10,273),str(idx+1),fill='black');thumbs.append(tile)
for start in range(0,len(thumbs),40):
    subset=thumbs[start:start+40];sheet=Image.new('RGB',(196*8,291*math.ceil(len(subset)/8)),'white')
    for k,tile in enumerate(subset):sheet.paste(tile,((k%8)*196,(k//8)*291))
    sheet.save(ROOT/'tmp'/'qa'/f'contact-{start//40+1}.jpg')
nav=''.join(f'<a href="#{s["id"]}"><span>{s["number"]:02}</span>{html.escape(s["title"])}</a>' for s in sections)
content=''
for s in sections:
    content+=f'<section class="chapter" id="{s["id"]}"><div class="eyebrow">{s["number"]:02} / HYDESVILLE</div><h2>{html.escape(s["title"])}</h2>'
    for p in s['paragraphs']:
        tag='h3' if p['subhead'] else 'p'
        cls=' class="original-title"' if 77<=p['i']<=103 else ''
        content+=f'<{tag}{cls}>{p["html"]}</{tag}>'
    content+='</section>'
reader=(ROOT/'templates'/'reader.html').read_text(encoding='utf-8').replace('{{NAV}}',nav).replace('{{CONTENT}}',content)
(SITE/'leggi.html').write_text(reader,encoding='utf-8')
meta={'pages':len(render),'chapters':len(sections),'words':sum(len(p['text'].split()) for s in sections for p in s['paragraphs']),'pdf_bytes':pdf.stat().st_size,'source':SOURCE.name,'chapter_pages':page_map}
(ROOT/'tmp'/'book-stats.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(meta,ensure_ascii=True))
