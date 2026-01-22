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


def build_cmap_stream(pdf: pikepdf.Pdf) -> pikepdf.Stream:
    # Custom non-Identity CMap with explicit CIDSystemInfo.
    cmap_content = (
        b"/CIDInit /ProcSet findresource begin\n"
        b"12 dict begin\n"
        b"begincmap\n"
        b"/CIDSystemInfo << /Registry (Test) /Ordering (Custom) /Supplement 0 >> def\n"
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
        CIDSystemInfo=pikepdf.Dictionary(
            Registry=pikepdf.String("Test"),
            Ordering=pikepdf.String("Custom"),
            Supplement=0,
        ),
        WMode=0,
    )


def build_type0_font(pdf: pikepdf.Pdf, cmap_stream: pikepdf.Stream) -> pikepdf.Dictionary:
    font_path = find_font_path()
    font_bytes = font_path.read_bytes()
    font_file_stream = pikepdf.Stream(
        pdf,
        font_bytes,
        Length1=len(font_bytes),
    )

    font_descriptor = pikepdf.Dictionary(
        Type=pikepdf.Name("/FontDescriptor"),
        FontName=pikepdf.Name("/DejaVuSans"),
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
        BaseFont=pikepdf.Name("/DejaVuSans"),
        CIDSystemInfo=pikepdf.Dictionary(
            Registry=pikepdf.String("Test"),
            Ordering=pikepdf.String("Custom"),
            Supplement=0,
        ),
        FontDescriptor=font_descriptor,
        DW=1000,
        CIDToGIDMap=pikepdf.Name("/Identity"),
    )

    type0_font = pikepdf.Dictionary(
        Type=pikepdf.Name("/Font"),
        Subtype=pikepdf.Name("/Type0"),
        BaseFont=pikepdf.Name("/DejaVuSans"),
        Encoding=cmap_stream,
        DescendantFonts=[cid_font],
        CIDSystemInfo=pikepdf.Dictionary(
            Registry=pikepdf.String("Adobe"),
            Ordering=pikepdf.String("Custom"),
            Supplement=0,
        ),
    )

    return pdf.make_indirect(type0_font)


def main() -> None:
    output_path = Path(
        "output/font_ua1_7_21_3_1/mh_ua1-7.21.3-1_fail.pdf"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = pikepdf.Pdf.new()

    cmap_stream = build_cmap_stream(pdf)
    type0_font = build_type0_font(pdf, cmap_stream)

    page = pdf.add_blank_page(page_size=(612, 792))
    page.Resources = pikepdf.Dictionary(
        Font=pikepdf.Dictionary(F1=type0_font),
    )
    # Empty content stream to avoid any text drawing operators.
    page.Contents = pikepdf.Stream(pdf, b"")
    pdf.save(output_path, deterministic_id=True)


if __name__ == "__main__":
    main()
