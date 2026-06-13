import asyncio
import json
from collections.abc import Sequence
from datetime import datetime, timezone
from uuid import UUID

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from lfx.log.logger import logger
from lfx.utils.async_helpers import run_until_complete
from sqlalchemy import delete, text
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from langflow.schema.message import Message
from langflow.services.database.models.message.model import MessageRead, MessageTable
from langflow.services.database.utils import session_get_by_pk
from langflow.services.deps import session_scope
from lfx.utils.session_utils import coerce_uuid, normalize_session_id, parse_flow_id


_MESSAGE_ORDER_COLUMNS = frozenset({"timestamp", "sender", "sender_name", "session_id"})


def _build_message_query_sql(
    sender: str | None = None,
    sender_name: str | None = None,
    session_id: str | UUID | None = None,
    context_id: str | None = None,
    order_by: str | None = "timestamp",
    order: str | None = "DESC",
    flow_id: UUID | None = None,
    limit: int | None = None,
) -> tuple[str, dict]:
    """Build a raw SQL query for messages.

    Avoids SQLAlchemy UUID ORM hydration, which fails on SQLite when UUIDs are
    stored as 32-char hex strings (AttributeError: 'str' object has no attribute 'hex').
    """
    conditions = ["error = 0"]
    params: dict = {}

    if sender:
        conditions.append("sender = :sender")
        params["sender"] = sender
    if sender_name:
        conditions.append("sender_name = :sender_name")
        params["sender_name"] = sender_name
    if session_id:
        conditions.append("session_id = :session_id")
        params["session_id"] = str(session_id)
    if context_id:
        conditions.append("context_id = :context_id")
        params["context_id"] = str(context_id)
    if flow_id:
        parsed_flow_id = parse_flow_id(flow_id)
        if parsed_flow_id is not None:
            conditions.append(
                "(REPLACE(CAST(flow_id AS TEXT), '-', '') = :flow_id_hex "
                "OR CAST(flow_id AS TEXT) = :flow_id_dashed)"
            )
            params["flow_id_hex"] = str(parsed_flow_id).replace("-", "")
            params["flow_id_dashed"] = str(parsed_flow_id)
        else:
            conditions.append("CAST(flow_id AS TEXT) = :flow_id_raw")
            params["flow_id_raw"] = str(flow_id)

    order_column = order_by if order_by in _MESSAGE_ORDER_COLUMNS else "timestamp"
    order_direction = "ASC" if order == "ASC" else "DESC"
    limit_clause = f" LIMIT {int(limit)}" if limit else ""

    sql = (
        f"SELECT id, timestamp, sender, sender_name, session_id, context_id, text, "
        f"files, error, edit, flow_id, properties, category, content_blocks, session_metadata "
        f"FROM message WHERE {' AND '.join(conditions)} "
        f"ORDER BY {order_column} {order_direction}{limit_clause}"
    )
    return sql, params


def _normalize_message_timestamp(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.strftime("%Y-%m-%d %H:%M:%S %Z")
    if isinstance(value, str):
        normalized = value.replace(" UTC", "").strip()
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                parsed = datetime.strptime(normalized, fmt)
                return parsed.replace(tzinfo=timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
            except ValueError:
                continue
    return str(value)


async def _message_row_to_model(row: dict) -> Message:
    data = dict(row)
    if data.get("timestamp") is not None:
        data["timestamp"] = _normalize_message_timestamp(data["timestamp"])
    for field in ("files", "properties", "content_blocks", "session_metadata"):
        value = data.get(field)
        if isinstance(value, str):
            try:
                data[field] = json.loads(value)
            except json.JSONDecodeError:
                pass
    for uuid_field in ("id", "flow_id"):
        if data.get(uuid_field) is not None:
            parsed = parse_flow_id(data[uuid_field])
            data[uuid_field] = str(parsed) if parsed else str(data[uuid_field])
    return await Message.create(**data)


def get_messages(
    sender: str | None = None,
    sender_name: str | None = None,
    session_id: str | UUID | None = None,
    context_id: str | None = None,
    order_by: str | None = "timestamp",
    order: str | None = "DESC",
    flow_id: UUID | None = None,
    limit: int | None = None,
) -> list[Message]:
    """DEPRECATED - Retrieves messages from the monitor service based on the provided filters.

    DEPRECATED: Use `aget_messages` instead.

    Args:
        sender (Optional[str]): The sender of the messages (e.g., "Machine" or "User")
        sender_name (Optional[str]): The name of the sender.
        session_id (Optional[str]): The session ID associated with the messages.
        context_id (Optional[str]): The context ID associated with the messages.
        order_by (Optional[str]): The field to order the messages by. Defaults to "timestamp".
        order (Optional[str]): The order in which to retrieve the messages. Defaults to "DESC".
        flow_id (Optional[UUID]): The flow ID associated with the messages.
        limit (Optional[int]): The maximum number of messages to retrieve.

    Returns:
        List[Data]: A list of Data objects representing the retrieved messages.
    """
    return run_until_complete(
        aget_messages(
            sender,
            sender_name,
            session_id,
            context_id,
            order_by,
            order,
            flow_id,
            limit,
        )
    )


async def aget_messages(
    sender: str | None = None,
    sender_name: str | None = None,
    session_id: str | UUID | None = None,
    context_id: str | None = None,
    order_by: str | None = "timestamp",
    order: str | None = "DESC",
    flow_id: UUID | None = None,
    limit: int | None = None,
) -> list[Message]:
    """Retrieves messages from the monitor service based on the provided filters.

    Args:
        sender (Optional[str]): The sender of the messages (e.g., "Machine" or "User")
        sender_name (Optional[str]): The name of the sender.
        session_id (Optional[str]): The session ID associated with the messages.
        context_id (Optional[str]): The context ID associated with the messages.
        order_by (Optional[str]): The field to order the messages by. Defaults to "timestamp".
        order (Optional[str]): The order in which to retrieve the messages. Defaults to "DESC".
        flow_id (Optional[UUID]): The flow ID associated with the messages.
        limit (Optional[int]): The maximum number of messages to retrieve.

    Returns:
        List[Data]: A list of Data objects representing the retrieved messages.
    """
    normalized_session_id = normalize_session_id(session_id)
    sql, params = _build_message_query_sql(
        sender, sender_name, normalized_session_id, context_id, order_by, order, flow_id, limit
    )
    async with session_scope() as session:
        result = await session.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]
        return [await _message_row_to_model(row) for row in rows]


def add_messages(messages: Message | list[Message], flow_id: str | UUID | None = None):
    """DEPRECATED - Add a message to the monitor service.

    DEPRECATED: Use `aadd_messages` instead.
    """
    return run_until_complete(aadd_messages(messages, flow_id=flow_id))


async def aadd_messages(messages: Message | list[Message], flow_id: str | UUID | None = None):
    """Add a message to the monitor service."""
    if not isinstance(messages, list):
        messages = [messages]

    # Check if all messages are Message instances (either from langflow or lfx)
    for message in messages:
        # Accept Message instances from both langflow and lfx packages
        is_valid_message = isinstance(message, Message) or (
            hasattr(message, "__class__") and message.__class__.__name__ in ["Message", "ErrorMessage"]
        )
        if not is_valid_message:
            types = ", ".join([str(type(msg)) for msg in messages])
            msg = f"The messages must be instances of Message. Found: {types}"
            raise ValueError(msg)

    try:
        messages_models = [MessageTable.from_message(msg, flow_id=flow_id) for msg in messages]
        async with session_scope() as session:
            messages_models = await aadd_messagetables(messages_models, session)
        return [await Message.create(**message.model_dump()) for message in messages_models]
    except Exception as e:
        await logger.aexception(e)
        raise


async def aupdate_messages(messages: Message | list[Message]) -> list[Message]:
    if not isinstance(messages, list):
        messages = [messages]

    async with session_scope() as session:
        updated_messages: list[MessageTable] = []
        for message in messages:
            message_pk = coerce_uuid(message.get_id() if hasattr(message, "get_id") else getattr(message, "id", None))
            if message_pk is None:
                error_message = "Message id is required for update"
                await logger.awarning(error_message)
                raise ValueError(error_message)
            msg = await session_get_by_pk(session, MessageTable, message_pk)
            if msg:
                msg = msg.sqlmodel_update(message.model_dump(exclude_unset=True, exclude_none=True))
                # Convert flow_id to UUID if it's a string preventing error when saving to database
                if msg.flow_id and isinstance(msg.flow_id, str):
                    msg.flow_id = parse_flow_id(msg.flow_id)
                result = session.add(msg)
                if asyncio.iscoroutine(result):
                    await result
                updated_messages.append(msg)
            else:
                error_message = f"Message with id {message.id} not found"
                await logger.awarning(error_message)
                raise ValueError(error_message)

        return [MessageRead.model_validate(message, from_attributes=True) for message in updated_messages]


async def aadd_messagetables(messages: list[MessageTable], session: AsyncSession, retry_count: int = 0):
    """Add messages to the database with retry logic for CancelledError.

    Args:
        messages: List of MessageTable objects to add
        session: Database session
        retry_count: Internal retry counter (max 3 retries to prevent infinite loops)

    This function includes a workaround for CancelledError that can occur during
    session.commit() when called from build_public_tmp but not from build_flow.
    The retry mechanism has a limit to prevent infinite recursion.
    """
    max_retries = 3
    try:
        try:
            for message in messages:
                result = session.add(message)
                if asyncio.iscoroutine(result):
                    await result
            await session.commit()
            # This is a hack.
            # We are doing this because build_public_tmp causes the CancelledError to be raised
            # while build_flow does not.
        except asyncio.CancelledError:
            await session.rollback()
            if retry_count >= max_retries:
                await logger.awarning(
                    f"Max retries ({max_retries}) reached for aadd_messagetables due to CancelledError"
                )
                error_msg = "Add Message operation cancelled after multiple retries"
                raise ValueError(error_msg) from None
            return await aadd_messagetables(messages, session, retry_count + 1)
        for message in messages:
            await session.refresh(message)
    except asyncio.CancelledError as e:
        await logger.aexception(e)
        error_msg = "Operation cancelled"
        raise ValueError(error_msg) from e
    except Exception as e:
        await logger.aexception(e)
        raise

    new_messages = []
    for msg in messages:
        msg.properties = json.loads(msg.properties) if isinstance(msg.properties, str) else msg.properties  # type: ignore[arg-type]
        msg.content_blocks = [json.loads(j) if isinstance(j, str) else j for j in msg.content_blocks]  # type: ignore[arg-type]
        msg.category = msg.category or ""
        new_messages.append(msg)

    return [MessageRead.model_validate(message, from_attributes=True) for message in new_messages]


def delete_messages(session_id: str | None = None, context_id: str | None = None) -> None:
    """DEPRECATED - Delete messages from the monitor service based on the provided session ID.

    DEPRECATED: Use `adelete_messages` instead.

    Args:
        session_id (str): The session ID associated with the messages to delete.
        context_id (str): The context ID associated with the messages to delete.
    """
    return run_until_complete(adelete_messages(session_id, context_id))


async def adelete_messages(session_id: str | None = None, context_id: str | None = None) -> None:
    """Delete messages from the monitor service based on the provided session ID.

    Args:
        session_id (str): The session ID associated with the messages to delete.
        context_id (str): The context ID associated with the messages to delete.
    """
    async with session_scope() as session:
        if not session_id and not context_id:
            msg = "Either session_id or context_id must be provided to delete messages."
            raise ValueError(msg)

        # Determine which field to filter by
        filter_column = MessageTable.context_id if context_id else MessageTable.session_id
        filter_value = context_id if context_id else session_id

        stmt = (
            delete(MessageTable)
            .where(col(filter_column) == filter_value)
            .execution_options(synchronize_session="fetch")
        )
        await session.exec(stmt)


async def delete_message(id_: str) -> None:
    """Delete a message from the monitor service based on the provided ID.

    Args:
        id_ (str): The ID of the message to delete.
    """
    async with session_scope() as session:
        message_pk = coerce_uuid(id_)
        if message_pk is None:
            return
        message = await session_get_by_pk(session, MessageTable, message_pk)
        if message:
            await session.delete(message)


def store_message(
    message: Message,
    flow_id: str | UUID | None = None,
) -> list[Message]:
    """DEPRECATED: Stores a message in the memory.

    DEPRECATED: Use `astore_message` instead.

    Args:
        message (Message): The message to store.
        flow_id (Optional[str | UUID]): The flow ID associated with the message.
            When running from the CustomComponent you can access this using `self.graph.flow_id`.

    Returns:
        List[Message]: A list of data containing the stored message.

    Raises:
        ValueError: If any of the required parameters (session_id, sender, sender_name) is not provided.
    """
    return run_until_complete(astore_message(message, flow_id=flow_id))


async def astore_message(
    message: Message,
    flow_id: str | UUID | None = None,
) -> list[Message]:
    """Stores a message in the memory.

    Args:
        message (Message): The message to store.
        flow_id (Optional[str]): The flow ID associated with the message.
            When running from the CustomComponent you can access this using `self.graph.flow_id`.

    Returns:
        List[Message]: A list of data containing the stored message.

    Raises:
        ValueError: If any of the required parameters (session_id, sender, sender_name) is not provided.
    """
    if not message:
        await logger.awarning("No message provided.")
        return []

    if not message.session_id or not message.sender or not message.sender_name:
        msg = (
            f"All of session_id, sender, and sender_name must be provided. Session ID: {message.session_id},"
            f" Sender: {message.sender}, Sender Name: {message.sender_name}"
        )
        raise ValueError(msg)
    if hasattr(message, "id") and message.id:
        # if message has an id and exist in the database, update it
        # if not raise an error and add the message to the database
        try:
            return await aupdate_messages([message])
        except ValueError as e:
            await logger.aerror(e)
    if flow_id and not isinstance(flow_id, UUID):
        flow_id = parse_flow_id(flow_id)
    return await aadd_messages([message], flow_id=flow_id)


class LCBuiltinChatMemory(BaseChatMessageHistory):
    """DEPRECATED: Kept for backward compatibility."""

    def __init__(
        self,
        flow_id: str,
        session_id: str,
        context_id: str | None = None,
    ) -> None:
        self.flow_id = flow_id
        self.session_id = session_id
        self.context_id = context_id

    @property
    def messages(self) -> list[BaseMessage]:
        messages = get_messages(
            session_id=self.session_id,
            context_id=self.context_id,
        )
        return [m.to_lc_message() for m in messages if not m.error]  # Exclude error messages

    async def aget_messages(self) -> list[BaseMessage]:
        messages = await aget_messages(
            session_id=self.session_id,
            context_id=self.context_id,
        )
        return [m.to_lc_message() for m in messages if not m.error]  # Exclude error messages

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        for lc_message in messages:
            message = Message.from_lc_message(lc_message)
            message.session_id = self.session_id
            message.context_id = self.context_id
            store_message(message, flow_id=self.flow_id)

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        for lc_message in messages:
            message = Message.from_lc_message(lc_message)
            message.session_id = self.session_id
            message.context_id = self.context_id
            await astore_message(message, flow_id=self.flow_id)

    def clear(self) -> None:
        delete_messages(self.session_id, self.context_id)

    async def aclear(self) -> None:
        await adelete_messages(self.session_id, self.context_id)
