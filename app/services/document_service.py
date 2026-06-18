import os
import pathlib
import uuid
from werkzeug.utils import secure_filename

from flask import current_app

from app.extensions import db
from app.models import Document


class DocumentService:
    @staticmethod
    def _allowed_extension(filename: str) -> bool:
        extension = pathlib.Path(filename).suffix.lower().lstrip(".")
        return extension in current_app.config["DOCUMENT_ALLOWED_EXTENSIONS"]

    @staticmethod
    def _validate_mime_type(mime_type: str) -> bool:
        return mime_type in current_app.config["DOCUMENT_ALLOWED_MIME_TYPES"]

    @staticmethod
    def _build_storage_path(filename: str) -> str:
        safe_name = secure_filename(filename)
        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        upload_folder = current_app.config["DOCUMENT_UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        return os.path.join(upload_folder, unique_name)

    @staticmethod
    def _scan_for_viruses(storage_path: str) -> bool:
        # Placeholder for antivirus integration.
        # Replace with an actual AV scan implementation.
        return True

    @staticmethod
    def upload_document(file_storage, title: str, case_id, confidential: bool = False):
        if not file_storage:
            raise ValueError("No file provided")

        if not DocumentService._allowed_extension(file_storage.filename):
            raise ValueError("File extension not allowed")

        if not DocumentService._validate_mime_type(file_storage.mimetype):
            raise ValueError("MIME type not allowed")

        content_length = getattr(file_storage, "content_length", None)
        if content_length is not None and content_length > current_app.config["MAX_CONTENT_LENGTH"]:
            raise ValueError("File size exceeds limit")

        storage_path = DocumentService._build_storage_path(file_storage.filename)
        file_storage.save(storage_path)

        if not DocumentService._scan_for_viruses(storage_path):
            os.remove(storage_path)
            raise ValueError("Malicious file content detected")

        existing = Document.query.filter_by(case_id=case_id, title=title).order_by(Document.version.desc()).first()
        version = existing.version + 1 if existing else 1

        document = Document(
            title=title,
            original_filename=file_storage.filename,
            storage_path=storage_path,
            mime_type=file_storage.mimetype,
            file_size=os.path.getsize(storage_path),
            version=version,
            confidential=confidential,
            parent_id=existing.id if existing else None,
            case_id=case_id,
        )
        db.session.add(document)
        db.session.commit()
        return document

    @staticmethod
    def get_document(document_id):
        return Document.query.get_or_404(document_id)

    @staticmethod
    def download_document(document_id):
        return DocumentService.get_document(document_id)

    @staticmethod
    def delete_document(document_id):
        document = Document.query.get_or_404(document_id)
        if os.path.exists(document.storage_path):
            os.remove(document.storage_path)
        db.session.delete(document)
        db.session.commit()
        return document

    @staticmethod
    def list_document_versions(document_id):
        document = DocumentService.get_document(document_id)
        if document.parent_id:
            return [document] + list(document.parent.revisions)
        return [document] + document.revisions
