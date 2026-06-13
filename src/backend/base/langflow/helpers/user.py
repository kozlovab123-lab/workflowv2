from fastapi import HTTPException
from lfx.services.deps import session_scope_readonly
from sqlmodel import select

from langflow.services.database.models.flow.model import Flow
from langflow.services.database.models.user.model import User, UserRead
from langflow.services.database.utils import parse_uuid, session_get_by_pk


async def get_user_by_flow_id_or_endpoint_name(flow_id_or_name: str) -> UserRead | None:
    async with session_scope_readonly() as session:
        try:
            flow_id = parse_uuid(flow_id_or_name, field_name="flow_id")
            flow = await session_get_by_pk(session, Flow, flow_id)
        except ValueError:
            stmt = select(Flow).where(Flow.endpoint_name == flow_id_or_name)
            flow = (await session.exec(stmt)).first()

        if flow is None:
            raise HTTPException(status_code=404, detail=f"Flow identifier {flow_id_or_name} not found")

        user = await session_get_by_pk(session, User, flow.user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User for flow {flow_id_or_name} not found")

        return UserRead.model_validate(user, from_attributes=True)
