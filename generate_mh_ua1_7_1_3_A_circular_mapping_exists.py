#!/usr/bin/env python3
from pathlib import Path

import pikepdf


OUTPUT_DIR = Path("output/structure_ua1_7_1_3")
FAIL_PATH = OUTPUT_DIR / (
    "mh_ua1-7.1-3_fail__A_circular_mapping_exists.pdf"
)
PASS_PATH = OUTPUT_DIR / (
    "mh_ua1-7.1-3_pass__A_circular_mapping_exists.pdf"
)


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


def build_struct_tree_root(circular: bool) -> pikepdf.Dictionary:
    if circular:
        role_map = pikepdf.Dictionary(
            {
                "/H1": pikepdf.Name("/Div"),
                "/Div": pikepdf.Name("/H1"),
            }
        )
    else:
        role_map = pikepdf.Dictionary(
            {
                "/H1": pikepdf.Name("/Div"),
            }
        )

    return pikepdf.Dictionary(
        Type=pikepdf.Name("/StructTreeRoot"),
        RoleMap=role_map,
    )


def build_pdf(output_path: Path, circular: bool) -> None:
    pdf = pikepdf.Pdf.new()
    pdf.Root.Metadata = build_xmp_metadata(pdf)

    page = pdf.add_blank_page(page_size=(612, 792))
    page.Contents = pikepdf.Stream(pdf, b"")

    pdf.Root.StructTreeRoot = build_struct_tree_root(circular)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path, deterministic_id=True)


def main() -> None:
    build_pdf(FAIL_PATH, circular=True)
    build_pdf(PASS_PATH, circular=False)


if __name__ == "__main__":
    main()
