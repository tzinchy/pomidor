import pytest
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.repository.database import auth_session
from app.models.action import Action
from app.models.department import Department
from app.models.district import District
from app.models.district_group import DistrictGroup
from app.models.group import Group
from app.models.management import Management
from app.models.position_list import PositionList
from app.models.role import Role
from app.models.service import Service
from app.models.service_table import ServiceTable


@pytest.mark.asyncio
async def test_action_model():
    """Test Action model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(Action))
        actions = result.scalars().all()
        assert isinstance(actions, list)
        for action in actions:
            assert hasattr(action, 'action_id')


@pytest.mark.asyncio
async def test_department_model():
    """Test Department model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(Department))
        departments = result.scalars().all()
        assert isinstance(departments, list)
        for department in departments:
            assert hasattr(department, 'department_id')


@pytest.mark.asyncio
async def test_district_model():
    """Test District model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(District))
        districts = result.scalars().all()
        assert isinstance(districts, list)
        for district in districts:
            assert hasattr(district, 'district_id')


@pytest.mark.asyncio
async def test_district_group_model():
    """Test DistrictGroup model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(DistrictGroup))
        district_groups = result.scalars().all()
        assert isinstance(district_groups, list)
        for district_group in district_groups:
            assert hasattr(district_group, 'district_group_id')


@pytest.mark.asyncio
async def test_role_model():
    """Test Role model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        assert isinstance(roles, list)
        for role in roles:
            assert hasattr(role, 'role_id')


@pytest.mark.asyncio
async def test_service_model():
    """Test Service model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(Service))
        services = result.scalars().all()
        assert isinstance(services, list)
        for service in services:
            assert hasattr(service, 'service_id')


@pytest.mark.asyncio
async def test_position_list_model():
    """Test PositionList model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(PositionList))
        positions = result.scalars().all()
        assert isinstance(positions, list)
        for position in positions:
            assert hasattr(position, 'position_id')


@pytest.mark.asyncio
async def test_service_table_model():
    """Test ServiceTable model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(ServiceTable))
        service_tables = result.scalars().all()
        assert isinstance(service_tables, list)
        for service_table in service_tables:
            assert hasattr(service_table, 'service_table_id')


@pytest.mark.asyncio
async def test_management_model():
    """Test Management model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(Management))
        managements = result.scalars().all()
        assert isinstance(managements, list)
        for management in managements:
            assert hasattr(management, 'management_id')


@pytest.mark.asyncio
async def test_group_model():
    """Test Group model can be queried successfully."""
    async with auth_session() as session:
        result = await session.execute(select(Group))
        groups = result.scalars().all()
        assert isinstance(groups, list)
        for group in groups:
            assert hasattr(group, 'group_id')