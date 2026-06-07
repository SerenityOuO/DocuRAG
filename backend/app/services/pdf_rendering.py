from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path


class PdfRenderingError(RuntimeError):
    pass


class PdfRenderingDependencyError(PdfRenderingError):
    pass


@dataclass(frozen=True)
class RenderedPdfPage:
    image_id: str
    page_number: int
    path: str
    width: int
    height: int
    dpi: int
    checksum: str
    created_at: datetime


class PdfPageRenderer:
    def __init__(
        self,
        data_dir: Path,
        dpi: int = 150,
        max_side: int = 1800,
    ) -> None:
        self.data_dir = data_dir
        self.output_root = data_dir / "page-images"
        self.dpi = dpi
        self.max_side = max_side

    def render_pages(
        self,
        content: bytes,
        document_id: str,
        page_numbers: list[int],
        timestamp: datetime | None = None,
    ) -> list[RenderedPdfPage]:
        try:
            import fitz
        except ImportError as exc:
            raise PdfRenderingDependencyError(
                "pdf_rendering_dependency_missing: PyMuPDF is not installed. "
                "Install backend dependencies before enabling PDF rendering."
            ) from exc

        try:
            pdf_document = fitz.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise PdfRenderingError(f"pdf_render_failed: {exc}") from exc

        created_at = timestamp or datetime.now(UTC)
        output_dir = self.output_root / document_id
        output_dir.mkdir(parents=True, exist_ok=True)
        rendered_pages: list[RenderedPdfPage] = []

        try:
            for page_number in page_numbers:
                if page_number < 1 or page_number > pdf_document.page_count:
                    raise PdfRenderingError(f"pdf_render_failed: page {page_number} is out of range.")

                page = pdf_document.load_page(page_number - 1)
                zoom = self._zoom_for_page(float(page.rect.width), float(page.rect.height))
                pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
                image_id = f"{document_id}-page-{page_number:03d}"
                relative_path = Path("page-images") / document_id / f"page-{page_number:03d}.png"
                output_path = self.data_dir / relative_path
                pixmap.save(str(output_path))
                image_bytes = output_path.read_bytes()

                rendered_pages.append(
                    RenderedPdfPage(
                        image_id=image_id,
                        page_number=page_number,
                        path=relative_path.as_posix(),
                        width=pixmap.width,
                        height=pixmap.height,
                        dpi=max(1, round(zoom * 72)),
                        checksum=sha256(image_bytes).hexdigest(),
                        created_at=created_at,
                    )
                )
        finally:
            pdf_document.close()

        return rendered_pages

    def _zoom_for_page(self, width_points: float, height_points: float) -> float:
        zoom = max(1, self.dpi) / 72
        page_max_side = max(width_points, height_points)

        if page_max_side <= 0:
            return zoom

        rendered_max_side = page_max_side * zoom
        if rendered_max_side <= self.max_side:
            return zoom

        return max(1 / 72, self.max_side / page_max_side)
