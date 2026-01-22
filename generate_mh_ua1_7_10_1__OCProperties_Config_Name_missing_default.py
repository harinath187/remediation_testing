#!/usr/bin/env python3
from pathlib import Path

import pikepdf


OUTPUT_DIR = Path("output/ocproperties_ua1_7_10_1_default")
FAIL_PATH = OUTPUT_DIR / (
    "mh_ua1-7.10-1_fail__OCProperties_Config_Name_missing_default.pdf"
)
PASS_PATH = OUTPUT_DIR / (
    "mh_ua1-7.10-1_pass__OCProperties_Config_Name_missing_default.pdf"
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


def build_ocproperties(pdf: pikepdf.Pdf, missing_name: bool) -> pikepdf.Dictionary:
    ocg = pikepdf.Dictionary(
        Type=pikepdf.Name("/OCG"),
        Name=pikepdf.String("Layer 1"),
    )
    ocg_ref = pdf.make_indirect(ocg)

    default_config = pikepdf.Dictionary(
        Type=pikepdf.Name("/OCConfig"),
        OCGs=[ocg_ref],
    )

    secondary_config = pikepdf.Dictionary(
        Type=pikepdf.Name("/OCConfig"),
        Name=pikepdf.String("OCConfig-2"),
        OCGs=[ocg_ref],
    )

    if not missing_name:
        default_config.Name = pikepdf.String("OCConfig-1")

    return pikepdf.Dictionary(
        OCGs=[ocg_ref],
        Configs=[default_config, secondary_config],
        D=default_config,
    )


def build_pdf(output_path: Path, missing_name: bool) -> None:
    pdf = pikepdf.Pdf.new()
    pdf.Root.Metadata = build_xmp_metadata(pdf)

    page = pdf.add_blank_page(page_size=(612, 792))
    page.Contents = pikepdf.Stream(pdf, b"")

    pdf.Root.OCProperties = build_ocproperties(pdf, missing_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path, deterministic_id=True)


def main() -> None:
    build_pdf(FAIL_PATH, missing_name=True)
    build_pdf(PASS_PATH, missing_name=False)


if __name__ == "__main__":
    main()
