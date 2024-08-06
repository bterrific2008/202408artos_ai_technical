"""PyPDFLoader form langchain_community, but can accept streams"""

from langchain_core.documents import Document
from langchain_community.document_loaders.blob_loaders import Blob
from langchain_community.document_loaders.pdf import BasePDFLoader
from langchain_community.document_loaders.parsers.pdf import PyPDFParser

from typing import Optional, Union, Dict, Iterator, BinaryIO


class PyPDFStreamLoader(BasePDFLoader):
    """Load PDF using pypdf into list of documents.

    Loader chunks by page and stores page numbers in metadata.
    """

    def __init__(
        self,
        stream: BinaryIO,
        extract_images: bool = False,
        extraction_mode: str = "plain",
        extraction_kwargs: Optional[Dict] = None,
    ) -> None:
        """Initialize with a BinaryIO stream."""
        try:
            import pypdf  # noqa:F401
        except ImportError:
            raise ImportError(
                "pypdf package not found, please install it with " "`pip install pypdf`"
            )
        self._stream = stream
        self.parser = PyPDFParser(
            extract_images=extract_images,
            extraction_mode=extraction_mode,
            extraction_kwargs=extraction_kwargs,
        )

    def lazy_load(
        self,
    ) -> Iterator[Document]:
        """Lazy load given path as pages."""
        # TODO: set path to name of stream
        blob = Blob.from_data(self._stream, path="uploaded_file.pdf")  # type: ignore[attr-defined]
        yield from self.parser.parse(blob)

if __name__ == "__main__":
    loader = PyPDFStreamLoader(open("../data/protocol/AMP_224.pdf", "rb").read())
    pages = loader.load_and_split()

    print(len(pages))