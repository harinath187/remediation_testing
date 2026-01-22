#!/usr/bin/env python3
from pathlib import Path

import pikepdf


def find_font_path() -> Path:
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("No suitable TrueType font found on the system.")


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


def build_cmap_stream(pdf: pikepdf.Pdf) -> pikepdf.Stream:
    cmap_content = (
        b"/CIDInit /ProcSet findresource begin\n"
        b"12 dict begin\n"
        b"begincmap\n"
        b"/CMapName /TestCMap def\n"
        b"/CMapType 1 def\n"
        b"/WMode 0 def\n"
        b"1 begincodespacerange\n"
        b"<00> <FF>\n"
        b"endcodespacerange\n"
        b"1 beginbfchar\n"
        b"<41> <0041>\n"
        b"endbfchar\n"
        b"endcmap\n"
        b"CMapName currentdict /CMap defineresource pop\n"
        b"end\n"
        b"end\n"
    )
    return pikepdf.Stream(
        pdf,
        cmap_content,
        Type=pikepdf.Name("/CMap"),
        CMapName=pikepdf.Name("/TestCMap"),
        WMode=0,
    )


def build_type0_font(
    pdf: pikepdf.Pdf,
    cmap_stream: pikepdf.Stream,
    registry_type0: str,
    registry_cidfont: str,
) -> pikepdf.Dictionary:
    font_path = find_font_path()
    font_bytes = font_path.read_bytes()
    font_file_stream = pikepdf.Stream(
        pdf,
        font_bytes,
        Length1=len(font_bytes),
    )

    font_descriptor = pikepdf.Dictionary(
        Type=pikepdf.Name("/FontDescriptor"),
        FontName=pikepdf.Name("/TestFont"),
        Flags=4,
        FontBBox=[-500, -200, 1500, 1000],
        ItalicAngle=0,
        Ascent=1000,
        Descent=-200,
        CapHeight=700,
        StemV=80,
        FontFile2=font_file_stream,
    )

    cid_font = pikepdf.Dictionary(
        Type=pikepdf.Name("/Font"),
        Subtype=pikepdf.Name("/CIDFontType2"),
        BaseFont=pikepdf.Name("/TestFont"),
        CIDSystemInfo=pikepdf.Dictionary(
            Registry=pikepdf.String(registry_cidfont),
            Ordering=pikepdf.String("TestOrdering"),
            Supplement=0,
        ),
        FontDescriptor=font_descriptor,
        DW=1000,
        CIDToGIDMap=pikepdf.Name("/Identity"),
    )

    type0_font = pikepdf.Dictionary(
        Type=pikepdf.Name("/Font"),
        Subtype=pikepdf.Name("/Type0"),
        BaseFont=pikepdf.Name("/TestFont"),
        Encoding=cmap_stream,
        DescendantFonts=[cid_font],
        CIDSystemInfo=pikepdf.Dictionary(
            Registry=pikepdf.String(registry_type0),
            Ordering=pikepdf.String("TestOrdering"),
            Supplement=0,
        ),
    )

    return pdf.make_indirect(type0_font)


def build_pdf(output_path: Path, registry_type0: str, registry_cidfont: str) -> None:
    pdf = pikepdf.Pdf.new()

    cmap_stream = build_cmap_stream(pdf)
    type0_font = build_type0_font(pdf, cmap_stream, registry_type0, registry_cidfont)

    page = pdf.add_blank_page(page_size=(612, 792))
    page.Resources = pikepdf.Dictionary(
        Font=pikepdf.Dictionary(F1=type0_font),
    )
    page.Contents = pikepdf.Stream(pdf, b"")

    pdf.Root.Metadata = build_xmp_metadata(pdf)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(output_path, deterministic_id=True)


def main() -> None:
    base_dir = Path("output/fonts_ua1_7_21_3_1")
    fail_path = base_dir / (
        "mh_ua1-7.21.3-1_fail__CIDSystemInfo_Registry_mismatch.pdf"
    )
    pass_path = base_dir / (
        "mh_ua1-7.21.3-1_pass__CIDSystemInfo_Registry_mismatch.pdf"
    )

    build_pdf(fail_path, registry_type0="RegistryA", registry_cidfont="RegistryB")
    build_pdf(pass_path, registry_type0="RegistryB", registry_cidfont="RegistryB")


if __name__ == "__main__":
    main()
