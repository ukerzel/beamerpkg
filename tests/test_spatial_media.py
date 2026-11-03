from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject,
    BooleanObject,
    DictionaryObject,
    FloatObject,
    NameObject,
    NumberObject,
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


def _launch_target(path: Path, target: str) -> None:
    writer = PdfWriter(clone_from=PdfReader(path))
    writer.pages[0]["/Annots"][1].get_object()["/A"][NameObject("/F")] = (
        TextStringObject(target)
    )
    writer.write(path)


def test_launch_link_tolerates_whitespace_and_empty_options(tmp_path: Path) -> None:
    # pack strips the target and ignores empty options; spatial must agree.
    path = tmp_path / "talk.pdf"
    fixture(path)
    _launch_target(path, " media/clip.mp4?autostart&loop& ")
    launch = discover_pdf_media_placements(path, {"media/clip.mp4"})[1]
    assert launch.asset_path == "media/clip.mp4"
    assert launch.autostart is True and launch.loop is True


def test_media_outside_the_mediabox_vertically_is_rejected(tmp_path: Path) -> None:
    # A CropBox taller than the MediaBox must not admit media above the page.
    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    page = writer.pages[0]
    page[NameObject("/CropBox")] = ArrayObject(
        [FloatObject(v) for v in (0, 0, 320, 400)]
    )
    page["/Annots"][0].get_object()[NameObject("/Rect")] = ArrayObject(
        [FloatObject(v) for v in (20, 200, 160, 260)]
    )
    writer.write(path)
    with pytest.raises(PdfMediaError, match="empty visible"):
        discover_pdf_media_placements(path, {"media/clip.mp4"})


@pytest.mark.parametrize("show_controls", [False, True])
def test_pdf_boolean_controls_preserve_false_as_well_as_true(
    tmp_path: Path, show_controls: bool
) -> None:
    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    writer.pages[0]["/Annots"][0].get_object()["/A"][NameObject("/ShowControls")] = (
        BooleanObject(show_controls)
    )
    writer.write(path)
    placement = discover_pdf_media_placements(path, {"media/clip.mp4"})[0]
    assert placement.controls is show_controls


@pytest.mark.parametrize(
    "reference", ["./media/clip.mp4", "media//clip.mp4", "media\\clip.mp4"]
)
def test_relative_media_normalization_agrees_on_both_routes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, reference: str
) -> None:
    from types import SimpleNamespace

    from beamerpkg import cli
    from beamerpkg.package import pack_package
    from beamerpkg.spatial_project import load_project

    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    writer.pages[0]["/Annots"][0].get_object()["/Movie"][NameObject("/F")] = (
        TextStringObject(reference)
    )
    writer.pages[0]["/Annots"][1].get_object()["/A"][NameObject("/F")] = (
        TextStringObject(reference + "?autostart&loop")
    )
    writer.write(path)
    (tmp_path / "media").mkdir()
    video = tmp_path / "media/clip.mp4"
    video.write_bytes(b"video")
    package = pack_package(path)
    monkeypatch.setattr(cli.shutil, "which", lambda _: "/fake/pdfpc")

    def present(command, *, cwd, check):
        assert (cwd / "media/clip.mp4").read_bytes() == video.read_bytes()
        assert (cwd / "talk.pdf").read_bytes() == path.read_bytes()
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", present)
    assert cli.main(["present", str(package)]) == 0
    with load_project(package) as project:
        assert {p["asset_path"] for p in project.data["placements"]} == {
            "media/clip.mp4"
        }
        assert project.assets["media/clip.mp4"].read_bytes() == video.read_bytes()


@pytest.mark.parametrize("key", ["/UF", "/F"])
def test_pdf_file_specification_dictionary_is_discovered(
    tmp_path: Path, key: str
) -> None:
    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    writer.pages[0]["/Annots"][0].get_object()["/Movie"][NameObject("/F")] = (
        DictionaryObject({NameObject(key): TextStringObject("media/clip.mp4")})
    )
    writer.write(path)
    assert discover_pdf_media_references(path) == ("media/clip.mp4",)
    assert (
        discover_pdf_media_placements(path, {"media/clip.mp4"})[0].asset_path
        == "media/clip.mp4"
    )


@pytest.mark.parametrize(
    "kind",
    [
        "movie-dictionary",
        "activation-type",
        "unknown-option",
        "mode",
        "controls",
        "file-spec",
        "rectangle-type",
        "rectangle-empty",
        "rectangle-off-page",
        "path-traversal",
        "launch-start",
        "launch-duplicate",
        "launch-value",
    ],
)
def test_unsupported_media_semantics_are_reported(tmp_path: Path, kind: str) -> None:
    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    movie = writer.pages[0]["/Annots"][0].get_object()
    launch = writer.pages[0]["/Annots"][1].get_object()
    if kind == "movie-dictionary":
        movie[NameObject("/Movie")] = NumberObject(42)
    elif kind == "activation-type":
        movie[NameObject("/A")] = TextStringObject("unsupported")
    elif kind == "unknown-option":
        movie["/A"][NameObject("/Rate")] = NumberObject(2)
    elif kind == "mode":
        movie["/A"][NameObject("/Mode")] = NameObject("/Open")
    elif kind == "controls":
        movie["/A"][NameObject("/ShowControls")] = TextStringObject("false")
    elif kind == "file-spec":
        movie["/Movie"][NameObject("/F")] = DictionaryObject()
    elif kind == "rectangle-type":
        movie["/Rect"][0] = TextStringObject("20")
    elif kind in {"rectangle-empty", "rectangle-off-page"}:
        rect = (20, 30, 20, 110) if kind == "rectangle-empty" else (400, 30, 450, 110)
        movie[NameObject("/Rect")] = ArrayObject([FloatObject(v) for v in rect])
    elif kind == "path-traversal":
        movie["/Movie"][NameObject("/F")] = TextStringObject("../media/clip.mp4")
    else:
        query = {
            "launch-start": "start=3",
            "launch-duplicate": "loop&loop",
            "launch-value": "autostart=true",
        }[kind]
        launch["/A"][NameObject("/F")] = TextStringObject("media/clip.mp4?" + query)
    writer.write(path)
    with pytest.raises(PdfMediaError):
        discover_pdf_media_placements(path, {"media/clip.mp4"})


def test_unknown_playback_flags_stay_unknown_and_once_does_not_loop(
    tmp_path: Path,
) -> None:
    path = tmp_path / "talk.pdf"
    fixture(path)
    writer = PdfWriter(clone_from=PdfReader(path))
    movie = writer.pages[0]["/Annots"][0].get_object()
    del movie["/A"]
    writer.write(path)
    placement = discover_pdf_media_placements(path, {"media/clip.mp4"})[0]
    assert placement.autostart is placement.loop is placement.controls is None
    movie[NameObject("/A")] = DictionaryObject(
        {NameObject("/Mode"): NameObject("/Once")}
    )
    writer.write(path)
    assert discover_pdf_media_placements(path, {"media/clip.mp4"})[0].loop is False


def test_unrelated_annotations_do_not_become_media(tmp_path: Path) -> None:
    path = tmp_path / "talk.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=320, height=180)
    page[NameObject("/Annots")] = ArrayObject(
        [
            NumberObject(42),
            DictionaryObject(
                {
                    NameObject("/Subtype"): NameObject("/Link"),
                    NameObject("/A"): DictionaryObject(
                        {
                            NameObject("/S"): NameObject("/URI"),
                            NameObject("/URI"): TextStringObject("https://example.org"),
                        }
                    ),
                }
            ),
            DictionaryObject(
                {
                    NameObject("/Subtype"): NameObject("/Link"),
                    NameObject("/A"): DictionaryObject(
                        {
                            NameObject("/S"): NameObject("/Launch"),
                            NameObject("/F"): TextStringObject("tool.exe"),
                        }
                    ),
                }
            ),
        ]
    )
    writer.write(path)
    assert discover_pdf_media_references(path) == ()
    assert discover_pdf_media_placements(path, set()) == ()


def test_unreadable_pdf_discovery_is_a_controlled_error(tmp_path: Path) -> None:
    path = tmp_path / "talk.pdf"
    path.write_bytes(b"not a PDF")
    for discover in (
        lambda: discover_pdf_media_references(path),
        lambda: discover_pdf_media_placements(path, set()),
    ):
        with pytest.raises(PdfMediaError, match="PDF"):
            discover()
