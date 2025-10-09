#!/usr/bin/env python3
"""
Oracle-CLI MCP Server
MCP (Model Context Protocol) sunucusu - AI araçlarının Oracle veritabanına erişimini sağlar.
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any, Optional, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from . import db
from .config import load_config
from .db import ConnectionConfig


# Global connection - server başlatıldığında oluşturulur
_connection: Optional[Any] = None
_config: Optional[ConnectionConfig] = None


async def initialize_connection() -> None:
    """Veritabanı bağlantısını başlat."""
    global _connection, _config
    
    # Config dosyasından bilgileri yükle
    _config = load_config()
    if not _config:
        raise RuntimeError(
            "Oracle bağlantı bilgileri bulunamadı. "
            "Lütfen önce 'oracle-cli configure' komutunu çalıştırın."
        )
    
    # Bağlantıyı oluştur
    loop = asyncio.get_running_loop()
    _connection = await loop.run_in_executor(
        None, db.create_connection, _config
    )


async def close_connection() -> None:
    """Veritabanı bağlantısını kapat."""
    global _connection
    if _connection:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, _connection.close)
        _connection = None


def get_connection() -> Any:
    """Mevcut bağlantıyı döndür."""
    if not _connection:
        raise RuntimeError("Veritabanı bağlantısı kurulmamış.")
    return _connection


def get_config() -> ConnectionConfig:
    """Mevcut konfigürasyonu döndür."""
    if not _config:
        raise RuntimeError("Konfigürasyon yüklenmemiş.")
    return _config


# MCP Server oluştur
app = Server("oracle-cli")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """MCP araçlarını listele."""
    return [
        Tool(
            name="list_tables",
            description="Oracle şemasındaki tüm tabloları listeler",
            inputSchema={
                "type": "object",
                "properties": {
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel, varsayılan configured schema)",
                    }
                },
            },
        ),
        Tool(
            name="describe_table",
            description="Tablonun yapısını (kolonlar, tipler, constraints) gösterir",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="query_table",
            description="Tablodan örnek veri getirir (ilk N satır)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maksimum satır sayısı (varsayılan: 10)",
                        "default": 10,
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="execute_sql",
            description="Özel SQL sorgusu çalıştırır (SELECT sorguları)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL sorgusu (sadece SELECT)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maksimum satır sayısı (varsayılan: 100)",
                        "default": 100,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="list_objects",
            description="Şemadaki PL/SQL objelerini listeler (packages, procedures, functions)",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_type": {
                        "type": "string",
                        "description": "Obje tipi: PACKAGE, PROCEDURE, FUNCTION, PACKAGE BODY",
                        "enum": ["PACKAGE", "PROCEDURE", "FUNCTION", "PACKAGE BODY"],
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["object_type"],
            },
        ),
        Tool(
            name="get_source",
            description="PL/SQL objesinin kaynak kodunu getirir",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Obje adı",
                    },
                    "object_type": {
                        "type": "string",
                        "description": "Obje tipi",
                        "enum": ["PACKAGE", "PROCEDURE", "FUNCTION", "PACKAGE BODY"],
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["object_name", "object_type"],
            },
        ),
        Tool(
            name="get_table_stats",
            description="Tablo istatistiklerini getirir (satır sayısı, boyut vb.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="get_table_relationships",
            description="Tablonun foreign key ilişkilerini gösterir (parent ve child tablolar)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="get_table_indexes",
            description="Tablonun tüm index'lerini listeler (performans optimizasyonu için)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="get_table_constraints",
            description="Tablonun tüm constraint'lerini gösterir (PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="get_related_tables",
            description="Bir tablo ile ilişkili tüm tabloları bulur (foreign key ilişkileri üzerinden)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                    "depth": {
                        "type": "integer",
                        "description": "İlişki derinliği (1=direkt ilişkili, 2=ikinci seviye). Varsayılan: 1",
                        "default": 1,
                    },
                },
                "required": ["table_name"],
            },
        ),
        Tool(
            name="search_tables",
            description="Tablo isimlerinde veya kolon isimlerinde arama yapar",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Aranacak kelime (büyük/küçük harf duyarsız)",
                    },
                    "search_in": {
                        "type": "string",
                        "description": "Arama yeri: table_name (sadece tablo adı), column_name (sadece kolon adı), both (her ikisi)",
                        "enum": ["table_name", "column_name", "both"],
                        "default": "both",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["keyword"],
            },
        ),
        Tool(
            name="get_table_triggers",
            description="Tablonun trigger'larını listeler (INSERT/UPDATE/DELETE olaylarında çalışan otomatik işlemler)",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Tablo adı",
                    },
                    "schema": {
                        "type": "string",
                        "description": "Şema adı (opsiyonel)",
                    },
                },
                "required": ["table_name"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """MCP aracını çalıştır."""
    
    conn = get_connection()
    config = get_config()
    loop = asyncio.get_running_loop()
    
    # Schema parametresini al veya varsayılanı kullan
    schema = arguments.get("schema", config.schema)
    schema = db.normalize_identifier(schema)
    
    try:
        if name == "list_tables":
            tables = await loop.run_in_executor(
                None, db.list_tables, conn, schema
            )
            result = {
                "schema": schema,
                "tables": tables,
                "count": len(tables),
            }
            return [
                TextContent(
                    type="text",
                    text=f"**Schema: {schema}**\n\nToplamda {len(tables)} tablo bulundu:\n\n" + 
                         "\n".join(f"- {table}" for table in tables)
                )
            ]
        
        elif name == "describe_table":
            table_name = arguments["table_name"]
            columns = await loop.run_in_executor(
                None, db.describe_table, conn, schema, table_name
            )
            
            if not columns:
                return [TextContent(type="text", text=f"Tablo bulunamadı: {table_name}")]
            
            # Markdown table formatında
            lines = [
                f"# Tablo: {schema}.{table_name.upper()}",
                "",
                "| Kolon | Tip | Uzunluk | Precision | Scale | Nullable | Varsayılan |",
                "|-------|-----|---------|-----------|-------|----------|------------|",
            ]
            
            for (
                _,
                col_name,
                data_type,
                data_length,
                data_precision,
                data_scale,
                nullable,
                data_default,
            ) in columns:
                lines.append(
                    f"| {col_name} | {data_type} | {data_length or ''} | "
                    f"{data_precision or ''} | {data_scale or ''} | {nullable} | "
                    f"{(data_default or '').strip()} |"
                )
            
            return [TextContent(type="text", text="\n".join(lines))]
        
        elif name == "query_table":
            table_name = arguments["table_name"]
            limit = arguments.get("limit", 10)
            
            column_names, rows = await loop.run_in_executor(
                None, db.fetch_rows, conn, schema, table_name, limit
            )
            
            if not rows:
                return [TextContent(type="text", text=f"Tabloda veri yok: {table_name}")]
            
            # Markdown table formatında
            lines = [
                f"# Tablo Verisi: {schema}.{table_name.upper()} (ilk {len(rows)} satır)",
                "",
                "| " + " | ".join(column_names) + " |",
                "| " + " | ".join(["---"] * len(column_names)) + " |",
            ]
            
            for row in rows:
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("NULL")
                    else:
                        # Uzun değerleri kısalt
                        str_val = str(value).replace("|", "\\|").replace("\n", " ")
                        formatted_row.append(str_val[:100])
                lines.append("| " + " | ".join(formatted_row) + " |")
            
            return [TextContent(type="text", text="\n".join(lines))]
        
        elif name == "execute_sql":
            query = arguments["query"]
            limit = arguments.get("limit", 100)
            
            # Güvenlik: Sadece SELECT sorgularına izin ver
            query_upper = query.strip().upper()
            if not query_upper.startswith("SELECT"):
                return [
                    TextContent(
                        type="text",
                        text="❌ Güvenlik: Sadece SELECT sorguları desteklenmektedir."
                    )
                ]
            
            # ROWNUM limiti ekle
            if "ROWNUM" not in query_upper:
                query = f"SELECT * FROM ({query}) WHERE ROWNUM <= {limit}"
            
            def run_query():
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    return columns, rows
            
            columns, rows = await loop.run_in_executor(None, run_query)
            
            if not rows:
                return [TextContent(type="text", text="Sorgu sonuç döndürmedi.")]
            
            # Markdown table formatında
            lines = [
                f"# SQL Sorgu Sonucu ({len(rows)} satır)",
                "",
                f"```sql\n{query}\n```",
                "",
                "| " + " | ".join(columns) + " |",
                "| " + " | ".join(["---"] * len(columns)) + " |",
            ]
            
            for row in rows:
                formatted_row = []
                for value in row:
                    if value is None:
                        formatted_row.append("NULL")
                    else:
                        str_val = str(value).replace("|", "\\|").replace("\n", " ")
                        formatted_row.append(str_val[:100])
                lines.append("| " + " | ".join(formatted_row) + " |")
            
            return [TextContent(type="text", text="\n".join(lines))]
        
        elif name == "list_objects":
            object_type = arguments["object_type"]
            objects = await loop.run_in_executor(
                None, db.list_objects, conn, schema, [object_type]
            )
            
            result_text = f"**{object_type} objeleri (Schema: {schema})**\n\n"
            result_text += f"Toplam {len(objects)} adet bulundu:\n\n"
            result_text += "\n".join(f"- {obj}" for obj in objects)
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_source":
            object_name = arguments["object_name"]
            object_type = arguments["object_type"]
            
            source = await loop.run_in_executor(
                None, db.fetch_source, conn, schema, object_name, object_type
            )
            
            result_text = f"# {object_type}: {schema}.{object_name}\n\n```sql\n{source}\n```"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_table_stats":
            table_name = arguments["table_name"]
            
            # Tablo istatistiklerini al
            def get_stats():
                with conn.cursor() as cursor:
                    # Satır sayısı
                    cursor.execute(
                        f"SELECT COUNT(*) FROM {db.qualified_identifier(schema, table_name)}"
                    )
                    row_count = cursor.fetchone()[0]
                    
                    # Normalize edilmiş şema ve tablo adı
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    # Tablo boyutu (segment bilgisi) - önce user_segments dene, yoksa all_segments
                    try:
                        cursor.execute(
                            """
                            SELECT 
                                ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
                                COUNT(*) as num_segments
                            FROM user_segments
                            WHERE segment_name = :table_name
                            """,
                            table_name=normalized_table
                        )
                        size_info = cursor.fetchone()
                    except:
                        # user_segments başarısız olursa all_segments dene
                        try:
                            cursor.execute(
                                """
                                SELECT 
                                    ROUND(SUM(bytes)/1024/1024, 2) as size_mb,
                                    COUNT(*) as num_segments
                                FROM all_segments
                                WHERE owner = :owner AND segment_name = :table_name
                                """,
                                owner=normalized_schema,
                                table_name=normalized_table
                            )
                            size_info = cursor.fetchone()
                        except:
                            # Segment bilgisi alınamazsa 0 döndür
                            size_info = (0, 0)
                    
                    size_mb = size_info[0] if size_info and size_info[0] else 0
                    num_segments = size_info[1] if size_info and size_info[1] else 0
                    
                    return row_count, size_mb, num_segments
            
            row_count, size_mb, num_segments = await loop.run_in_executor(None, get_stats)
            
            result_text = f"""# Tablo İstatistikleri: {schema}.{table_name.upper()}

**Satır Sayısı:** {row_count:,}
**Boyut:** {size_mb} MB
**Segment Sayısı:** {num_segments}
"""
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_table_relationships":
            table_name = arguments["table_name"]
            
            def get_relationships():
                with conn.cursor() as cursor:
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    # Parent tablolar (bu tablo hangi tabloları referans ediyor)
                    cursor.execute(
                        """
                        SELECT 
                            c.constraint_name,
                            c.table_name AS child_table,
                            cc.column_name AS child_column,
                            r.table_name AS parent_table,
                            rc.column_name AS parent_column,
                            c.delete_rule
                        FROM all_constraints c
                        JOIN all_cons_columns cc ON c.constraint_name = cc.constraint_name AND c.owner = cc.owner
                        JOIN all_constraints r ON c.r_constraint_name = r.constraint_name AND c.owner = r.owner
                        JOIN all_cons_columns rc ON r.constraint_name = rc.constraint_name AND r.owner = rc.owner
                        WHERE c.constraint_type = 'R' 
                          AND c.owner = :owner 
                          AND c.table_name = :table_name
                        ORDER BY c.constraint_name, cc.position
                        """,
                        owner=normalized_schema,
                        table_name=normalized_table
                    )
                    parents = cursor.fetchall()
                    
                    # Child tablolar (hangi tablolar bu tabloyu referans ediyor)
                    cursor.execute(
                        """
                        SELECT 
                            c.constraint_name,
                            c.table_name AS child_table,
                            cc.column_name AS child_column,
                            r.table_name AS parent_table,
                            rc.column_name AS parent_column,
                            c.delete_rule
                        FROM all_constraints c
                        JOIN all_cons_columns cc ON c.constraint_name = cc.constraint_name AND c.owner = cc.owner
                        JOIN all_constraints r ON c.r_constraint_name = r.constraint_name AND c.owner = r.owner
                        JOIN all_cons_columns rc ON r.constraint_name = rc.constraint_name AND r.owner = rc.owner
                        WHERE c.constraint_type = 'R' 
                          AND r.owner = :owner 
                          AND r.table_name = :table_name
                        ORDER BY c.constraint_name, cc.position
                        """,
                        owner=normalized_schema,
                        table_name=normalized_table
                    )
                    children = cursor.fetchall()
                    
                    return parents, children
            
            parents, children = await loop.run_in_executor(None, get_relationships)
            
            result_text = f"# Tablo İlişkileri: {schema}.{table_name.upper()}\n\n"
            
            # Parent tablolar
            if parents:
                result_text += "## 🔗 Parent Tablolar (Bu Tablo Referans Ediyor)\n\n"
                result_text += "| Constraint | Child Column | Parent Table | Parent Column | Delete Rule |\n"
                result_text += "|------------|--------------|--------------|---------------|-------------|\n"
                for p in parents:
                    result_text += f"| {p[0]} | {p[2]} | {p[3]} | {p[4]} | {p[5] or 'NO ACTION'} |\n"
                result_text += "\n"
            else:
                result_text += "## 🔗 Parent Tablolar\n\nBu tabloyu referans eden başka tablo yok.\n\n"
            
            # Child tablolar
            if children:
                result_text += "## 👶 Child Tablolar (Bu Tabloyu Referans Eden)\n\n"
                result_text += "| Constraint | Child Table | Child Column | Parent Column | Delete Rule |\n"
                result_text += "|------------|-------------|--------------|---------------|-------------|\n"
                for c in children:
                    result_text += f"| {c[0]} | {c[1]} | {c[2]} | {c[4]} | {c[5] or 'NO ACTION'} |\n"
                result_text += "\n"
            else:
                result_text += "## 👶 Child Tablolar\n\nBu tabloyu referans eden başka tablo yok.\n\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_table_indexes":
            table_name = arguments["table_name"]
            
            def get_indexes():
                with conn.cursor() as cursor:
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    cursor.execute(
                        """
                        SELECT 
                            i.index_name,
                            i.index_type,
                            i.uniqueness,
                            i.status,
                            LISTAGG(ic.column_name, ', ') WITHIN GROUP (ORDER BY ic.column_position) AS columns
                        FROM all_indexes i
                        JOIN all_ind_columns ic ON i.index_name = ic.index_name AND i.owner = ic.index_owner
                        WHERE i.table_owner = :owner
                          AND i.table_name = :table_name
                        GROUP BY i.index_name, i.index_type, i.uniqueness, i.status
                        ORDER BY i.index_name
                        """,
                        owner=normalized_schema,
                        table_name=normalized_table
                    )
                    return cursor.fetchall()
            
            indexes = await loop.run_in_executor(None, get_indexes)
            
            result_text = f"# Index'ler: {schema}.{table_name.upper()}\n\n"
            
            if indexes:
                result_text += f"**Toplam {len(indexes)} index bulundu:**\n\n"
                result_text += "| Index Adı | Tip | Unique | Status | Kolonlar |\n"
                result_text += "|-----------|-----|--------|--------|----------|\n"
                for idx in indexes:
                    result_text += f"| {idx[0]} | {idx[1]} | {idx[2]} | {idx[3]} | {idx[4]} |\n"
            else:
                result_text += "Bu tabloda index bulunamadı.\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_table_constraints":
            table_name = arguments["table_name"]
            
            def get_constraints():
                with conn.cursor() as cursor:
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    cursor.execute(
                        """
                        SELECT 
                            c.constraint_name,
                            c.constraint_type,
                            LISTAGG(cc.column_name, ', ') WITHIN GROUP (ORDER BY cc.position) AS columns,
                            c.search_condition,
                            c.r_constraint_name AS references,
                            c.delete_rule,
                            c.status
                        FROM all_constraints c
                        LEFT JOIN all_cons_columns cc ON c.constraint_name = cc.constraint_name 
                                                       AND c.owner = cc.owner
                        WHERE c.owner = :owner
                          AND c.table_name = :table_name
                        GROUP BY c.constraint_name, c.constraint_type, c.search_condition, 
                                 c.r_constraint_name, c.delete_rule, c.status
                        ORDER BY 
                            CASE c.constraint_type 
                                WHEN 'P' THEN 1 
                                WHEN 'U' THEN 2 
                                WHEN 'R' THEN 3 
                                ELSE 4 
                            END
                        """,
                        owner=normalized_schema,
                        table_name=normalized_table
                    )
                    return cursor.fetchall()
            
            constraints = await loop.run_in_executor(None, get_constraints)
            
            result_text = f"# Constraint'ler: {schema}.{table_name.upper()}\n\n"
            
            if constraints:
                constraint_types = {
                    'P': 'PRIMARY KEY',
                    'U': 'UNIQUE',
                    'R': 'FOREIGN KEY',
                    'C': 'CHECK'
                }
                
                result_text += f"**Toplam {len(constraints)} constraint bulundu:**\n\n"
                result_text += "| Constraint | Tip | Kolonlar | Detay | Status |\n"
                result_text += "|------------|-----|----------|-------|--------|\n"
                
                for c in constraints:
                    c_type = constraint_types.get(c[1], c[1])
                    detail = ""
                    if c[1] == 'C' and c[3]:
                        # CHECK constraint - search condition göster
                        detail = str(c[3])[:50] + "..." if len(str(c[3])) > 50 else str(c[3])
                    elif c[1] == 'R' and c[4]:
                        # FOREIGN KEY - referenced constraint göster
                        detail = f"→ {c[4]}"
                        if c[5]:
                            detail += f" (ON DELETE {c[5]})"
                    
                    result_text += f"| {c[0]} | {c_type} | {c[2]} | {detail} | {c[6]} |\n"
            else:
                result_text += "Bu tabloda constraint bulunamadı.\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_related_tables":
            table_name = arguments["table_name"]
            depth = arguments.get("depth", 1)
            
            def get_related():
                with conn.cursor() as cursor:
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    # İlişkili tabloları bul (hem parent hem child)
                    cursor.execute(
                        """
                        SELECT DISTINCT r.table_name AS related_table, 'PARENT' AS relationship_type
                        FROM all_constraints c
                        JOIN all_constraints r ON c.r_constraint_name = r.constraint_name AND c.owner = r.owner
                        WHERE c.constraint_type = 'R' 
                          AND c.owner = :owner 
                          AND c.table_name = :table_name
                        UNION
                        SELECT DISTINCT c.table_name AS related_table, 'CHILD' AS relationship_type
                        FROM all_constraints c
                        JOIN all_constraints r ON c.r_constraint_name = r.constraint_name AND c.owner = r.owner
                        WHERE c.constraint_type = 'R' 
                          AND r.owner = :owner 
                          AND r.table_name = :table_name
                        ORDER BY relationship_type, related_table
                        """,
                        owner=normalized_schema,
                        table_name=normalized_table
                    )
                    return cursor.fetchall()
            
            related = await loop.run_in_executor(None, get_related)
            
            result_text = f"# İlişkili Tablolar: {schema}.{table_name.upper()}\n\n"
            
            if related:
                parents = [r for r in related if r[1] == 'PARENT']
                children = [r for r in related if r[1] == 'CHILD']
                
                result_text += f"**Toplam {len(related)} ilişkili tablo bulundu:**\n\n"
                
                if parents:
                    result_text += "## 🔗 Parent Tablolar\n\n"
                    for p in parents:
                        result_text += f"- {p[0]}\n"
                    result_text += "\n"
                
                if children:
                    result_text += "## 👶 Child Tablolar\n\n"
                    for c in children:
                        result_text += f"- {c[0]}\n"
                    result_text += "\n"
            else:
                result_text += "Bu tablo ile ilişkili başka tablo bulunamadı.\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "search_tables":
            keyword = arguments["keyword"]
            search_in = arguments.get("search_in", "both")
            
            def search():
                with conn.cursor() as cursor:
                    normalized_schema = db.normalize_identifier(schema)
                    search_pattern = f"%{keyword.upper()}%"
                    
                    results = []
                    
                    # Tablo isimlerinde ara
                    if search_in in ["table_name", "both"]:
                        cursor.execute(
                            """
                            SELECT table_name, 'TABLE_NAME' AS match_type, NULL AS column_name
                            FROM all_tables
                            WHERE owner = :owner
                              AND table_name LIKE :pattern
                            ORDER BY table_name
                            """,
                            owner=normalized_schema,
                            pattern=search_pattern
                        )
                        results.extend(cursor.fetchall())
                    
                    # Kolon isimlerinde ara
                    if search_in in ["column_name", "both"]:
                        cursor.execute(
                            """
                            SELECT table_name, 'COLUMN_NAME' AS match_type, column_name
                            FROM all_tab_columns
                            WHERE owner = :owner
                              AND column_name LIKE :pattern
                            ORDER BY table_name, column_name
                            """,
                            owner=normalized_schema,
                            pattern=search_pattern
                        )
                        results.extend(cursor.fetchall())
                    
                    return results
            
            results = await loop.run_in_executor(None, search)
            
            result_text = f"# Arama Sonuçları: '{keyword}'\n\n"
            
            if results:
                result_text += f"**{len(results)} sonuç bulundu:**\n\n"
                
                # Tablo adı sonuçları
                table_matches = [r for r in results if r[1] == 'TABLE_NAME']
                if table_matches:
                    result_text += "## 📊 Tablo İsimleri\n\n"
                    for r in table_matches:
                        result_text += f"- **{r[0]}**\n"
                    result_text += "\n"
                
                # Kolon adı sonuçları
                column_matches = [r for r in results if r[1] == 'COLUMN_NAME']
                if column_matches:
                    result_text += "## 📋 Kolon İsimleri\n\n"
                    current_table = None
                    for r in column_matches:
                        if r[0] != current_table:
                            if current_table:
                                result_text += "\n"
                            result_text += f"**{r[0]}:**\n"
                            current_table = r[0]
                        result_text += f"  - {r[2]}\n"
            else:
                result_text += f"'{keyword}' için sonuç bulunamadı.\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_table_triggers":
            table_name = arguments["table_name"]
            
            def get_triggers():
                with conn.cursor() as cursor:
                    normalized_schema = db.normalize_identifier(schema)
                    normalized_table = db.normalize_identifier(table_name)
                    
                    cursor.execute(
                        """
                        SELECT 
                            trigger_name,
                            trigger_type,
                            triggering_event,
                            status,
                            description
                        FROM all_triggers
                        WHERE owner = :owner
                          AND table_name = :table_name
                        ORDER BY trigger_name
                        """,
                        owner=normalized_schema,
                        table_name=normalized_table
                    )
                    return cursor.fetchall()
            
            triggers = await loop.run_in_executor(None, get_triggers)
            
            result_text = f"# Trigger'lar: {schema}.{table_name.upper()}\n\n"
            
            if triggers:
                result_text += f"**Toplam {len(triggers)} trigger bulundu:**\n\n"
                result_text += "| Trigger Adı | Tip | Event | Status | Açıklama |\n"
                result_text += "|-------------|-----|-------|--------|----------|\n"
                for t in triggers:
                    desc = str(t[4])[:50] + "..." if t[4] and len(str(t[4])) > 50 else (t[4] or "")
                    result_text += f"| {t[0]} | {t[1]} | {t[2]} | {t[3]} | {desc} |\n"
            else:
                result_text += "Bu tabloda trigger bulunamadı.\n"
            
            return [TextContent(type="text", text=result_text)]
        
        else:
            return [TextContent(type="text", text=f"Bilinmeyen araç: {name}")]
    
    except Exception as exc:
        import traceback
        error_detail = traceback.format_exc()
        return [
            TextContent(
                type="text",
                text=f"❌ Hata: {str(exc)}\n\nDetay:\n```\n{error_detail}\n```"
            )
        ]


async def main():
    """MCP sunucusunu başlat."""
    
    # Bağlantıyı başlat
    await initialize_connection()
    
    try:
        # stdio üzerinden MCP sunucusunu çalıştır
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        # Temizlik
        await close_connection()


def run_mcp_server():
    """MCP sunucusunu çalıştır (CLI entry point)."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nMCP sunucusu durduruldu.", file=sys.stderr)
    except Exception as exc:
        print(f"MCP sunucu hatası: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_mcp_server()
