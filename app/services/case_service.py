from app.extensions import db
from app.models import Case


class CaseService:
    @staticmethod
    def list_cases():
        return Case.query.order_by(Case.created_at.desc()).all()

    @staticmethod
    def search_cases(query):
        search_term = f"%{query}%"
        return (
            Case.query.filter(
                db.or_(
                    Case.title.ilike(search_term),
                    Case.description.ilike(search_term),
                )
            )
            .order_by(Case.created_at.desc())
            .all()
        )

    @staticmethod
    def create_case(title, description, client_id):
        case = Case(
            title=title,
            description=description,
            client_id=client_id,
            status="open",
        )
        db.session.add(case)
        db.session.commit()
        return case

    @staticmethod
    def update_case(case_id, title=None, description=None, status=None):
        case = Case.query.get_or_404(case_id)
        if title is not None:
            case.title = title
        if description is not None:
            case.description = description
        if status is not None:
            case.status = status
        db.session.commit()
        return case

    @staticmethod
    def close_case(case_id):
        case = Case.query.get_or_404(case_id)
        case.status = "closed"
        db.session.commit()
        return case
