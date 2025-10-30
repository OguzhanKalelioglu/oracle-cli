from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Dict, Optional

import click
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from . import db
from .config import CONFIG_PATH, load_config, save_config
from .db import ConnectionConfig
from .tui import OracleExplorerApp

__version__ = "1.2.3"  # Package body scroll support with arrow key navigation


OBJECT_TYPE_ALIASES: Dict[str, str] = {
    "package": "PACKAGE",
    "package-body": "PACKAGE BODY",
    "procedure": "PROCEDURE",
    "function": "FUNCTION",
}


def resolve_connection_config(
    user: Optional[str],
    password: Optional[str],
    dsn: Optional[str],
    schema: Optional[str],
) -> ConnectionConfig:
    stored = load_config()

    resolved_user = user or (stored.user if stored else None)
    resolved_password = password or (stored.password if stored else None)
    resolved_dsn = dsn or (stored.dsn if stored else None)
    resolved_schema = schema or (stored.schema if stored else None)

    # Eğer hiçbir bilgi yoksa (ne stored ne de parametre), interaktif configure yap
    needs_interactive_config = not resolved_user or not resolved_password or not resolved_dsn
    
    if not resolved_user:
        resolved_user = click.prompt("Oracle username")

    if not resolved_password:
        resolved_password = click.prompt("Oracle password", hide_input=True)

    if not resolved_dsn:
        resolved_dsn = click.prompt("Oracle DSN (e.g., localhost:1521/XEPDB1)")

    if not resolved_schema:
        default_schema = resolved_user
        resolved_schema = click.prompt(
            "Default schema", default=default_schema, show_default=True
        )

    try:
        normalized_schema = db.normalize_identifier(resolved_schema or resolved_user)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    config = ConnectionConfig(
        user=resolved_user,
        password=resolved_password,
        dsn=resolved_dsn,
        schema=normalized_schema,
    )
    
    # Eğer config dosyası yoktu ve interaktif olarak bilgi girildiyse, kaydet
    if needs_interactive_config and not stored:
        try:
            save_config(config)
            click.echo(f"\n✅ Connection details saved to: {CONFIG_PATH}")
            click.echo("   (You won't be asked again on next run)\n")
        except Exception as e:
            click.echo(f"\n⚠️  Warning: Could not save config: {e}", err=True)
            click.echo("   (Connection will work, but you'll be asked again next time)\n", err=True)
    
    return config


def get_console(ctx: click.Context) -> Console:
    return ctx.obj["console"]


@click.group(invoke_without_command=True)
@click.version_option(version=__version__, prog_name="oracle-cli")
@click.option(
    "--user",
    envvar="ORACLE_USER",
    default=None,
    help="Oracle database username.",
)
@click.option(
    "--password",
    envvar="ORACLE_PASSWORD",
    default=None,
    hide_input=True,
    help="Oracle database password.",
)
@click.option(
    "--dsn",
    envvar="ORACLE_DSN",
    default=None,
    help="Oracle connection string (e.g., localhost:1521/XEPDB1).",
)
@click.option(
    "--schema",
    envvar="ORACLE_SCHEMA",
    default=None,
    help="Default schema name. If empty, username will be used.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    user: Optional[str],
    password: Optional[str],
    dsn: Optional[str],
    schema: Optional[str],
):
    """Interactive Oracle database schema explorer."""

    ctx.ensure_object(dict)
    console = ctx.obj.setdefault("console", Console())
    ctx.obj["raw_options"] = {
        "user": user,
        "password": password,
        "dsn": dsn,
        "schema": schema,
    }

    subcommand = ctx.invoked_subcommand

    if subcommand == "configure":
        return

    # Eğer hiçbir komut çağrılmadıysa, TUI'yi başlat
    if subcommand is None:
        # Bağlantı bilgilerini yükle
        config = resolve_connection_config(user, password, dsn, schema)
        ctx.obj["config"] = config
        # TUI'yi başlat
        ctx.invoke(launch_tui, row_limit=50, debug=False)
        return

    # Bağlantı bilgilerini yükle (diğer komutlar için)
    config = resolve_connection_config(user, password, dsn, schema)
    ctx.obj["config"] = config

    if subcommand == "tui":
        return

    try:
        conn = db.create_connection(config)
    except Exception as exc:
        raise click.ClickException(f"Connection failed: {exc}") from exc

    ctx.obj["conn"] = conn
    ctx.call_on_close(conn.close)
    console.print(
        f"[bold green]Connected:[/] {config.user}@{config.dsn} (schema: {config.schema.upper()})"
    )


@cli.command("configure")
@click.option(
    "--path",
    "config_path",
    type=click.Path(path_type=str),
    default=str(CONFIG_PATH),
    show_default=True,
    help="Path to save the configuration file.",
)
@click.pass_context
def configure(ctx: click.Context, config_path: str):
    """Save Oracle connection details for later use."""

    console = get_console(ctx)
    path = Path(config_path)
    existing = load_config(path)
    
    def prompt_masked(
        label: str,
        *,
        existing_value: Optional[str] = None,
        fallback_default: Optional[str] = None,
        hide_input: bool = False,
        allow_empty: bool = False,
    ) -> str:
        """Prompt for a value without echoing existing sensitive defaults."""

        prompt_text = label
        if existing_value:
            prompt_text = f"{label} (leave empty to keep current)"
            result = click.prompt(
                prompt_text,
                default="",
                show_default=False,
                hide_input=hide_input,
            )
            if result:
                return result
            return existing_value

        result = click.prompt(
            prompt_text,
            default=fallback_default if fallback_default is not None else None,
            show_default=fallback_default is not None,
            hide_input=hide_input,
        )

        if not result:
            if fallback_default is not None:
                return fallback_default
            if allow_empty:
                return ""
            raise click.ClickException(f"{label} cannot be empty.")

        return result

    user = prompt_masked("Oracle username", existing_value=(existing.user if existing else None))

    password_prompt = click.prompt(
        "Oracle password (leave empty to keep existing)",
        hide_input=True,
        default="",
        show_default=False,
    )
    if password_prompt:
        password = password_prompt
    elif existing:
        password = existing.password
    else:
        raise click.ClickException("Password cannot be empty.")

    dsn = prompt_masked(
        "Oracle DSN (e.g., localhost:1521/XEPDB1 or hostname:1521/ORCL)",
        existing_value=(existing.dsn if existing else None),
    )

    schema = prompt_masked(
        "Default schema",
        existing_value=(existing.schema if existing else None),
        fallback_default=user,
    )

    try:
        normalized_schema = db.normalize_identifier(schema)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    config = ConnectionConfig(user=user, password=password, dsn=dsn, schema=normalized_schema)
    save_config(config, path)
    console.print(f"[green]Connection details saved:[/] {path}")


@cli.command("tui")
@click.option(
    "--limit",
    "row_limit",
    type=click.IntRange(1, None),
    default=50,
    show_default=True,
    help="Number of rows to display in table preview.",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug mode and show logs.",
)
@click.pass_context
def launch_tui(ctx: click.Context, row_limit: int, debug: bool):
    """Launch the interactive Text User Interface."""

    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)
    
    if debug:
        from pathlib import Path
        log_file = Path.home() / ".oracle_cli" / "logs" / "tui_debug.log"
        console.print(f"[yellow]Debug modu aktif - Loglar şuraya yazılacak: {log_file}[/]")
    
    app = OracleExplorerApp(config=config, row_limit=row_limit, debug=debug)
    app.run()


@cli.command("list-tables")
@click.pass_context
def list_tables(ctx: click.Context):
    """List all tables in the schema."""

    conn = ctx.obj["conn"]
    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)

    tables = db.list_tables(conn, config.schema)

    if not tables:
        console.print("[yellow]No tables found.[/]")
        return

    table = Table(title=f"Tables ({config.schema.upper()})", header_style="bold")
    table.add_column("Table Name")
    for name in tables:
        table.add_row(name)

    console.print(table)


@cli.command("describe-table")
@click.argument("table_name")
@click.pass_context
def describe_table(ctx: click.Context, table_name: str):
    """Show detailed column information for a table."""

    conn = ctx.obj["conn"]
    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)

    try:
        rows = db.describe_table(conn, config.schema, table_name)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if not rows:
        raise click.ClickException(
            f"Table {table_name.upper()} not found in schema {config.schema.upper()}."
        )

    table = Table(title=f"Columns: {table_name.upper()}", header_style="bold")
    table.add_column("ID", justify="right")
    table.add_column("Column")
    table.add_column("Type")
    table.add_column("Length", justify="right")
    table.add_column("Precision", justify="right")
    table.add_column("Scale", justify="right")
    table.add_column("Nullable")
    table.add_column("Default Value")

    for (
        column_id,
        column_name,
        data_type,
        data_length,
        data_precision,
        data_scale,
        nullable,
        data_default,
    ) in rows:
        table.add_row(
            str(column_id),
            column_name,
            data_type,
            str(data_length or ""),
            str(data_precision or ""),
            str(data_scale or ""),
            nullable,
            (data_default or "").strip(),
        )

    console.print(table)


@cli.command("preview-table")
@click.argument("table_name")
@click.option(
    "--limit",
    default=20,
    show_default=True,
    type=click.IntRange(1, None),
    help="Number of rows to display.",
)
@click.pass_context
def preview_table(ctx: click.Context, table_name: str, limit: int):
    """Preview table data with sample rows."""

    conn = ctx.obj["conn"]
    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)

    try:
        column_names, rows = db.fetch_rows(conn, config.schema, table_name, limit)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if not rows:
        console.print("[yellow]No rows found.[/]")
        return

    table = Table(
        title=f"{table_name.upper()} - first {limit} rows",
        header_style="bold",
        show_lines=False,
    )
    for name in column_names:
        table.add_column(name)

    for row in rows:
        table.add_row(*(str(value) if value is not None else "NULL" for value in row))

    console.print(table)


@cli.command("list-packages")
@click.option(
    "--with-body",
    is_flag=True,
    help="Include package bodies in the list.",
)
@click.pass_context
def list_packages(ctx: click.Context, with_body: bool):
    """List all packages (and optionally package bodies) in the schema."""

    conn = ctx.obj["conn"]
    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)

    object_types = ["PACKAGE"]
    if with_body:
        object_types.append("PACKAGE BODY")

    packages = db.list_objects(conn, config.schema, object_types)

    if not packages:
        console.print("[yellow]No packages found.[/]")
        return

    table = Table(title="Packages", header_style="bold")
    table.add_column("Name")
    for name in packages:
        table.add_row(name)
    console.print(table)


@cli.command("list-programs")
@click.option(
    "--type",
    "program_type",
    type=click.Choice(["procedure", "function"], case_sensitive=False),
    required=True,
    help="Type of program to list (procedure or function).",
)
@click.pass_context
def list_programs(ctx: click.Context, program_type: str):
    """List procedures or functions in the schema."""

    conn = ctx.obj["conn"]
    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)

    oracle_type = OBJECT_TYPE_ALIASES[program_type.lower()]
    programs = db.list_objects(conn, config.schema, [oracle_type])

    if not programs:
        console.print(f"[yellow]No {oracle_type.lower()}s found.[/]")
        return

    table = Table(title=oracle_type.title(), header_style="bold")
    table.add_column("Name")
    for name in programs:
        table.add_row(name)
    console.print(table)


@cli.command("show-source")
@click.argument("object_name")
@click.option(
    "--type",
    "object_type_key",
    type=click.Choice(sorted(OBJECT_TYPE_ALIASES.keys()), case_sensitive=False),
    prompt="Object type",
    help="Type of the object to display.",
)
@click.option(
    "--body",
    is_flag=True,
    help="Show package body (only for packages).",
)
@click.pass_context
def show_source(ctx: click.Context, object_name: str, object_type_key: str, body: bool):
    """Display PL/SQL source code for a database object."""

    conn = ctx.obj["conn"]
    config: ConnectionConfig = ctx.obj["config"]
    console = get_console(ctx)

    normalized_key = object_type_key.lower()
    oracle_type = OBJECT_TYPE_ALIASES[normalized_key]

    if body:
        if oracle_type != "PACKAGE":
            raise click.ClickException("--body yalnızca package tipi için geçerlidir.")
        oracle_type = "PACKAGE BODY"

    try:
        source = db.fetch_source(conn, config.schema, object_name, oracle_type)
    except (ValueError, LookupError) as exc:
        raise click.ClickException(str(exc)) from exc

    syntax = Syntax(source, "plsql", theme="monokai", line_numbers=True)
    console.print(syntax)


@cli.command("use-schema")
@click.argument("schema_name")
@click.pass_context
def use_schema(ctx: click.Context, schema_name: str):
    """Switch to a different schema."""

    config: ConnectionConfig = ctx.obj["config"]
    conn = ctx.obj["conn"]
    console = get_console(ctx)

    try:
        new_schema = db.normalize_identifier(schema_name)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    ctx.obj["config"] = replace(config, schema=new_schema)
    console.print(f"[green]Schema changed to:[/] {new_schema}")


@cli.command("mcp")
@click.pass_context
def start_mcp_server(ctx: click.Context):
    """Start MCP (Model Context Protocol) server for AI tools integration.
    
    This command starts an MCP server that allows AI tools like Cursor, VS Code,
    and Claude Desktop to access your Oracle database schema and data.
    
    The server communicates via stdio (standard input/output) using JSON-RPC.
    
    Configuration needed in your AI tool (e.g., Cursor MCP settings):
    
    \b
    {
      "mcpServers": {
        "oracle-cli": {
          "command": "oracle-cli",
          "args": ["mcp"]
        }
      }
    }
    """
    
    from .mcp_server import run_mcp_server
    
    # Önce konfigürasyon kontrolü
    config = load_config()
    if not config:
        raise click.ClickException(
            "Oracle bağlantı bilgileri bulunamadı.\n"
            "Lütfen önce 'oracle-cli configure' komutunu çalıştırın."
        )
    
    # MCP sunucusunu başlat
    run_mcp_server()


def main():
    cli(prog_name="oracle-cli")


if __name__ == "__main__":
    main()
