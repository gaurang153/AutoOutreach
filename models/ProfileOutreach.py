from sqlalchemy import Column, Integer, String, Enum, Boolean, TIMESTAMP
from database import Base, session
from datetime import datetime, timedelta

class OutreachStatus(Enum):
    NOT_SENT = 'not_sent'
    SENT = 'sent'
    FAILED = 'failed'
    PENDING = 'pending'


class ProfileOutreach(Base):
    __tablename__ = 'profile_outreach'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile = Column("profile", String(255), unique=True)
    profile_name = Column("profile_name", String(255), default=None)
    message_sent = Column("message_sent", String(255), default=None)
    sent_time = Column("sent_time", TIMESTAMP)
    outreach_status = Column(Enum(OutreachStatus.NOT_SENT, OutreachStatus.SENT, OutreachStatus.FAILED, OutreachStatus.PENDING, name="OutreachStatus"))
    city = Column("city", String(255), default=None)
    industry = Column("industry", String(255), default=None)
    replied = Column("replied", Boolean, default=None)
    replied_message = Column("replied_message", String(255), default=None)
    followed_up = Column("followed_up", Boolean, default=False)
    sent_by = Column("sent_by", String(255), default=None)

    def __init__(self, profile,outreach_status, message_sent=None, city=None, industry=None, replied=None, sent_time=None, sent_by=None, followed_up=False, profile_name=None, replied_message=None):
        self.profile = profile
        self.profile_name = profile_name
        self.message_sent = message_sent
        self.outreach_status = outreach_status
        self.city = city
        self.industry = industry
        self.replied = replied
        self.replied_message = replied_message
        self.sent_time = sent_time
        self.sent_by = sent_by
        self.followed_up = followed_up

    @classmethod
    def create(cls, profile, message_sent, outreach_status):
        new_profile_outreach = cls(profile=profile, message_sent=message_sent, outreach_status=outreach_status)
        session.add(new_profile_outreach)
        session.commit()
    
    @classmethod
    def add_unique_profile(cls, profile, outreach_status, city, industry):
        existing_profile = session.query(cls).filter_by(profile=profile).first()
        if not existing_profile:
            new_profile_outreach = cls(profile=profile, outreach_status=outreach_status, city=city, industry=industry)
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
    def set_message_sent_and_status(cls, profile, message_sent, sent_by):
        profile = session.query(cls).filter_by(profile = profile).first()
        if profile:
            profile.outreach_status = OutreachStatus.SENT
            profile.message_sent = message_sent
            profile.sent_time = datetime.now()
            profile.sent_by = sent_by
            session.commit()
            return profile
        
    @classmethod
    def set_failed_status(cls, profile):
        profile = session.query(cls).filter_by(profile = profile).first()
        if profile:
            profile.outreach_status = OutreachStatus.FAILED
            session.commit()
            return profile
        
    @classmethod
    def get_follow_up_profiles(cls, sent_by):
        current_time = datetime.now()
        follow_up_threshold = current_time - timedelta(hours=48)
        re_follow_up_threshold = current_time - timedelta(hours=96)
        follow_up_profiles = session.query(cls).filter(
            cls.sent_by==sent_by,
            cls.sent_time.isnot(None),
            cls.replied.isnot(True),
            cls.sent_time < follow_up_threshold,
            cls.sent_time > re_follow_up_threshold,
            cls.followed_up == False
            ).all()
        return follow_up_profiles
    
    @classmethod
    def get_re_follow_up_profiles(cls, sent_by):
        current_time = datetime.now()
        re_follow_up_threshold = current_time - timedelta(hours=96)
        re_follow_up_profiles = session.query(cls).filter(
            cls.sent_by==sent_by,
            cls.sent_time < re_follow_up_threshold,
            cls.replied == False,
            cls.followed_up == False
            ).all()
        return re_follow_up_profiles
    
    @classmethod
    def set_replied(cls, profile_name, replied):
        profile = session.query(cls).filter_by(profile = profile_name).first()
        profile.replied = replied
        session.commit()

    @classmethod
    def set_followed_up(cls, profile_name, followed_up):
        profile = session.query(cls).filter_by(profile = profile_name).first()
        profile.followed_up = followed_up
        session.commit()

    @classmethod
    def set_profile_name(cls, profile_name, profile_id):
        profile = session.query(cls).filter_by(id = profile_id).first()
        profile.profile_name = profile_name
        session.commit()

    @classmethod
    def set_replied_message(cls, profile, replied_message):
        profile = session.query(cls).filter_by(profile = profile).first()
        if profile:
            profile.replied_message = replied_message
        session.commit()

    @classmethod
    def get_profile_outreach(cls, profile):
        profile_outreach = session.query(cls).filter_by(profile = profile).first()
        return profile_outreach
    
    @classmethod
    def get_profile_outreach_by_id(cls, profile_id):
        profile_outreach = session.query(cls).filter_by(id = profile_id).first()
        return profile_outreach

