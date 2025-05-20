from dataclasses import dataclass, field
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class ProjectManagementSettings:
    DB_HOST: str = os.environ.get("DB_HOST")
    DB_PORT: str = os.environ.get("DB_PORT")
    DB_USER: str = os.environ.get("DB_USER")
    DB_PASSWORD: str = os.environ.get("DB_PASS")
    DB_NAME: str = os.environ.get("DB_NAME")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

@dataclass
class DashboardSetting:
    DB_DASHBORD_HOST: str = os.environ.get("DB_DASHBORD_HOST")
    DB_DASHBORD_PORT: str = os.environ.get("DB_DASHBORD_PORT")
    DB_DASHBORD_USER: str = os.environ.get("DB_DASHBORD_USER")
    DB_DASHBORD_PASSWORD: str = os.environ.get("DB_DASHBORD_PASS")
    DB_DASHBORD_NAME: str = os.environ.get("DB_DASHBORD_NAME")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_DASHBORD_USER}:{self.DB_DASHBORD_PASSWORD}@{self.DB_DASHBORD_HOST}:{self.DB_DASHBORD_PORT}/{self.DB_DASHBORD_NAME}"

@dataclass
class Settings:
    project_management_setting: ProjectManagementSettings = field(default_factory=ProjectManagementSettings)
    dashboard_setting: DashboardSetting = field(default_factory=DashboardSetting)

settings = Settings()

tables = {
    # Independent tables without foreign key dependencies
    "renovation.apartment_difficultues": ["id", "difficulty_name"],
    "renovation.apartment_stages": ["id", "name", "group_name", "next_action_text", "expected_done_days", "camel_case_key", "is_manual", "priority", "is_cancelling", "requires_approval"],
    "renovation.apartment_statuses": ["id", "group_name", "status_name", "full_name"],
    "renovation.case_categories": ["id", "name", "case_group", "dgi_role", "need_no_execution"],
    "renovation.connection_building_construction_types": ["id", "type", "priority"],
    "renovation.connection_building_movement_types": ["id", "type", "priority"],
    "renovation.dates_buildings_new_types": ["id", "type", "priority"],
    "renovation.dates_buildings_old_types": ["id", "type", "priority", "short_name"],
    "renovation.relocation_types": ["id", "type"],
    
    # Building tables (needed for apartments)
    "renovation.buildings_old": ["id", "unom", "okrug", "district", "adress", "relocation_type", "walls_material", "repairing_year", "floors", "num_elevators", "num_entrances", "dorm", "area_living", "area_non_living", "area_full", "area_outside", "year_wear", "year_building", "wear_percent", "building_series", "cad_num", "terms_reason", "unom_ugd", "moves_outside_district", "terms", "manual_relocation_type", "okrug_order", "status_order"],
    "renovation.buildings_new": ["id", "okrug", "district", "adress", "cad_num", "terms", "status", "apartmentography"],
    
    # Old apartments (needed for many other tables)
    "renovation.apartments_old": ["id", "building_id", "unkv", "cad_num", "apart_num", "apart_type", "floor", "area_obsh", "room_count", "fio", "people_count", "requirement", "old_apart_status", "notes", "affair_id", "kpu_num", "area_zhil", "area_zhp"],
    "renovation.apartments_old_temp": ["id", "building_id", "affair_id", "unkv", "cad_num", "apart_num", "apart_type", "floor", "area_obsh", "room_count", "fio", "people_count", "requirement", "old_apart_status", "kpu_num", "notes", "area_zhil", "area_zhp", "kpu_close_reason", "custody_date", "dates", "new_aparts", "stages_dates", "classificator"],
    
    # New apartments (needed for connections)
    "renovation.apartments_new": ["id", "building_id", "unom", "adress", "apart_num", "room_count", "area_obsh", "unkv", "notes", "area_zhil", "area_zhp", "cad_num", "version"],
    
    # Building dates (depend on buildings)
    "renovation.dates_buildings_old": ["id", "building_id", "date_type", "control_date", "created_at", "updated_at", "documents", "notes", "version", "is_manual"],
    "renovation.dates_buildings_new": ["id", "building_id", "date_type", "control_date", "created_at", "updated_at", "documents", "notes", "version", "is_manual"],
    
    # Building connections (depend on buildings)
    "renovation.connection_building_construction": ["id", "old_building_id", "new_building_id", "connection_type", "created_at", "updated_at", "is_cancelled", "notes"],
    "renovation.connection_building_movement": ["id", "old_building_id", "new_building_id", "connection_type", "created_at", "updated_at", "is_cancelled", "notes"],
    
    # Litigations (depend on old apartments)
    "renovation.apartment_litigations_temp": ["id", "created_at", "updated_at", "fssp_updated_at", "claim_date", "claim_submission_date", "claim_num", "case_num", "case_num_dgi", "case_category", "case_result", "last_act_date", "changes_date", "fssp_doc_date", "fssp_institute_date", "fssp_num", "fssp_actions_taken", "fssp_subject_of_proceedings_details", "fssp_subject_of_proceedings", "fssp_notes", "fssp_entry_into_force_date", "fssp_list_date", "fssp_list_send_date", "fssp_status", "fssp_execution_status", "fssp_list_num", "case_category_id", "version"],
    "renovation.apartment_litigations": ["id", "old_apart_id", "created_at", "updated_at", "claim_date", "claim_submission_date", "claim_num", "case_num", "case_num_dgi", "case_category", "case_result", "last_act_date", "changes_date", "hearing_date", "hearing_result", "hearing_result_class", "act_date", "notes", "subject_of_proceedings", "appeal_date", "final_result", "version"],
    
    # Litigation connections (depend on litigations and apartments)
    "renovation.litigation_connections_temp": ["id", "old_apart_id", "litigation_id", "cad_num", "case_num_dgi"],
    
    # Apartment connections (depend on both old and new apartments)
    "renovation.apartment_connections": ["id", "old_apart_id", "new_apart_id", "created_at", "updated_at", "notes", "order_date", "order_series", "order_num", "order_reason", "inspection_date", "inspection_response", "inspection_response_date", "inspection_response_input_date", "rd_num", "rd_date", "contract_status", "contract_date", "contract_num", "contract_prelimenary_signing_date", "contract_delay_reason", "contract_delay_comment", "contract_delay_date", "status", "status_prio", "contract_notification_date", "contract_notification_num", "contract_creation_date", "version"],
    "renovation.apartment_litigation_connections": ["id", "created_at", "updated_at", "old_apart_id", "litigation_id", "notes"],
    
    # Litigation details (depend on litigations)
    "renovation.apartment_litigation_errants": ["id", "litigation_id", "errant_type", "errant_date", "errant_complition_date", "errant_status", "version"],
    "renovation.apartment_litigation_hearings": ["id", "litigation_id", "hearing_date", "hearing_result", "hearing_result_class", "act_date", "notes", "subject_of_proceedings", "appeal_date", "priority", "version"],
    
    # Status connections (depend on statuses and difficulties)
    "renovation.apartment_status_connections": ["id", "status_id", "difficulty_id", "next_step_term"],
    
    # Other tables
    "renovation.objects": ["id", "code", "objectnotes", "municipaldistrict", "district", "address2", "apartmentnumber", "quantityroom", "sectionhouse", "floor", "area", "allarea", "livingspace", "cadastrnumber", "categoryroom", "owner", "control", "series", "information", "arealtype", "resource", "state", "givesubject", "areaadmin", "purpose"],
    "renovation.selection_apartments": ["id", "sentencedate", "givedate", "registry", "answerdate", "sentencenumber", "selectionaction", "conditions", "notes", "claim", "ordinal", "subjectid", "objectid", "result", "archives", "subjectarea", "objectsallarea", "decreenumber", "decreedate", "agrementdate"],
    "renovation.subjects": ["id", "unom", "kpu_number", "lastname", "firstname", "patronymic", "viewsubject", "address2", "apartmentnumber", "roomnumber", "apartmenttype", "quantityroom", "allarea", "livingspace", "category", "quantitypeople", "quantityowner", "registrationpeople", "floor", "sectionhouse", "subject", "subjectstatus", "sectionposition", "notes", "area", "dateprg", "legalbasis", "pacttype", "informing"],
}
