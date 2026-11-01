from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    TextStringObject,
)

from beamerpkg.pdf_media import (
    PdfMediaError,
    discover_pdf_media_references,
    discover_pdf_media_placements,
)


def fixture(path: Path) -> None:
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    movie = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/Movie"),
            NameObject("/Movie"): DictionaryObject(
                {NameObject("/F"): TextStringObject("media/clip.mp4")}
            ),
            NameObject("/A"): DictionaryObject(
                {
                    NameObject("/Mode"): NameObject("/Repeat"),
                    NameObject("/ShowControls"): BooleanObject(True),
                }
            ),
        }
    )
    launch = DictionaryObject(
        {
            NameObject("/Subtype"): NameObject("/Link"),
            NameObject("/A"): DictionaryObject(
                {
                    NameObject("/S"): NameObject("/Launch"),
                    NameObject("/F"): TextStringObject("media/clip.mp4?autostart&loop"),
                }
            ),
        }
    )
    for annotation in (movie, launch):
        annotation[NameObject("/Rect")] = ArrayObject(
            [FloatObject(v) for v in (20, 30, 160, 110)]
        )
    page[NameObject("/Annots")] = ArrayObject(
        [writer._add_object(a) for a in (movie, launch)]
    )
    writer.write(path)


def test_placements_preserve_identity_and_encoded_options(tmp_path: Path) -> None:
    path = tmp_path / "talk.pdf"
    fixture(path)
    placements = discover_pdf_media_placements(path, {"media/clip.mp4"})
    assert len(placements) == 2
    assert placements[0].annotation_index == 0
    assert placements[0].loop is True and placements[0].controls is True
    assert placements[0].autostart is None
    assert placements[1].autostart is True and placements[1].loop is True
    assert placements[0].rect_pdf == (20, 30, 160, 110)
    assert discover_pdf_media_references(path) == ("media/clip.mp4",)
    with pytest.raises(PdfMediaError, match="manifest"):
        discover_pdf_media_placements(path, set())


@pytest.mark.parametrize("kind", ["rect", "remote", "option"])
def test_invalid_placements_fail_closed(tmp_path: Path, kind: str) -> None:
    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    annotations = writer.pages[0]["/Annots"]
    if kind == "rect":
        del annotations[0].get_object()["/Rect"]
    elif kind == "remote":
        annotations[0].get_object()["/Movie"][NameObject("/F")] = TextStringObject(
            "https://example.org/video.mp4"
        )
    else:
        annotations[1].get_object()["/A"][NameObject("/F")] = TextStringObject(
            "media/clip.mp4?autostart&unknown"
        )
    writer.write(path)
    with pytest.raises(PdfMediaError):
        discover_pdf_media_placements(path, {"media/clip.mp4"})
