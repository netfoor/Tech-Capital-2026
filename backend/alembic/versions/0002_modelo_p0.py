"""Modelo P0 de §13.2: catálogo, datos personales, agregados y auditoría (spec 014).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-16
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Búsqueda sin acentos en GET /pois?q=
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.create_table(
        "audit_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "ts", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("actor_id", sa.UUID(), nullable=True),
        sa.Column("accion", sa.String(length=80), nullable=False),
        sa.Column("entidad", sa.String(length=80), nullable=False),
        sa.Column("entidad_id", sa.String(length=120), nullable=False),
        sa.Column("detalle", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_event")),
        schema="audit",
    )
    op.create_geospatial_table(
        "corridor",
        sa.Column("corredor_id", sa.String(length=64), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("lat_min", sa.Float(), nullable=False),
        sa.Column("lon_min", sa.Float(), nullable=False),
        sa.Column("lat_max", sa.Float(), nullable=False),
        sa.Column("lon_max", sa.Float(), nullable=False),
        sa.Column(
            "geom",
            Geometry(
                geometry_type="POLYGON",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "lat_min <= lat_max AND lon_min <= lon_max", name=op.f("ck_corridor_bbox_valida")
        ),
        sa.PrimaryKeyConstraint("corredor_id", name=op.f("pk_corridor")),
        schema="core",
    )
    op.create_geospatial_index(
        "idx_corridor_geom",
        "corridor",
        ["geom"],
        unique=False,
        schema="core",
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_table(
        "data_source",
        sa.Column("fuente_id", sa.String(length=80), nullable=False),
        sa.Column("nombre", sa.String(length=300), nullable=False),
        sa.Column("institucion", sa.String(length=300), nullable=True),
        sa.Column("tipo", sa.String(length=60), nullable=True),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("licencia", sa.String(length=200), nullable=True),
        sa.Column("fecha_consulta", sa.Date(), nullable=True),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("fuente_id", name=op.f("pk_data_source")),
        schema="core",
    )
    op.create_geospatial_table(
        "destination",
        sa.Column("destino_id", sa.String(length=64), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=True),
        sa.Column("pueblo_magico", sa.Boolean(), nullable=False),
        sa.Column("municipios_cvegeo", postgresql.ARRAY(sa.String(length=10)), nullable=False),
        sa.Column("cabecera_cvegeo", sa.String(length=12), nullable=True),
        sa.Column("zona", sa.String(length=100), nullable=True),
        sa.Column("centro_ot", sa.String(length=100), nullable=True),
        sa.Column("altitud_m", sa.Float(), nullable=True),
        sa.Column(
            "geom",
            Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.PrimaryKeyConstraint("destino_id", name=op.f("pk_destination")),
        schema="core",
    )
    op.create_geospatial_index(
        "idx_destination_geom",
        "destination",
        ["geom"],
        unique=False,
        schema="core",
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_table(
        "user_account",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("correo", sa.String(length=254), nullable=False),
        sa.Column("hash_contrasena", sa.String(length=200), nullable=False),
        sa.Column("rol", sa.String(length=20), nullable=False),
        sa.Column("nombre_visible", sa.String(length=120), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "rol IN ('visitante', 'viewer', 'analista', 'admin')", name=op.f("ck_user_account_rol")
        ),
        sa.CheckConstraint(
            "correo = lower(correo)", name=op.f("ck_user_account_correo_minusculas")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_account")),
        sa.UniqueConstraint("correo", name=op.f("uq_user_account_correo")),
        schema="private",
    )
    op.create_table(
        "data_lineage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entidad", sa.String(length=80), nullable=False),
        sa.Column("entidad_id", sa.String(length=120), nullable=False),
        sa.Column("fuente_id", sa.String(length=80), nullable=False),
        sa.Column("campo", sa.String(length=80), nullable=True),
        sa.Column("metodo", sa.Text(), nullable=True),
        sa.Column("fecha", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fuente_id"],
            ["core.data_source.fuente_id"],
            name=op.f("fk_data_lineage_fuente_id_data_source"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_data_lineage")),
        schema="core",
    )
    op.create_table(
        "metric_definition",
        sa.Column("metric_id", sa.String(length=80), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("version_formula", sa.String(length=40), nullable=False),
        sa.Column("unidad", sa.String(length=80), nullable=True),
        sa.Column("denominador", sa.Text(), nullable=True),
        sa.Column("procedencia", sa.String(length=20), nullable=True),
        sa.Column("fuente_id", sa.String(length=80), nullable=True),
        sa.Column("k_minimo", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "procedencia IS NULL OR procedencia IN ('medido', 'derivado')",
            name=op.f("ck_metric_definition_procedencia"),
        ),
        sa.ForeignKeyConstraint(
            ["fuente_id"],
            ["core.data_source.fuente_id"],
            name=op.f("fk_metric_definition_fuente_id_data_source"),
        ),
        sa.PrimaryKeyConstraint("metric_id", name=op.f("pk_metric_definition")),
        schema="core",
    )
    op.create_geospatial_table(
        "point_of_interest",
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("nombre", sa.String(length=300), nullable=False),
        sa.Column("categoria", sa.String(length=80), nullable=False),
        sa.Column("subcategoria", sa.String(length=120), nullable=True),
        sa.Column("destino_id", sa.String(length=64), nullable=False),
        sa.Column("corredor_id", sa.String(length=64), nullable=True),
        sa.Column("municipio_cvegeo", sa.String(length=10), nullable=True),
        sa.Column(
            "geom",
            Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("direccion", sa.Text(), nullable=True),
        sa.Column("horario_osm", sa.Text(), nullable=True),
        sa.Column("costo_rango", sa.String(length=10), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column(
            "fuentes", postgresql.ARRAY(sa.String(length=80)), server_default="{}", nullable=False
        ),
        sa.Column("osm_id", sa.String(length=40), nullable=True),
        sa.Column("denue_id", sa.String(length=40), nullable=True),
        sa.Column("sic_id", sa.String(length=40), nullable=True),
        sa.Column("match_score", sa.Float(), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "costo_rango IS NULL OR costo_rango IN ('gratis', 'bajo', 'medio', 'alto')",
            name=op.f("ck_point_of_interest_costo_rango"),
        ),
        sa.CheckConstraint(
            "match_score IS NULL OR (match_score >= 0 AND match_score <= 1)",
            name=op.f("ck_point_of_interest_match_score"),
        ),
        sa.ForeignKeyConstraint(
            ["corredor_id"],
            ["core.corridor.corredor_id"],
            name=op.f("fk_point_of_interest_corredor_id_corridor"),
        ),
        sa.ForeignKeyConstraint(
            ["destino_id"],
            ["core.destination.destino_id"],
            name=op.f("fk_point_of_interest_destino_id_destination"),
        ),
        sa.PrimaryKeyConstraint("poi_id", name=op.f("pk_point_of_interest")),
        schema="core",
    )
    op.create_geospatial_index(
        "idx_point_of_interest_geom",
        "point_of_interest",
        ["geom"],
        unique=False,
        schema="core",
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_index(
        op.f("ix_core_point_of_interest_categoria"),
        "point_of_interest",
        ["categoria"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_point_of_interest_corredor_id"),
        "point_of_interest",
        ["corredor_id"],
        unique=False,
        schema="core",
    )
    op.create_index(
        op.f("ix_core_point_of_interest_destino_id"),
        "point_of_interest",
        ["destino_id"],
        unique=False,
        schema="core",
    )
    op.create_table(
        "consent_grant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("finalidad", sa.String(length=40), nullable=False),
        sa.Column("version", sa.String(length=40), nullable=False),
        sa.Column("otorgado", sa.Boolean(), nullable=False),
        sa.Column(
            "fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("revocado_en", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "finalidad IN ('ubicacion_sesion', 'resenas', 'fotos', 'analitica_agregada')",
            name=op.f("ck_consent_grant_finalidad"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_consent_grant_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consent_grant")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_consent_grant_user_id"),
        "consent_grant",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "itinerary",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("modo", sa.String(length=20), nullable=False),
        sa.Column("solicitud", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("explicacion", sa.Text(), nullable=True),
        sa.Column("motor", sa.String(length=60), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "modo IN ('recomendado', 'desde_guardados')", name=op.f("ck_itinerary_modo")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_itinerary_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_itinerary")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_itinerary_user_id"),
        "itinerary",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "media_asset",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("ruta", sa.Text(), nullable=False),
        sa.Column("tipo_mime", sa.String(length=40), nullable=False),
        sa.Column("bytes", sa.Integer(), nullable=False),
        sa.Column("texto_alternativo", sa.Text(), nullable=True),
        sa.Column("sin_exif", sa.Boolean(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint("sin_exif", name=op.f("ck_media_asset_sin_exif")),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_media_asset_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_media_asset")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_media_asset_user_id"),
        "media_asset",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "place_list",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("nombre", sa.String(length=200), nullable=False),
        sa.Column(
            "etiquetas", postgresql.ARRAY(sa.String(length=60)), server_default="{}", nullable=False
        ),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_place_list_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_place_list")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_place_list_user_id"),
        "place_list",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "privacy_preference",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("perfil_publico", sa.Boolean(), nullable=False),
        sa.Column("precision_publicacion", sa.String(length=10), nullable=False),
        sa.Column("retencion_dias", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "precision_publicacion IN ('lugar', 'zona')",
            name=op.f("ck_privacy_preference_precision"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_privacy_preference_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_privacy_preference")),
        sa.UniqueConstraint("user_id", name=op.f("uq_privacy_preference_user_id")),
        schema="private",
    )
    op.create_table(
        "user_accessibility_preference",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("sin_escalones", sa.Boolean(), nullable=True),
        sa.Column("banio_accesible", sa.Boolean(), nullable=True),
        sa.Column("descansos_cada_min", sa.Integer(), nullable=True),
        sa.Column("pendiente_max_pct", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_user_accessibility_preference_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_accessibility_preference")),
        sa.UniqueConstraint("user_id", name=op.f("uq_user_accessibility_preference_user_id")),
        schema="private",
    )
    op.create_table(
        "aggregate_metric",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("metric_id", sa.String(length=80), nullable=False),
        sa.Column("destino_id", sa.String(length=64), nullable=True),
        sa.Column("corredor_id", sa.String(length=64), nullable=True),
        sa.Column("centro_ot", sa.String(length=100), nullable=True),
        sa.Column("nivel", sa.String(length=20), nullable=True),
        sa.Column("periodo", sa.String(length=10), nullable=False),
        sa.Column("valor", sa.Float(), nullable=True),
        sa.Column("n", sa.Integer(), nullable=True),
        sa.Column("suprimido", sa.Boolean(), nullable=False),
        sa.Column("procedencia", sa.String(length=20), nullable=True),
        sa.Column("version_formula", sa.String(length=40), nullable=False),
        sa.Column("calculado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fuente_id", sa.String(length=80), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "procedencia IS NULL OR procedencia IN ('medido', 'derivado')",
            name=op.f("ck_aggregate_metric_proc"),
        ),
        sa.CheckConstraint(
            "NOT suprimido OR valor IS NULL", name=op.f("ck_aggregate_metric_suprimido_sin_valor")
        ),
        sa.CheckConstraint("n IS NULL OR n >= 0", name=op.f("ck_aggregate_metric_n")),
        sa.ForeignKeyConstraint(
            ["corredor_id"],
            ["core.corridor.corredor_id"],
            name=op.f("fk_aggregate_metric_corredor_id_corridor"),
        ),
        sa.ForeignKeyConstraint(
            ["destino_id"],
            ["core.destination.destino_id"],
            name=op.f("fk_aggregate_metric_destino_id_destination"),
        ),
        sa.ForeignKeyConstraint(
            ["fuente_id"],
            ["core.data_source.fuente_id"],
            name=op.f("fk_aggregate_metric_fuente_id_data_source"),
        ),
        sa.ForeignKeyConstraint(
            ["metric_id"],
            ["core.metric_definition.metric_id"],
            name=op.f("fk_aggregate_metric_metric_id_metric_definition"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_aggregate_metric")),
        sa.UniqueConstraint(
            "metric_id",
            "centro_ot",
            "nivel",
            "periodo",
            name="uq_aggregate_metric_metric_centro_nivel_periodo",
            postgresql_nulls_not_distinct=True,
        ),
        schema="analytics",
    )
    op.create_index(
        op.f("ix_analytics_aggregate_metric_destino_id"),
        "aggregate_metric",
        ["destino_id"],
        unique=False,
        schema="analytics",
    )
    op.create_index(
        op.f("ix_analytics_aggregate_metric_metric_id"),
        "aggregate_metric",
        ["metric_id"],
        unique=False,
        schema="analytics",
    )
    op.create_table(
        "opening_hours",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("dia_semana", sa.Integer(), nullable=True),
        sa.Column("abre", sa.Time(), nullable=True),
        sa.Column("cierra", sa.Time(), nullable=True),
        sa.Column("texto_osm", sa.Text(), nullable=True),
        sa.Column("origen", sa.String(length=40), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "dia_semana IS NULL OR (dia_semana >= 0 AND dia_semana <= 6)",
            name=op.f("ck_opening_hours_dia_semana"),
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_opening_hours_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_opening_hours")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_opening_hours_poi_id"),
        "opening_hours",
        ["poi_id"],
        unique=False,
        schema="core",
    )
    op.create_table(
        "poi_accessibility_attribute",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("atributo", sa.String(length=40), nullable=False),
        sa.Column("valor", sa.String(length=80), nullable=True),
        sa.Column("origen", sa.String(length=40), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("alcance", sa.String(length=80), server_default="poi", nullable=False),
        sa.Column("confianza", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("evidencia", sa.Text(), nullable=True),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "atributo IN ('acceso_sin_escalones', 'rampa', 'banio_accesible', 'elevador', 'superficie', 'asientos', 'estacionamiento_reservado', 'pendiente_pct', 'numero_escalones')",
            name=op.f("ck_poi_accessibility_attribute_atributo"),
        ),
        sa.CheckConstraint(
            "estado IN ('verificado', 'sin_verificar', 'reportado', 'en_moderacion')",
            name=op.f("ck_poi_accessibility_attribute_estado"),
        ),
        sa.CheckConstraint(
            "confianza >= 0 AND confianza <= 1",
            name=op.f("ck_poi_accessibility_attribute_confianza"),
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_poi_accessibility_attribute_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_poi_accessibility_attribute")),
        sa.UniqueConstraint(
            "poi_id", "atributo", name="uq_poi_accessibility_attribute_poi_atributo"
        ),
        schema="core",
    )
    op.create_table(
        "provider",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nombre", sa.String(length=300), nullable=False),
        sa.Column("tipo", sa.String(length=80), nullable=True),
        sa.Column("poi_id", sa.String(length=80), nullable=True),
        sa.Column("denue_id", sa.String(length=40), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_provider_poi_id_point_of_interest"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_provider")),
        schema="core",
    )
    op.create_table(
        "check_in",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column(
            "fecha", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("nota", sa.Text(), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_check_in_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_check_in_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_check_in")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_check_in_poi_id"), "check_in", ["poi_id"], unique=False, schema="private"
    )
    op.create_index(
        op.f("ix_private_check_in_user_id"), "check_in", ["user_id"], unique=False, schema="private"
    )
    op.create_table(
        "community_report",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("media_asset_id", sa.Integer(), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "estado IN ('en_moderacion', 'aceptado', 'rechazado')",
            name=op.f("ck_community_report_estado"),
        ),
        sa.CheckConstraint(
            "tipo IN ('escalones', 'rampa_bloqueada', 'sin_banio_accesible', 'superficie', 'senalizacion', 'otro')",
            name=op.f("ck_community_report_tipo"),
        ),
        sa.ForeignKeyConstraint(
            ["media_asset_id"],
            ["private.media_asset.id"],
            name=op.f("fk_community_report_media_asset_id_media_asset"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_community_report_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_community_report_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_community_report")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_community_report_poi_id"),
        "community_report",
        ["poi_id"],
        unique=False,
        schema="private",
    )
    op.create_index(
        op.f("ix_private_community_report_user_id"),
        "community_report",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "itinerary_day",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("dia", sa.Integer(), nullable=False),
        sa.CheckConstraint("dia >= 1", name=op.f("ck_itinerary_day_dia")),
        sa.ForeignKeyConstraint(
            ["itinerary_id"],
            ["private.itinerary.id"],
            name=op.f("fk_itinerary_day_itinerary_id_itinerary"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_itinerary_day")),
        sa.UniqueConstraint("itinerary_id", "dia", name="uq_itinerary_day_itinerary_dia"),
        schema="private",
    )
    op.create_table(
        "recommendation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("itinerary_id", sa.Integer(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("incluido", sa.Boolean(), nullable=False),
        sa.Column("alternativo", sa.Boolean(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["itinerary_id"],
            ["private.itinerary.id"],
            name=op.f("fk_recommendation_itinerary_id_itinerary"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_recommendation_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recommendation")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_recommendation_itinerary_id"),
        "recommendation",
        ["itinerary_id"],
        unique=False,
        schema="private",
    )
    op.create_index(
        op.f("ix_private_recommendation_poi_id"),
        "recommendation",
        ["poi_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "review",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("texto", sa.Text(), nullable=True),
        sa.Column("publica", sa.Boolean(), nullable=False),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_review_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_review_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_review")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_review_poi_id"), "review", ["poi_id"], unique=False, schema="private"
    )
    op.create_index(
        op.f("ix_private_review_user_id"), "review", ["user_id"], unique=False, schema="private"
    )
    op.create_table(
        "saved_place",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=True),
        sa.Column("nombre_propio", sa.String(length=300), nullable=True),
        sa.Column("nota", sa.Text(), nullable=True),
        sa.Column("url_origen", sa.Text(), nullable=True),
        sa.Column("plataforma_origen", sa.String(length=40), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "poi_id IS NOT NULL OR nombre_propio IS NOT NULL",
            name=op.f("ck_saved_place_poi_o_propio"),
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_saved_place_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_saved_place_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_saved_place")),
        sa.UniqueConstraint("user_id", "poi_id", name="uq_saved_place_user_poi"),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_saved_place_poi_id"),
        "saved_place",
        ["poi_id"],
        unique=False,
        schema="private",
    )
    op.create_index(
        op.f("ix_private_saved_place_user_id"),
        "saved_place",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "trip_session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("consent_id", sa.Integer(), nullable=True),
        sa.Column("version_consentimiento", sa.String(length=40), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column(
            "inicio", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("fin", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "estado IN ('activa', 'pausada', 'detenida')", name=op.f("ck_trip_session_estado")
        ),
        sa.ForeignKeyConstraint(
            ["consent_id"],
            ["private.consent_grant.id"],
            name=op.f("fk_trip_session_consent_id_consent_grant"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_trip_session_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trip_session")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_trip_session_user_id"),
        "trip_session",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "moderation_case",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_report_id", sa.Integer(), nullable=True),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("tipo", sa.String(length=30), nullable=False),
        sa.Column("atributo", sa.String(length=40), nullable=True),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=True),
        sa.Column("nota", sa.Text(), nullable=True),
        sa.Column("decidido_por", sa.UUID(), nullable=True),
        sa.Column("decidido_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "atributo IS NULL OR atributo IN ('acceso_sin_escalones', 'rampa', 'banio_accesible', 'elevador', 'superficie', 'asientos', 'estacionamiento_reservado', 'pendiente_pct', 'numero_escalones')",
            name=op.f("ck_moderation_case_atributo"),
        ),
        sa.CheckConstraint(
            "estado = 'abierto' OR (decidido_en IS NOT NULL AND decision IS NOT NULL)",
            name=op.f("ck_moderation_case_decision_completa"),
        ),
        sa.CheckConstraint(
            "estado IN ('abierto', 'aceptado', 'rechazado')", name=op.f("ck_moderation_case_estado")
        ),
        sa.CheckConstraint(
            "tipo IN ('escalones', 'rampa_bloqueada', 'sin_banio_accesible', 'superficie', 'senalizacion', 'otro')",
            name=op.f("ck_moderation_case_tipo"),
        ),
        sa.ForeignKeyConstraint(
            ["community_report_id"],
            ["private.community_report.id"],
            name=op.f("fk_moderation_case_community_report_id_community_report"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_moderation_case_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_moderation_case")),
        schema="audit",
    )
    op.create_index(
        op.f("ix_audit_moderation_case_community_report_id"),
        "moderation_case",
        ["community_report_id"],
        unique=False,
        schema="audit",
    )
    op.create_index(
        op.f("ix_audit_moderation_case_poi_id"),
        "moderation_case",
        ["poi_id"],
        unique=False,
        schema="audit",
    )
    op.create_table(
        "accessibility_evidence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("attribute_id", sa.Integer(), nullable=True),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("atributo", sa.String(length=40), nullable=False),
        sa.Column("valor", sa.String(length=80), nullable=True),
        sa.Column("origen", sa.String(length=40), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False),
        sa.Column("confianza", sa.Float(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("referencia", sa.String(length=120), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "atributo IN ('acceso_sin_escalones', 'rampa', 'banio_accesible', 'elevador', 'superficie', 'asientos', 'estacionamiento_reservado', 'pendiente_pct', 'numero_escalones')",
            name=op.f("ck_accessibility_evidence_atributo"),
        ),
        sa.CheckConstraint(
            "confianza >= 0 AND confianza <= 1", name=op.f("ck_accessibility_evidence_confianza")
        ),
        sa.ForeignKeyConstraint(
            ["attribute_id"],
            ["core.poi_accessibility_attribute.id"],
            name=op.f("fk_accessibility_evidence_attribute_id_poi_accessibility_attribute"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_accessibility_evidence_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accessibility_evidence")),
        schema="core",
    )
    op.create_index(
        op.f("ix_core_accessibility_evidence_poi_id"),
        "accessibility_evidence",
        ["poi_id"],
        unique=False,
        schema="core",
    )
    op.create_table(
        "itinerary_stop",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("day_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("llegada_min", sa.Float(), nullable=False),
        sa.Column("estancia_min", sa.Float(), nullable=False),
        sa.Column("traslado_min", sa.Float(), nullable=False),
        sa.Column("motivo", sa.Text(), nullable=True),
        sa.Column("advertencias", postgresql.ARRAY(sa.Text()), server_default="{}", nullable=False),
        sa.CheckConstraint(
            "llegada_min >= 0 AND estancia_min >= 0 AND traslado_min >= 0",
            name=op.f("ck_itinerary_stop_tiempos"),
        ),
        sa.ForeignKeyConstraint(
            ["day_id"],
            ["private.itinerary_day.id"],
            name=op.f("fk_itinerary_stop_day_id_itinerary_day"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_itinerary_stop_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_itinerary_stop")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_itinerary_stop_poi_id"),
        "itinerary_stop",
        ["poi_id"],
        unique=False,
        schema="private",
    )
    op.create_geospatial_table(
        "location_sample",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "geom",
            Geometry(
                geometry_type="POINT",
                srid=4326,
                dimension=2,
                spatial_index=False,
                from_text="ST_GeomFromEWKT",
                name="geometry",
                nullable=False,
            ),
            nullable=False,
        ),
        sa.Column("precision_m", sa.Float(), nullable=False),
        sa.Column("version_consentimiento", sa.String(length=40), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint("precision_m >= 0", name=op.f("ck_location_sample_precision")),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["private.trip_session.id"],
            name=op.f("fk_location_sample_session_id_trip_session"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_location_sample")),
        schema="private",
    )
    op.create_geospatial_index(
        "idx_location_sample_geom",
        "location_sample",
        ["geom"],
        unique=False,
        schema="private",
        postgresql_using="gist",
        postgresql_ops={},
    )
    op.create_index(
        op.f("ix_private_location_sample_session_id"),
        "location_sample",
        ["session_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "place_list_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("list_id", sa.Integer(), nullable=False),
        sa.Column("saved_place_id", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["list_id"],
            ["private.place_list.id"],
            name=op.f("fk_place_list_item_list_id_place_list"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["saved_place_id"],
            ["private.saved_place.id"],
            name=op.f("fk_place_list_item_saved_place_id_saved_place"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_place_list_item")),
        sa.UniqueConstraint("list_id", "saved_place_id", name="uq_place_list_item_list_saved"),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_place_list_item_list_id"),
        "place_list_item",
        ["list_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "recommendation_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("recommendation_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("util", sa.Boolean(), nullable=True),
        sa.Column("comentario", sa.Text(), nullable=True),
        sa.Column(
            "creado_en", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["recommendation_id"],
            ["private.recommendation.id"],
            name=op.f("fk_recommendation_feedback_recommendation_id_recommendation"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_recommendation_feedback_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_recommendation_feedback")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_recommendation_feedback_user_id"),
        "recommendation_feedback",
        ["user_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "review_dimension",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("review_id", sa.Integer(), nullable=False),
        sa.Column("dimension", sa.String(length=30), nullable=False),
        sa.Column("puntaje", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "dimension IN ('accesibilidad', 'limpieza', 'servicio', 'precio_percibido', 'senalizacion', 'comodidad', 'inclusion', 'global')",
            name=op.f("ck_review_dimension_dimension"),
        ),
        sa.CheckConstraint(
            "puntaje >= 1 AND puntaje <= 5", name=op.f("ck_review_dimension_puntaje")
        ),
        sa.ForeignKeyConstraint(
            ["review_id"],
            ["private.review.id"],
            name=op.f("fk_review_dimension_review_id_review"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_review_dimension")),
        sa.UniqueConstraint("review_id", "dimension", name="uq_review_dimension_review_dimension"),
        schema="private",
    )
    op.create_table(
        "visit_candidate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=True),
        sa.Column("inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fin", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duracion_min", sa.Float(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("fuente_evidencia", sa.String(length=40), nullable=False),
        sa.Column("precision_m", sa.Float(), nullable=False),
        sa.Column("confianza", sa.Float(), nullable=False),
        sa.Column("confirmada", sa.Boolean(), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "estado IN ('visita_probable', 'paso_cercano', 'desconocido')",
            name=op.f("ck_visit_candidate_estado"),
        ),
        sa.CheckConstraint(
            "confianza >= 0 AND confianza <= 1", name=op.f("ck_visit_candidate_confianza")
        ),
        sa.CheckConstraint("precision_m >= 0", name=op.f("ck_visit_candidate_precision")),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_visit_candidate_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["private.trip_session.id"],
            name=op.f("fk_visit_candidate_session_id_trip_session"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_visit_candidate")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_visit_candidate_poi_id"),
        "visit_candidate",
        ["poi_id"],
        unique=False,
        schema="private",
    )
    op.create_index(
        op.f("ix_private_visit_candidate_session_id"),
        "visit_candidate",
        ["session_id"],
        unique=False,
        schema="private",
    )
    op.create_table(
        "confirmed_visit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("poi_id", sa.String(length=80), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=True),
        sa.Column("fecha", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fuente_evidencia", sa.String(length=40), nullable=False),
        sa.Column("precision_m", sa.Float(), nullable=True),
        sa.Column("confianza", sa.Float(), nullable=False),
        sa.Column("confirmada", sa.Boolean(), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "fuente_evidencia IN ('gps_confirmado', 'check_in', 'manual')",
            name=op.f("ck_confirmed_visit_fuente_evidencia"),
        ),
        sa.CheckConstraint(
            "precision_m IS NOT NULL OR fuente_evidencia IN ('check_in', 'manual')",
            name=op.f("ck_confirmed_visit_precision_con_gps"),
        ),
        sa.CheckConstraint(
            "confianza >= 0 AND confianza <= 1", name=op.f("ck_confirmed_visit_confianza")
        ),
        sa.ForeignKeyConstraint(
            ["candidate_id"],
            ["private.visit_candidate.id"],
            name=op.f("fk_confirmed_visit_candidate_id_visit_candidate"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["poi_id"],
            ["core.point_of_interest.poi_id"],
            name=op.f("fk_confirmed_visit_poi_id_point_of_interest"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["private.user_account.id"],
            name=op.f("fk_confirmed_visit_user_id_user_account"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_confirmed_visit")),
        schema="private",
    )
    op.create_index(
        op.f("ix_private_confirmed_visit_poi_id"),
        "confirmed_visit",
        ["poi_id"],
        unique=False,
        schema="private",
    )
    op.create_index(
        op.f("ix_private_confirmed_visit_user_id"),
        "confirmed_visit",
        ["user_id"],
        unique=False,
        schema="private",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_private_confirmed_visit_user_id"), table_name="confirmed_visit", schema="private"
    )
    op.drop_index(
        op.f("ix_private_confirmed_visit_poi_id"), table_name="confirmed_visit", schema="private"
    )
    op.drop_table("confirmed_visit", schema="private")
    op.drop_index(
        op.f("ix_private_visit_candidate_session_id"),
        table_name="visit_candidate",
        schema="private",
    )
    op.drop_index(
        op.f("ix_private_visit_candidate_poi_id"), table_name="visit_candidate", schema="private"
    )
    op.drop_table("visit_candidate", schema="private")
    op.drop_table("review_dimension", schema="private")
    op.drop_index(
        op.f("ix_private_recommendation_feedback_user_id"),
        table_name="recommendation_feedback",
        schema="private",
    )
    op.drop_table("recommendation_feedback", schema="private")
    op.drop_index(
        op.f("ix_private_place_list_item_list_id"), table_name="place_list_item", schema="private"
    )
    op.drop_table("place_list_item", schema="private")
    op.drop_index(
        op.f("ix_private_location_sample_session_id"),
        table_name="location_sample",
        schema="private",
    )
    op.drop_geospatial_index(
        "idx_location_sample_geom",
        table_name="location_sample",
        schema="private",
        postgresql_using="gist",
        column_name="geom",
    )
    op.drop_geospatial_table("location_sample", schema="private")
    op.drop_index(
        op.f("ix_private_itinerary_stop_poi_id"), table_name="itinerary_stop", schema="private"
    )
    op.drop_table("itinerary_stop", schema="private")
    op.drop_index(
        op.f("ix_core_accessibility_evidence_poi_id"),
        table_name="accessibility_evidence",
        schema="core",
    )
    op.drop_table("accessibility_evidence", schema="core")
    op.drop_index(
        op.f("ix_audit_moderation_case_poi_id"), table_name="moderation_case", schema="audit"
    )
    op.drop_index(
        op.f("ix_audit_moderation_case_community_report_id"),
        table_name="moderation_case",
        schema="audit",
    )
    op.drop_table("moderation_case", schema="audit")
    op.drop_index(
        op.f("ix_private_trip_session_user_id"), table_name="trip_session", schema="private"
    )
    op.drop_table("trip_session", schema="private")
    op.drop_index(
        op.f("ix_private_saved_place_user_id"), table_name="saved_place", schema="private"
    )
    op.drop_index(op.f("ix_private_saved_place_poi_id"), table_name="saved_place", schema="private")
    op.drop_table("saved_place", schema="private")
    op.drop_index(op.f("ix_private_review_user_id"), table_name="review", schema="private")
    op.drop_index(op.f("ix_private_review_poi_id"), table_name="review", schema="private")
    op.drop_table("review", schema="private")
    op.drop_index(
        op.f("ix_private_recommendation_poi_id"), table_name="recommendation", schema="private"
    )
    op.drop_index(
        op.f("ix_private_recommendation_itinerary_id"),
        table_name="recommendation",
        schema="private",
    )
    op.drop_table("recommendation", schema="private")
    op.drop_table("itinerary_day", schema="private")
    op.drop_index(
        op.f("ix_private_community_report_user_id"), table_name="community_report", schema="private"
    )
    op.drop_index(
        op.f("ix_private_community_report_poi_id"), table_name="community_report", schema="private"
    )
    op.drop_table("community_report", schema="private")
    op.drop_index(op.f("ix_private_check_in_user_id"), table_name="check_in", schema="private")
    op.drop_index(op.f("ix_private_check_in_poi_id"), table_name="check_in", schema="private")
    op.drop_table("check_in", schema="private")
    op.drop_table("provider", schema="core")
    op.drop_table("poi_accessibility_attribute", schema="core")
    op.drop_index(op.f("ix_core_opening_hours_poi_id"), table_name="opening_hours", schema="core")
    op.drop_table("opening_hours", schema="core")
    op.drop_index(
        op.f("ix_analytics_aggregate_metric_metric_id"),
        table_name="aggregate_metric",
        schema="analytics",
    )
    op.drop_index(
        op.f("ix_analytics_aggregate_metric_destino_id"),
        table_name="aggregate_metric",
        schema="analytics",
    )
    op.drop_table("aggregate_metric", schema="analytics")
    op.drop_table("user_accessibility_preference", schema="private")
    op.drop_table("privacy_preference", schema="private")
    op.drop_index(op.f("ix_private_place_list_user_id"), table_name="place_list", schema="private")
    op.drop_table("place_list", schema="private")
    op.drop_index(
        op.f("ix_private_media_asset_user_id"), table_name="media_asset", schema="private"
    )
    op.drop_table("media_asset", schema="private")
    op.drop_index(op.f("ix_private_itinerary_user_id"), table_name="itinerary", schema="private")
    op.drop_table("itinerary", schema="private")
    op.drop_index(
        op.f("ix_private_consent_grant_user_id"), table_name="consent_grant", schema="private"
    )
    op.drop_table("consent_grant", schema="private")
    op.drop_index(
        op.f("ix_core_point_of_interest_destino_id"), table_name="point_of_interest", schema="core"
    )
    op.drop_index(
        op.f("ix_core_point_of_interest_corredor_id"), table_name="point_of_interest", schema="core"
    )
    op.drop_index(
        op.f("ix_core_point_of_interest_categoria"), table_name="point_of_interest", schema="core"
    )
    op.drop_geospatial_index(
        "idx_point_of_interest_geom",
        table_name="point_of_interest",
        schema="core",
        postgresql_using="gist",
        column_name="geom",
    )
    op.drop_geospatial_table("point_of_interest", schema="core")
    op.drop_table("metric_definition", schema="core")
    op.drop_table("data_lineage", schema="core")
    op.drop_table("user_account", schema="private")
    op.drop_geospatial_index(
        "idx_destination_geom",
        table_name="destination",
        schema="core",
        postgresql_using="gist",
        column_name="geom",
    )
    op.drop_geospatial_table("destination", schema="core")
    op.drop_table("data_source", schema="core")
    op.drop_geospatial_index(
        "idx_corridor_geom",
        table_name="corridor",
        schema="core",
        postgresql_using="gist",
        column_name="geom",
    )
    op.drop_geospatial_table("corridor", schema="core")
    op.drop_table("audit_event", schema="audit")
    op.execute("DROP EXTENSION IF EXISTS unaccent")
