"""Database access layer for Oracle schema explorer."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import oracledb


IDENTIFIER_RE = re.compile(r"^[A-Z][A-Z0-9_$#]*$")
OBJECT_TYPE_RE = re.compile(r"^[A-Z ]+$")


@dataclass(frozen=True)
class ConnectionConfig:
    """Connection details for an Oracle schema."""

    user: str
    password: str
    dsn: str
    schema: str


def create_connection(config: ConnectionConfig) -> oracledb.Connection:
    """Create a direct Oracle connection using python-oracledb thin mode."""

    return oracledb.connect(
        user=config.user,
        password=config.password,
        dsn=config.dsn,
        config_dir=None,
        wallet_location=None,
    )


def normalize_identifier(name: str) -> str:
    """Return the uppercase version of a SQL identifier and validate it."""

    identifier = name.strip().upper()
    if not IDENTIFIER_RE.match(identifier):
        raise ValueError(
            f"Identifier '{name}' must contain only alphanumerics, _, $, # and start with a letter."
        )
    return identifier


def normalize_object_type(name: str) -> str:
    """Normalise Oracle dictionary object type names."""

    object_type = name.strip().upper()
    if not OBJECT_TYPE_RE.match(object_type):
        raise ValueError(f"Unsupported object type '{name}'.")
    return object_type


def qualified_identifier(schema: str, name: str) -> str:
    """Return a safely qualified identifier for use in SQL text."""

    owner = normalize_identifier(schema)
    identifier = normalize_identifier(name)
    return f'"{owner}"."{identifier}"'


def list_tables(conn: oracledb.Connection, schema: str) -> List[str]:
    """List tables owned by the given schema."""

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name
            FROM all_tables
            WHERE owner = :owner
            ORDER BY table_name
            """,
            owner=normalize_identifier(schema),
        )
        return [row[0] for row in cursor.fetchall()]


def list_schemas(conn: oracledb.Connection) -> List[str]:
    """Return list of accessible schema owners."""

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT DISTINCT owner
            FROM all_objects
            ORDER BY owner
            """
        )
        return [row[0] for row in cursor.fetchall()]


def describe_table(
    conn: oracledb.Connection, schema: str, table_name: str
) -> List[Tuple]:
    """Describe columns of the given table."""

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                column_id,
                column_name,
                data_type,
                data_length,
                data_precision,
                data_scale,
                nullable,
                data_default
            FROM all_tab_columns
            WHERE owner = :owner AND table_name = :table_name
            ORDER BY column_id
            """,
            owner=normalize_identifier(schema),
            table_name=normalize_identifier(table_name),
        )
        return cursor.fetchall()


def fetch_rows(
    conn: oracledb.Connection, schema: str, table_name: str, limit: int | str
) -> Tuple[Sequence[str], List[Sequence]]:
    """Fetch rows from the specified table."""

    try:
        limit_value = int(limit)
    except (TypeError, ValueError) as exc:
        raise ValueError("Row limit must be a positive integer.") from exc

    if limit_value <= 0:
        raise ValueError("Row limit must be a positive integer.")

    table = qualified_identifier(schema, table_name)
    sql = f"SELECT * FROM {table} WHERE ROWNUM <= :row_limit"

    with conn.cursor() as cursor:
        cursor.execute(sql, row_limit=limit_value)
        column_names = [col[0] for col in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

    return column_names, rows


def list_objects(
    conn: oracledb.Connection, schema: str, object_types: Iterable[str]
) -> List[str]:
    """List PL/SQL objects of the specified types."""

    return [name for name, _ in list_objects_info(conn, schema, object_types)]


def list_objects_info(
    conn: oracledb.Connection, schema: str, object_types: Iterable[str]
) -> List[Tuple[str, str]]:
    """List PL/SQL objects with their types."""

    normalized_owner = normalize_identifier(schema)
    normalized_types = tuple(normalize_object_type(typ) for typ in object_types)

    placeholders = ", ".join(f":type_{idx}" for idx in range(len(normalized_types)))
    binds = {f"type_{idx}": obj_type for idx, obj_type in enumerate(normalized_types)}

    sql = f"""
        SELECT object_name, object_type
        FROM all_objects
        WHERE owner = :owner
          AND object_type IN ({placeholders})
        ORDER BY object_name
    """

    with conn.cursor() as cursor:
        cursor.execute(sql, owner=normalized_owner, **binds)
        return [(row[0], row[1]) for row in cursor.fetchall()]


def fetch_source(
    conn: oracledb.Connection, schema: str, object_name: str, object_type: str
) -> str:
    """Return the PL/SQL source code for the given object."""

    normalized_type = normalize_object_type(object_type)

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT text
            FROM all_source
            WHERE owner = :owner
              AND name = :name
              AND type = :type
            ORDER BY line
            """,
            owner=normalize_identifier(schema),
            name=normalize_identifier(object_name),
            type=normalized_type,
        )
        lines = [row[0] for row in cursor.fetchall()]

    if not lines:
        raise LookupError(
            f"Source for {normalized_type} {object_name} under schema {schema} not found."
        )

    return "".join(lines)
