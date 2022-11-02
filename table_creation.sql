CREATE TABLE IF NOT EXISTS public.usuarios_registrados
(
    "ID" bigint NOT NULL,
    "PRIMER_NOMBRE" text COLLATE pg_catalog."default",
    "APELLIDO_PAT" text COLLATE pg_catalog."default",
    "APELLIDO_MAT" text COLLATE pg_catalog."default",
    "FECHA_NAC" date,
    "RFC" text COLLATE pg_catalog."default",
    "INGRESOS_MENSUALES" money,
    "DEPENDIENTES" integer,
    "APROBADO" boolean,
    CONSTRAINT usuarios_registrados_pkey PRIMARY KEY ("ID")
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.usuarios_registrados
    OWNER to postgres;