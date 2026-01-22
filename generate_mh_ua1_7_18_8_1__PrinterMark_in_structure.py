#!/usr/bin/env python3
from pathlib import Path

import pikepdf


OUTPUT_DIR = Path("output/printermark_ua1_7_18_8_1")
FAIL_PATH = OUTPUT_DIR / "mh_ua1-7.18.8-1_fail__PrinterMark_in_structure.pdf"
PASS_PATH = OUTPUT_DIR / "mh_ua1-7.18.8-1_pass__PrinterMark_in_structure.pdf"


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


def build_printermark_appearance(pdf: pikepdf.Pdf) -> pikepdf.Stream:
    content = b"0 0 1 rg\n10 10 60 40 re\nf\n"
    return pikepdf.Stream(
        pdf,
        content,
        Type=pikepdf.Name("/XObject"),
        Subtype=pikepdf.Name("/Form"),
        BBox=[0, 0, 100, 100],
        Resources=pikepdf.Dictionary(),
    )


def add_structure(
    pdf: pikepdf.Pdf,
    page: pikepdf.Page,
    annotation: pikepdf.Object,
    include_printermark: bool,
) -> None:
    struct_tree_root = pdf.make_indirect(
        pikepdf.Dictionary(Type=pikepdf.Name("/StructTreeRoot"))
    )

    struct_elem = pikepdf.Dictionary(
        Type=pikepdf.Name("/StructElem"),
        S=pikepdf.Name("/P"),
        P=struct_tree_root,
        PG=page.obj,
    )

    if include_printermark:
        objr = pikepdf.Dictionary(
            Type=pikepdf.Name("/OBJR"),
            Obj=annotation,
            Pg=page.obj,
        )
        struct_elem.K = [pdf.make_indirect(objr)]
        annotation.StructParent = 0
        parent_tree = pikepdf.Dictionary(Nums=[0, pdf.make_indirect(struct_elem)])
    else:
        struct_elem.K = []
        parent_tree = pikepdf.Dictionary(Nums=[])

    struct_tree_root.K = [pdf.make_indirect(struct_elem)]
    struct_tree_root.ParentTree = pdf.make_indirect(parent_tree)

    pdf.Root.StructTreeRoot = struct_tree_root
    pdf.Root.MarkInfo = pikepdf.Dictionary(Marked=True)
    pdf.Root.Lang = pikepdf.String("en-US")


def build_pdf(output_path: Path, include_printermark: bool) -> None:
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

    appearance = build_printermark_appearance(pdf)
    annotation = pikepdf.Dictionary(
        Type=pikepdf.Name("/Annot"),
        Subtype=pikepdf.Name("/PrinterMark"),
        Rect=[50, 50, 150, 120],
        AP=pikepdf.Dictionary(N=appearance),
    )
    annot_ref = pdf.make_indirect(annotation)
    page.Annots = [annot_ref]

    add_structure(pdf, page, annot_ref, include_printermark)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path, deterministic_id=True)


def main() -> None:
    build_pdf(FAIL_PATH, include_printermark=True)
    build_pdf(PASS_PATH, include_printermark=False)


if __name__ == "__main__":
    main()
