-- FabPilot synthetic fab business schema (read-only for the agent).
-- 100% synthetic: generic names, no real products, tools, recipes or specs from any company.
-- Grain: product -> route -> process_step; lot -> wafer; history/measurement keyed by step.

CREATE SCHEMA IF NOT EXISTS fab;
SET search_path = fab;

CREATE TABLE product (
    product_id       text PRIMARY KEY,           -- e.g. 'PRD-A'
    product_name     text NOT NULL,
    technology_node  text NOT NULL,              -- e.g. '55nm' (label only)
    wafer_size_mm    smallint NOT NULL DEFAULT 300,
    gross_die        integer NOT NULL            -- dies per wafer
);

CREATE TABLE route (
    route_id    text PRIMARY KEY,
    product_id  text NOT NULL REFERENCES product,
    version     smallint NOT NULL DEFAULT 1
);

CREATE TABLE process_step (
    step_id         text PRIMARY KEY,            -- e.g. 'R-A-0040'
    route_id        text NOT NULL REFERENCES route,
    seq             smallint NOT NULL,
    step_name       text NOT NULL,               -- e.g. 'POLY ETCH'
    module          text NOT NULL,               -- LITHO / ETCH / THIN_FILM / CMP / IMPLANT / DIFF / CLEAN / METRO
    equipment_type  text NOT NULL,
    UNIQUE (route_id, seq)
);

CREATE TABLE equipment (
    equipment_id    text PRIMARY KEY,            -- e.g. 'ETCH-03'
    equipment_type  text NOT NULL,
    module          text NOT NULL,
    bay             text NOT NULL,
    chamber_count   smallint NOT NULL DEFAULT 1,
    status          text NOT NULL DEFAULT 'UP'   -- UP / DOWN / PM / IDLE
);

CREATE TABLE lot (
    lot_id         text PRIMARY KEY,             -- e.g. 'L26A0001'
    product_id     text NOT NULL REFERENCES product,
    route_id       text NOT NULL REFERENCES route,
    priority       smallint NOT NULL DEFAULT 3,  -- 1 = hot lot
    wafer_qty      smallint NOT NULL,
    start_time     timestamptz NOT NULL,
    finish_time    timestamptz,
    status         text NOT NULL                 -- WIP / HOLD / FINISHED / SCRAPPED
);

CREATE TABLE wafer (
    wafer_id  text PRIMARY KEY,                  -- '<lot_id>.<slot>'
    lot_id    text NOT NULL REFERENCES lot,
    slot_no   smallint NOT NULL,
    UNIQUE (lot_id, slot_no)
);

-- One row per lot per step it went through (track-in / track-out).
CREATE TABLE lot_step_history (
    lot_id        text NOT NULL REFERENCES lot,
    step_id       text NOT NULL REFERENCES process_step,
    equipment_id  text NOT NULL REFERENCES equipment,
    chamber       smallint,
    recipe        text NOT NULL,
    track_in      timestamptz NOT NULL,
    track_out     timestamptz,
    PRIMARY KEY (lot_id, step_id)
);

-- Spec per measured parameter at a metrology step.
CREATE TABLE parameter_spec (
    param_name  text NOT NULL,                   -- e.g. 'POLY_CD'
    step_id     text NOT NULL REFERENCES process_step,
    unit        text NOT NULL,
    target      double precision NOT NULL,
    lsl         double precision NOT NULL,
    usl         double precision NOT NULL,
    PRIMARY KEY (param_name, step_id)
);

-- Inline metrology, site level.
CREATE TABLE measurement (
    measurement_id  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    wafer_id        text NOT NULL REFERENCES wafer,
    step_id         text NOT NULL REFERENCES process_step,
    param_name      text NOT NULL,
    site_no         smallint NOT NULL,
    value           double precision NOT NULL,
    measured_at     timestamptz NOT NULL,
    FOREIGN KEY (param_name, step_id) REFERENCES parameter_spec
);

CREATE TABLE defect_inspection (
    wafer_id      text NOT NULL REFERENCES wafer,
    step_id       text NOT NULL REFERENCES process_step,
    defect_count  integer NOT NULL,
    inspected_at  timestamptz NOT NULL,
    PRIMARY KEY (wafer_id, step_id)
);

-- End-of-line wafer sort / CP result.
CREATE TABLE wafer_yield (
    wafer_id      text PRIMARY KEY REFERENCES wafer,
    gross_die     integer NOT NULL,
    good_die      integer NOT NULL,
    yield_pct     numeric(5, 2) NOT NULL,
    map_pattern   text,                          -- WM-811K style label: none / center / edge-ring / scratch ...
    tested_at     timestamptz NOT NULL
);

CREATE TABLE equipment_event (
    event_id      bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    equipment_id  text NOT NULL REFERENCES equipment,
    event_time    timestamptz NOT NULL,
    event_type    text NOT NULL,                 -- ALARM / PM_START / PM_END / DOWN / UP
    code          text,
    message       text
);

CREATE TABLE lot_hold (
    hold_id       bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lot_id        text NOT NULL REFERENCES lot,
    step_id       text REFERENCES process_step,
    hold_time     timestamptz NOT NULL,
    release_time  timestamptz,
    reason_code   text NOT NULL,                 -- OOS / OOC / EQP_ALARM / ENG_REQUEST
    comment       text
);

CREATE INDEX ON lot (product_id, start_time);
CREATE INDEX ON wafer (lot_id);
CREATE INDEX ON lot_step_history (equipment_id, track_in);
CREATE INDEX ON measurement (step_id, param_name, measured_at);
CREATE INDEX ON measurement (wafer_id);
CREATE INDEX ON equipment_event (equipment_id, event_time);
CREATE INDEX ON lot_hold (lot_id);

COMMENT ON SCHEMA fab IS 'Synthetic semiconductor fab data. Generated by fabpilot-datagen; no real company data.';
