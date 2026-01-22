#!/usr/bin/env python3
from pathlib import Path

import pikepdf


OUTPUT_DIR = Path("output/notes_ua1_7_9_2")
FAIL_PATH = OUTPUT_DIR / "mh_ua1-7.9-2_fail__Note_ID_missing.pdf"
PASS_PATH = OUTPUT_DIR / "mh_ua1-7.9-2_pass__Note_ID_missing.pdf"


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


def build_structure(pdf: pikepdf.Pdf, page: pikepdf.Page, include_id: bool) -> None:
    struct_tree_root = pdf.make_indirect(
        pikepdf.Dictionary(Type=pikepdf.Name("/StructTreeRoot"))
    )

    note_dict = pikepdf.Dictionary(
        Type=pikepdf.Name("/StructElem"),
        S=pikepdf.Name("/Note"),
        P=struct_tree_root,
        PG=page.obj,
    )
    if include_id:
        note_dict.ID = pikepdf.String("note-1")

    note_elem = pdf.make_indirect(note_dict)
    struct_tree_root.K = [note_elem]

    pdf.Root.StructTreeRoot = struct_tree_root


def build_pdf(output_path: Path, include_id: bool) -> None:
    pdf = pikepdf.Pdf.new()
    pdf.Root.Metadata = build_xmp_metadata(pdf)

    page = pdf.add_blank_page(page_size=(612, 792))
    build_structure(pdf, page, include_id)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path, deterministic_id=True)


def main() -> None:
    build_pdf(FAIL_PATH, include_id=False)
    build_pdf(PASS_PATH, include_id=True)


if __name__ == "__main__":
    main()
