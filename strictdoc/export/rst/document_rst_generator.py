# mypy: disable-error-code="no-untyped-call,no-untyped-def"
import os
from pathlib import Path

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.rst.writer import RSTWriter


def get_path_components(folder_path):
    path = os.path.normpath(folder_path)
    return path.split(os.sep)


class DocumentRSTGenerator:
    @staticmethod
    def export_tree(traceability_index: TraceabilityIndex, output_rst_root):
        Path(output_rst_root).mkdir(parents=True, exist_ok=True)

        document: SDocDocument
        assert isinstance(traceability_index.document_tree, DocumentTree)
        for document in traceability_index.document_tree.document_list:
            document_content = DocumentRSTGenerator.export(
                document, traceability_index
            )

            assert isinstance(document.meta, DocumentMeta)
            output_folder = os.path.join(
                output_rst_root,
                document.meta.input_doc_dir_rel_path.relative_path,
            )
            Path(output_folder).mkdir(parents=True, exist_ok=True)

            document_out_file = f"{document.meta.document_filename_base}.rst"
            output_path = os.path.join(output_folder, document_out_file)

            with open(output_path, "w", encoding="utf8") as file:
                file.write(document_content)

    @staticmethod
    def export(document, traceability_index):
        writer = RSTWriter(traceability_index)

        single_or_many = (
            len(traceability_index.document_tree.document_list) == 1
        )
        output = writer.write(document, single_or_many)

        return output
