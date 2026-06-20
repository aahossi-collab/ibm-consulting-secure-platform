from flask import abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from app.auth.decorators import role_required
from app.models import Case, Document
from app.security.audit import AuditLogger
from app.security.rbac import (
    PERMISSION_MANAGE_CASES,
    PERMISSION_MANAGE_DOCUMENTS,
    PERMISSION_UPLOAD_DOCUMENT,
    PERMISSION_VIEW_CASE,
    require_permission,
)
from app.services.case_service import CaseService
from app.services.document_service import DocumentService
from . import client_bp
from .forms import (
    CaseCreateForm,
    CaseSearchForm,
    CaseUpdateForm,
    DocumentUploadForm,
)


@client_bp.route("/")
@login_required
@role_required("Client")
def index():
    return render_template("client/dashboard.html")


@client_bp.route("/cases")
@login_required
@require_permission(PERMISSION_VIEW_CASE)
def list_cases():
    query = request.args.get("q", "")
    if query:
        cases = CaseService.search_cases(query)
    else:
        cases = CaseService.list_cases()
    return render_template("client/cases/list.html", cases=cases, query=query)


@client_bp.route("/cases/create", methods=["GET", "POST"])
@login_required
@require_permission(PERMISSION_MANAGE_CASES)
def create_case():
    form = CaseCreateForm()
    if form.validate_on_submit():
        CaseService.create_case(
            title=form.title.data,
            description=form.description.data,
            client_id=form.client_id.data,
        )
        flash("Case created successfully.", "success")
        return redirect(url_for("client.list_cases"))
    return render_template("client/cases/create.html", form=form)


@client_bp.route("/cases/<uuid:case_id>/edit", methods=["GET", "POST"])
@login_required
@require_permission(PERMISSION_MANAGE_CASES)
def update_case(case_id):
    case = Case.query.get_or_404(case_id)
    form = CaseUpdateForm(obj=case)
    if form.validate_on_submit():
        CaseService.update_case(
            case_id=case.id,
            title=form.title.data,
            description=form.description.data,
            status=form.status.data,
        )
        flash("Case updated successfully.", "success")
        return redirect(url_for("client.list_cases"))
    return render_template("client/cases/edit.html", form=form, case=case)


@client_bp.route("/cases/<uuid:case_id>/close", methods=["POST"])
@login_required
@require_permission(PERMISSION_MANAGE_CASES)
def close_case(case_id):
    CaseService.close_case(case_id)
    flash("Case closed successfully.", "success")
    return redirect(url_for("client.list_cases"))


@client_bp.route("/cases/<uuid:case_id>/documents")
@login_required
@require_permission(PERMISSION_VIEW_CASE)
def list_documents(case_id):
    case = Case.query.get_or_404(case_id)
    documents = case.documents.order_by(Document.version.desc()).all()
    return render_template(
        "client/documents/list.html",
        case=case,
        documents=documents,
    )


@client_bp.route("/cases/<uuid:case_id>/documents/upload", methods=["GET", "POST"])
@login_required
@require_permission(PERMISSION_UPLOAD_DOCUMENT)
def upload_document(case_id):
    form = DocumentUploadForm()
    if form.validate_on_submit():
        file_storage = request.files.get("file")
        document = DocumentService.upload_document(
            file_storage,
            title=form.title.data,
            case_id=case_id,
            confidential=form.confidential.data,
        )
        AuditLogger.log_document_uploaded(current_user, document.id)
        flash("Document uploaded successfully.", "success")
        return redirect(url_for("client.list_documents", case_id=case_id))

    return render_template("client/documents/upload.html", form=form)


@client_bp.route("/documents/<uuid:document_id>/download")
@login_required
@require_permission(PERMISSION_UPLOAD_DOCUMENT)
def download_document(document_id):
    document = DocumentService.download_document(document_id)
    AuditLogger.log_document_downloaded(current_user, document.id)
    try:
        return send_file(
            document.storage_path,
            as_attachment=True,
            download_name=document.original_filename,
            mimetype=document.mime_type,
        )
    except FileNotFoundError:
        abort(404)


@client_bp.route("/documents/<uuid:document_id>/delete", methods=["POST"])
@login_required
@require_permission(PERMISSION_UPLOAD_DOCUMENT)
def delete_document(document_id):
    document = DocumentService.delete_document(document_id)
    AuditLogger.log_document_deleted(current_user, document.id)
    flash("Document deleted successfully.", "success")
    return redirect(url_for("client.list_documents", case_id=document.case_id))
