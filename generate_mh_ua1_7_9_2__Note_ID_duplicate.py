#!/usr/bin/env python3
from pathlib import Path

import pikepdf


OUTPUT_DIR = Path("output/structure_ua1_7_9_2")
FAIL_PATH = OUTPUT_DIR / "mh_ua1-7.9-2_fail__Note_ID_duplicate.pdf"
PASS_PATH = OUTPUT_DIR / "mh_ua1-7.9-2_pass__Note_ID_unique.pdf"


def build_xmp_metadata(pdf: pikepdf.Pdf) -> pikepdf.Stream:
    xmp = (
        b'<?xpacket begin=" " id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        b'<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        b' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        b'  <rdf:Description rdf:about=""\n'
        b'    xmlns:pdfuaid="http://www.aiim.org/pdfua/ns/id/">\n'
        b'   <pdfuaid:part>1</pdfuaid:part>\n'
        b'  </rdf:Description>\n'
        b' </rdf:RDF>\n'
        b'</x:xmpmeta>\n'
        b'<?xpacket end="w"?>\n'
    )
    return pikepdf.Stream(
        pdf,
        xmp,
        Type=pikepdf.Name("/Metadata"),
        Subtype=pikepdf.Name("/XML"),
    )


def build_structure(
    pdf: pikepdf.Pdf,
    page: pikepdf.Page,
    duplicate_ids: bool,
) -> None:
    struct_tree_root = pdf.make_indirect(
        pikepdf.Dictionary(Type=pikepdf.Name("/StructTreeRoot"))
    )

    note_id_first = pikepdf.String("note-1")
    note_id_second = pikepdf.String("note-1" if duplicate_ids else "note-2")

    struct_elem_one = pdf.make_indirect(
        pikepdf.Dictionary(
            Type=pikepdf.Name("/StructElem"),
            S=pikepdf.Name("/Note"),
            P=struct_tree_root,
            PG=page.obj,
            K=0,
            ID=note_id_first,
        )
    )
    struct_elem_two = pdf.make_indirect(
        pikepdf.Dictionary(
            Type=pikepdf.Name("/StructElem"),
            S=pikepdf.Name("/Note"),
            P=struct_tree_root,
            PG=page.obj,
            K=1,
            ID=note_id_second,
        )
    )

    parent_tree = pdf.make_indirect(
        pikepdf.Dictionary(Nums=[0, [struct_elem_one, struct_elem_two]])
    )

    struct_tree_root.K = [struct_elem_one, struct_elem_two]
    struct_tree_root.ParentTree = parent_tree

    pdf.Root.StructTreeRoot = struct_tree_root
    pdf.Root.MarkInfo = pikepdf.Dictionary(Marked=True)
    pdf.Root.Lang = pikepdf.String("en-US")
    page.StructParents = 0


def build_page_content(pdf: pikepdf.Pdf, page: pikepdf.Page) -> None:
    page.Resources = pikepdf.Dictionary(
        Font=pikepdf.Dictionary(
            F1=pikepdf.Dictionary(
                Type=pikepdf.Name("/Font"),
                Subtype=pikepdf.Name("/Type1"),
                BaseFont=pikepdf.Name("/Helvetica"),
            )
        )
    )

    content = (
        b"/Note << /MCID 0 >> BDC\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"72 720 Td\n"
        b"(Note one) Tj\n"
        b"ET\n"
        b"EMC\n"
        b"/Note << /MCID 1 >> BDC\n"
        b"BT\n"
        b"/F1 12 Tf\n"
        b"72 700 Td\n"
        b"(Note two) Tj\n"
        b"ET\n"
        b"EMC\n"
    )
    page.Contents = pikepdf.Stream(pdf, content)


def build_pdf(output_path: Path, duplicate_ids: bool) -> None:
    pdf = pikepdf.Pdf.new()
    pdf.Root.Metadata = build_xmp_metadata(pdf)

    page = pdf.add_blank_page(page_size=(612, 792))
    build_page_content(pdf, page)
    build_structure(pdf, page, duplicate_ids)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path, deterministic_id=True)


def main() -> None:
    build_pdf(FAIL_PATH, duplicate_ids=True)
    build_pdf(PASS_PATH, duplicate_ids=False)


if __name__ == "__main__":
    main()
