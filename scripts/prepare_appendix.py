"""Prepare web facsimiles and retain the reviewed English transcripts as sources."""
from pathlib import Path
import shutil
from pypdf import PdfReader, PdfWriter
from PIL import Image

root=Path(__file__).resolve().parents[1]
source=root/'output'/'appendici-inglesi'
target=root/'sources'/'appendici'
target.mkdir(parents=True,exist_ok=True)
for old,new in [('01-lewis-1848-rapporto-originale','appendice-lewis-en'),('02-margaret-fox-1888-confessione','appendice-fox-en')]:
    shutil.copy2(source/(old+'.txt'),target/(new+'.txt'))
    reader=PdfReader(source/(old+'.pdf'))
    writer=PdfWriter();writer.append(reader)
    for page in writer.pages:
        maximum=(round(float(page.mediabox.width)*200/72),round(float(page.mediabox.height)*200/72))
        for image in list(page.images):
            reduced=image.image.convert('L')
            reduced.thumbnail(maximum,Image.Resampling.LANCZOS)
            image.replace(reduced,quality=85,optimize=True)
    writer.add_metadata({'/Title':str(reader.metadata.title),'/Subject':'Facsimile con testo selezionabile; immagini ottimizzate a 200 dpi per la lettura online'})
    writer.compress_identical_objects(remove_identicals=True,remove_orphans=True)
    result=root/'site'/'assets'/(new+'.pdf');writer.write(result)
    print(result.name,len(writer.pages),'pages',result.stat().st_size,'bytes')
