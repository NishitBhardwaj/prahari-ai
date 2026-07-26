"""Models package — imports all models to ensure they register with Base.metadata."""

from app.db.postgres.models.user import User, UserRole  # noqa: F401
from app.db.postgres.models.station import District, PoliceStation  # noqa: F401
from app.db.postgres.models.case import Case  # noqa: F401
from app.db.postgres.models.person import Person  # noqa: F401
from app.db.postgres.models.accused import AccusedRecord, Victim, Complainant, Witness  # noqa: F401
from app.db.postgres.models.evidence import Evidence, FSLReport, InvestigationDiary, CrimeEvent  # noqa: F401
from app.db.postgres.models.chargesheet import Chargesheet, Court, CourtProceeding  # noqa: F401
from app.db.postgres.models.gang import (  # noqa: F401
    Gang, Employee, Vehicle, MobileDevice,
    CallDetailRecord, BankAccount, FinancialTransaction,
    NarrativeDocument, AuditLog,
)

from app.db.postgres.models.case_state_transition import CaseStateTransition, CaseState  # noqa: F401
from app.db.postgres.models.timeline_event import TimelineEvent  # noqa: F401
from app.db.postgres.models.investigation_task import InvestigationTask, TaskStatus, TaskPriority  # noqa: F401
from app.db.postgres.models.case_relationship import CaseRelationship  # noqa: F401
from app.db.postgres.models.evidence_version import EvidenceVersion  # noqa: F401
