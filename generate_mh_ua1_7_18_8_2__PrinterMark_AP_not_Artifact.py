#!/usr/bin/env python3
from pathlib import Path

import pikepdf


OUTPUT_DIR = Path("output/printermark_ua1_7_18_8_2")
FAIL_PATH = OUTPUT_DIR / "mh_ua1-7.18.8-2_fail__PrinterMark_AP_not_Artifact.pdf"
PASS_PATH = OUTPUT_DIR / "mh_ua1-7.18.8-2_pass__PrinterMark_AP_not_Artifact.pdf"


def build_xmp_metadata() -> bytes:
    return b"""<?xpacket begin='\xef\xbb\xbf' id='W5M0MpCehiHzreSzNTczkc9d'?>
<x:xmpmeta xmlns:x='adobe:ns:meta/'>
 <rdf:RDF xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
  <rdf:Description xmlns:pdfuaid='http://www.aiim.org/pdfua/ns/id/'>
   <pdfuaid:part>1</pdfuaid:part>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end='w'?>"""


def build_printermark_appearance(pdf: pikepdf.Pdf, artifact_wrapped: bool) -> pikepdf.Stream:
    if artifact_wrapped:
        content = b"/Artifact BMC\n0 0 1 rg\n10 10 60 40 re\nf\nEMC\n"
    else:
        content = b"0 0 1 rg\n10 10 60 40 re\nf\n"
    return pikepdf.Stream(
        pdf,
        content,
        Type=pikepdf.Name("/XObject"),
        Subtype=pikepdf.Name("/Form"),
        BBox=[0, 0, 100, 100],
        Resources=pikepdf.Dictionary(),
    )


def build_pdf(output_path: Path, artifact_wrapped: bool) -> None:
    pdf = pikepdf.Pdf.new()

    metadata_stream = pikepdf.Stream(
        pdf,
        build_xmp_metadata(),
        Type=pikepdf.Name("/Metadata"),
        Subtype=pikepdf.Name("/XML"),
    )
    pdf.Root.Metadata = metadata_stream

    page = pdf.add_blank_page(page_size=(612, 792))
    if "/Contents" in page:
        del page["/Contents"]
    page.Tabs = pikepdf.Name("/S")

    appearance = build_printermark_appearance(pdf, artifact_wrapped)
    annotation = pikepdf.Dictionary(
        Type=pikepdf.Name("/Annot"),
        Subtype=pikepdf.Name("/PrinterMark"),
        Rect=[50, 50, 150, 120],
        AP=pikepdf.Dictionary(N=appearance),
    )
    page.Annots = [pdf.make_indirect(annotation)]

    pdf.save(output_path)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_pdf(FAIL_PATH, artifact_wrapped=False)
    build_pdf(PASS_PATH, artifact_wrapped=True)


if __name__ == "__main__":
    main()
