from sqlalchemy import Column, Integer, String, Enum
from database import Base, session

class OutreachStatus(Enum):
    NOT_SENT = 'not_sent'
    SENT = 'sent'
    FAILED = 'failed'
    PENDING = 'pending'


class ProfileOutreach(Base):
    __tablename__ = 'profile_outreach'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile = Column("profile", String(255), unique=True)
    message_sent = Column("message_sent", String(255), default=None)
    outreach_status = Column(Enum(OutreachStatus.NOT_SENT, OutreachStatus.SENT, OutreachStatus.FAILED, OutreachStatus.PENDING, name="OutreachStatus"))

    def __init__(self, profile,outreach_status, message_sent=None):
        self.profile = profile
        self.message_sent = message_sent
        self.outreach_status = outreach_status

    @classmethod
    def create(cls, profile, message_sent, outreach_status):
        new_profile_outreach = cls(profile=profile, message_sent=message_sent, outreach_status=outreach_status)
        session.add(new_profile_outreach)
        session.commit()
    
    @classmethod
    def add_unique_profile(cls, profile, outreach_status):
        existing_profile = session.query(cls).filter_by(profile=profile).first()
        if not existing_profile:
            new_profile_outreach = cls(profile=profile, outreach_status=outreach_status)
            session.add(new_profile_outreach)
            session.commit()
            return new_profile_outreach
        
        return existing_profile
    
    @classmethod
    def get_first_failed_profile(cls):
        failed_profile = session.query(cls).filter_by(outreach_status=OutreachStatus.FAILED).with_for_update().first()
        if failed_profile:
            failed_profile.outreach_status = OutreachStatus.PENDING
            session.commit()
            return failed_profile
    
    @classmethod
    def get_first_not_sent_profile(cls):
        not_sent_profile = session.query(cls).filter_by(outreach_status=OutreachStatus.NOT_SENT).with_for_update().first()
        #get the first not sent profile and update to pending state
        if not_sent_profile:
            not_sent_profile.outreach_status = OutreachStatus.PENDING
            session.commit()
            return not_sent_profile
        else:
            return None
        
    @classmethod
    def set_message_sent_and_status(cls, profile, message_sent):
        profile = session.query(cls).filter_by(profile = profile).first()
        if profile:
            profile.outreach_status = OutreachStatus.SENT
            profile.message_sent = message_sent
            session.commit()
            return profile
        
    @classmethod
    def set_failed_status(cls, profile):
        profile = session.query(cls).filter_by(profile = profile).first()
        if profile:
            profile.outreach_status = OutreachStatus.FAILED
            session.commit()
            return profile

