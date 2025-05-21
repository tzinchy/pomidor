from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ApartmentDifficultues(Base):
    __tablename__ = 'apartment_difficultues'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    difficulty_name = Column(String(225))

class ApartmentStatuses(Base):
    __tablename__ = 'apartment_statuses'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    group_name = Column(String(225))
    status_name = Column(String(225))
    full_name = Column(String(225))

class ApartmentStatusConnections(Base):
    __tablename__ = 'apartment_status_connections'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    status_id = Column(Integer, ForeignKey('renovation.apartment_statuses.id'))
    difficulty_id = Column(Integer, ForeignKey('renovation.apartment_difficultues.id'))
    next_step_term = Column(Integer)
    
    status = relationship("ApartmentStatuses")
    difficulty = relationship("ApartmentDifficultues")

class RelocationTypes(Base):
    __tablename__ = 'relocation_types'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    type = Column(String(225))

class BuildingsOld(Base):
    __tablename__ = 'buildings_old'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    unom = Column(BigInteger, unique=True)
    okrug = Column(String(25))
    district = Column(String(225))
    adress = Column(String(225))
    relocation_type = Column(Integer, ForeignKey('renovation.relocation_types.id'))
    walls_material = Column(String(225))
    repairing_year = Column(Integer)
    floors = Column(Integer)
    num_elevators = Column(Integer)
    num_entrances = Column(Integer)
    dorm = Column(Boolean)
    area_living = Column(Float(7, 1))
    area_non_living = Column(Float(7, 1))
    area_full = Column(Float(7, 1))
    area_outside = Column(Float(7, 1))
    year_wear = Column(Integer)
    year_building = Column(Integer)
    wear_percent = Column(Integer)
    building_series = Column(String(50))
    cad_num = Column(String(225))
    terms_reason = Column(Text)
    unom_ugd = Column(BigInteger)
    moves_outside_district = Column(Boolean, default=False)
    terms = Column(JSON)
    manual_relocation_type = Column(Integer, ForeignKey('renovation.relocation_types.id'))
    okrug_order = Column(Integer)
    status_order = Column(Integer)
    
    relocation_type_rel = relationship("RelocationTypes", foreign_keys=[relocation_type])
    manual_relocation_type_rel = relationship("RelocationTypes", foreign_keys=[manual_relocation_type])

class BuildingsNew(Base):
    __tablename__ = 'buildings_new'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    okrug = Column(String(25))
    district = Column(String(225))
    adress = Column(String(225))
    cad_num = Column(String(225))
    terms = Column(JSON)
    status = Column(String)
    apartmentography = Column(String)

class ConnectionBuildingConstructionTypes(Base):
    __tablename__ = 'connection_building_construction_types'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    type = Column(String(225), nullable=False)
    priority = Column(Integer, nullable=False, default=0)

class ConnectionBuildingMovementTypes(Base):
    __tablename__ = 'connection_building_movement_types'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    type = Column(String(225), nullable=False)
    priority = Column(Integer, nullable=False, default=0)

class ConnectionBuildingConstruction(Base):
    __tablename__ = 'connection_building_construction'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    old_building_id = Column(Integer, ForeignKey('renovation.buildings_old.id'))
    new_building_id = Column(Integer, ForeignKey('renovation.buildings_new.id'))
    connection_type = Column(Integer, ForeignKey('renovation.connection_building_construction_types.id'))
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    is_cancelled = Column(Boolean, nullable=False, default=False)
    notes = Column(Text)
    
    old_building = relationship("BuildingsOld", foreign_keys=[old_building_id])
    new_building = relationship("BuildingsNew", foreign_keys=[new_building_id])
    connection_type_rel = relationship("ConnectionBuildingConstructionTypes")

class ConnectionBuildingMovement(Base):
    __tablename__ = 'connection_building_movement'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    old_building_id = Column(Integer, ForeignKey('renovation.buildings_old.id'))
    new_building_id = Column(Integer, ForeignKey('renovation.buildings_new.id'))
    connection_type = Column(Integer, ForeignKey('renovation.connection_building_movement_types.id'))
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    is_cancelled = Column(Boolean, nullable=False, default=False)
    notes = Column(Text)
    
    old_building = relationship("BuildingsOld", foreign_keys=[old_building_id])
    new_building = relationship("BuildingsNew", foreign_keys=[new_building_id])
    connection_type_rel = relationship("ConnectionBuildingMovementTypes")

class DatesBuildingsOldTypes(Base):
    __tablename__ = 'dates_buildings_old_types'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    type = Column(String(225), nullable=False)
    priority = Column(Integer, nullable=False, default=0)
    short_name = Column(String)

class DatesBuildingsNewTypes(Base):
    __tablename__ = 'dates_buildings_new_types'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    type = Column(String(225), nullable=False)
    priority = Column(Integer, nullable=False, default=0)

class DatesBuildingsOld(Base):
    __tablename__ = 'dates_buildings_old'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('renovation.buildings_old.id'), nullable=False)
    date_type = Column(Integer, ForeignKey('renovation.dates_buildings_old_types.id'), nullable=False)
    control_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    documents = Column(Text)
    notes = Column(Text)
    version = Column(Integer, nullable=False, default=1)
    is_manual = Column(Boolean, nullable=False, default=False)
    
    building = relationship("BuildingsOld")
    date_type_rel = relationship("DatesBuildingsOldTypes")

class DatesBuildingsNew(Base):
    __tablename__ = 'dates_buildings_new'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('renovation.buildings_new.id'), nullable=False)
    date_type = Column(Integer, ForeignKey('renovation.dates_buildings_new_types.id'), nullable=False)
    control_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    documents = Column(Text)
    notes = Column(Text)
    version = Column(Integer, nullable=False, default=1)
    is_manual = Column(Boolean, nullable=False, default=False)
    
    building = relationship("BuildingsNew")
    date_type_rel = relationship("DatesBuildingsNewTypes")

class ApartmentsOldTemp(Base):
    __tablename__ = 'apartments_old_temp'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('renovation.buildings_old.id'))
    affair_id = Column(Integer, unique=True, nullable=False)
    unkv = Column(Integer)
    cad_num = Column(String(225))
    apart_num = Column(String(225))
    apart_type = Column(String(225))
    floor = Column(Integer)
    area_obsh = Column(Float(7, 1))
    room_count = Column(Integer)
    fio = Column(String(225))
    people_count = Column(Integer)
    requirement = Column(String(500))
    old_apart_status = Column(String(500))
    kpu_num = Column(String(225))
    notes = Column(Text)
    area_zhil = Column(Float(7, 1))
    area_zhp = Column(Float(7, 1))
    kpu_close_reason = Column(String(500))
    custody_date = Column(Date)
    dates = Column(JSON, nullable=False, server_default='{}')
    new_aparts = Column(JSON)
    stages_dates = Column(JSON)
    classificator = Column(JSON)
    
    building = relationship("BuildingsOld")

class ApartmentsOld(Base):
    __tablename__ = 'apartments_old'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey('renovation.buildings_old.id'))
    unkv = Column(Integer)
    cad_num = Column(String(225))
    apart_num = Column(String(225))
    apart_type = Column(String(225))
    floor = Column(Integer)
    area_obsh = Column(Float(7, 1))
    room_count = Column(Integer)
    fio = Column(String(225))
    people_count = Column(Integer)
    requirement = Column(String(225))
    old_apart_status = Column(String(225))
    notes = Column(Text)
    affair_id = Column(Integer, unique=True)
    kpu_num = Column(String(225))
    area_zhil = Column(Float(7, 1))
    area_zhp = Column(Float(7, 1))
    
    building = relationship("BuildingsOld")

class ApartmentsNew(Base):
    __tablename__ = 'apartments_new'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer)
    unom = Column(BigInteger)
    adress = Column(String(225))
    apart_num = Column(String(225))
    room_count = Column(Integer)
    area_obsh = Column(Float(7, 1))
    unkv = Column(Integer)
    notes = Column(Text)
    area_zhil = Column(Float(7, 1))
    area_zhp = Column(Float(7, 1))
    cad_num = Column(String(225))
    version = Column(Integer, nullable=False, default=1)

class ApartmentStages(Base):
    __tablename__ = 'apartment_stages'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(225))
    group_name = Column(String(225))
    next_action_text = Column(String(225))
    expected_done_days = Column(Integer)
    camel_case_key = Column(String(225))
    is_manual = Column(Boolean, nullable=False, default=False)
    priority = Column(Integer)
    is_cancelling = Column(Boolean, nullable=False, default=False)
    requires_approval = Column(Boolean, nullable=False, default=False)

class CaseCategories(Base):
    __tablename__ = 'case_categories'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(String(25), primary_key=True)
    name = Column(String(225), nullable=False)
    case_group = Column(Integer)
    dgi_role = Column(String(225), nullable=False)
    need_no_execution = Column(Boolean, default=False)

class ApartmentLitigationsTemp(Base):
    __tablename__ = 'apartment_litigations_temp'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    fssp_updated_at = Column(DateTime(timezone=True), server_default='now()')
    claim_date = Column(Date)
    claim_submission_date = Column(Date)
    claim_num = Column(String(225))
    case_num = Column(String(225))
    case_num_dgi = Column(String(225), unique=True, nullable=False)
    case_category = Column(String(225))
    case_result = Column(String(550))
    last_act_date = Column(Date)
    changes_date = Column(Date)
    fssp_doc_date = Column(Date)
    fssp_institute_date = Column(Date)
    fssp_num = Column(Text)
    fssp_actions_taken = Column(Text)
    fssp_subject_of_proceedings_details = Column(Text)
    fssp_subject_of_proceedings = Column(Text)
    fssp_notes = Column(Text)
    fssp_entry_into_force_date = Column(Date)
    fssp_list_date = Column(Date)
    fssp_list_send_date = Column(Date)
    fssp_status = Column(Text)
    fssp_execution_status = Column(Text)
    fssp_list_num = Column(Text)
    case_category_id = Column(String(25))
    version = Column(Integer, nullable=False, default=1)

class ApartmentLitigations(Base):
    __tablename__ = 'apartment_litigations'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    old_apart_id = Column(Integer, ForeignKey('renovation.apartments_old_temp.id'))
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    claim_date = Column(Date)
    claim_submission_date = Column(Date)
    claim_num = Column(String(225))
    case_num = Column(String(225), nullable=False)
    case_num_dgi = Column(String(225), nullable=False)
    case_category = Column(String(225))
    case_result = Column(String(225))
    last_act_date = Column(Date)
    changes_date = Column(Date)
    hearing_date = Column(Date, nullable=False)
    hearing_result = Column(String(225))
    hearing_result_class = Column(String(225))
    act_date = Column(Date)
    notes = Column(Text)
    subject_of_proceedings = Column(String(225))
    appeal_date = Column(Date)
    final_result = Column(String(225))
    version = Column(Integer, nullable=False, default=1)
    
    old_apart = relationship("ApartmentsOldTemp")

class ApartmentLitigationHearings(Base):
    __tablename__ = 'apartment_litigation_hearings'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    litigation_id = Column(Integer, ForeignKey('renovation.apartment_litigations_temp.id'))
    hearing_date = Column(Date, nullable=False)
    hearing_result = Column(String(225))
    hearing_result_class = Column(String(225))
    act_date = Column(Date)
    notes = Column(Text)
    subject_of_proceedings = Column(String(225), nullable=False)
    appeal_date = Column(Date)
    priority = Column(Integer)
    version = Column(Integer, nullable=False, default=1)
    
    litigation = relationship("ApartmentLitigationsTemp")

class ApartmentLitigationErrants(Base):
    __tablename__ = 'apartment_litigation_errants'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    litigation_id = Column(Integer, ForeignKey('renovation.apartment_litigations_temp.id'))
    errant_type = Column(String(540), nullable=False)
    errant_date = Column(Date, nullable=False)
    errant_complition_date = Column(Date)
    errant_status = Column(String(225))
    version = Column(Integer, nullable=False, default=1)
    
    litigation = relationship("ApartmentLitigationsTemp")

class ApartmentLitigationConnections(Base):
    __tablename__ = 'apartment_litigation_connections'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    old_apart_id = Column(Integer, ForeignKey('renovation.apartments_old_temp.id'), nullable=False)
    litigation_id = Column(Integer, ForeignKey('renovation.apartment_litigations_temp.id'), nullable=False)
    notes = Column(String)
    
    old_apart = relationship("ApartmentsOldTemp")
    litigation = relationship("ApartmentLitigationsTemp")

class LitigationConnectionsTemp(Base):
    __tablename__ = 'litigation_connections_temp'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    old_apart_id = Column(Integer, ForeignKey('renovation.apartments_old_temp.id'), nullable=False)
    litigation_id = Column(Integer, ForeignKey('renovation.apartment_litigations_temp.id'), nullable=False)
    cad_num = Column(String(225))
    case_num_dgi = Column(String(225))
    
    old_apart = relationship("ApartmentsOldTemp")
    litigation = relationship("ApartmentLitigationsTemp")

class ApartmentConnections(Base):
    __tablename__ = 'apartment_connections'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    old_apart_id = Column(Integer, ForeignKey('renovation.apartments_old_temp.id'))
    new_apart_id = Column(Integer, ForeignKey('renovation.apartments_new.id'))
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()')
    notes = Column(Text)
    order_date = Column(Date)
    order_series = Column(String(500))
    order_num = Column(String(225))
    order_reason = Column(Text)
    inspection_date = Column(Date)
    inspection_response = Column(String(500))
    inspection_response_date = Column(Date)
    inspection_response_input_date = Column(DateTime(timezone=True))
    rd_num = Column(String(225))
    rd_date = Column(Date)
    contract_status = Column(String(225))
    contract_date = Column(Date)
    contract_num = Column(String(225))
    contract_prelimenary_signing_date = Column(Date)
    contract_delay_reason = Column(Text)
    contract_delay_comment = Column(Text)
    contract_delay_date = Column(Date)
    status = Column(String(225))
    status_prio = Column(Integer)
    contract_notification_date = Column(Date)
    contract_notification_num = Column(String(225))
    contract_creation_date = Column(Date)
    version = Column(Integer, nullable=False, default=1)
    
    old_apart = relationship("ApartmentsOldTemp")
    new_apart = relationship("ApartmentsNew")

class Objects(Base):
    __tablename__ = 'objects'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    code = Column(BigInteger)
    objectnotes = Column(String(5000))
    municipaldistrict = Column(String(225))
    district = Column(String(225))
    address2 = Column(String(225))
    apartmentnumber = Column(Integer)
    quantityroom = Column(Integer)
    sectionhouse = Column(Integer)
    floor = Column(Integer)
    area = Column(Float(7, 1))
    allarea = Column(Float(7, 1))
    livingspace = Column(Float(7, 1))
    cadastrnumber = Column(String(225))
    categoryroom = Column(String(225))
    owner = Column(String(225))
    control = Column(Boolean)
    series = Column(String(225))
    information = Column(String(225))
    arealtype = Column(String(225))
    resource = Column(String(225))
    state = Column(String(225))
    givesubject = Column(String(225))
    areaadmin = Column(String(225))
    purpose = Column(String(225))

class Subjects(Base):
    __tablename__ = 'subjects'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    unom = Column(BigInteger)
    kpu_number = Column(String(5000))
    lastname = Column(String(5000))
    firstname = Column(String(5000))
    patronymic = Column(String(5000))
    viewsubject = Column(String(5000))
    address2 = Column(String(5000))
    apartmentnumber = Column(Integer)
    roomnumber = Column(Integer)
    apartmenttype = Column(String(5000))
    quantityroom = Column(Integer)
    allarea = Column(Float(7, 1))
    livingspace = Column(Float(7, 1))
    category = Column(String(5000))
    quantitypeople = Column(Integer)
    quantityowner = Column(Integer)
    registrationpeople = Column(Integer)
    floor = Column(Integer)
    sectionhouse = Column(Integer)
    subject = Column(String(5000))
    subjectstatus = Column(String(5000))
    sectionposition = Column(Integer)
    notes = Column(String(5000))
    area = Column(Float(7, 1))
    dateprg = Column(Date)
    legalbasis = Column(String(5000))
    pacttype = Column(String(5000))
    informing = Column(String(5000))

class SelectionApartments(Base):
    __tablename__ = 'selection_apartments'
    __table_args__ = {'schema': 'renovation'}
    
    id = Column(Integer, primary_key=True)
    sentencedate = Column(Date)
    givedate = Column(Date)
    registry = Column(Date)
    answerdate = Column(DateTime(timezone=True))
    sentencenumber = Column(Integer)
    selectionaction = Column(String(1000))
    conditions = Column(String(225))
    notes = Column(String(5000))
    claim = Column(String(5000))
    ordinal = Column(Integer)
    subjectid = Column(Integer, ForeignKey('renovation.subjects.id'))
    objectid = Column(Integer, ForeignKey('renovation.objects.id'))
    result = Column(String(225))
    archives = Column(Boolean)
    subjectarea = Column(Float(7, 1))
    objectsallarea = Column(Float(7, 1))
    decreenumber = Column(Integer)
    decreedate = Column(Date)
    agrementdate = Column(Date)
    
    subject = relationship("Subjects")
    object = relationship("Objects")