--
-- PostgreSQL database dump
--

\restrict 7MZSpxPSZTkISrcl26lf9tnm7lFVSiV7c6vaOYIZWUdRdxNFkIrbjbdQVhfaGSf

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: app; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA app;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: dispositions; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.dispositions (
    workflow_id character varying(100) NOT NULL,
    code character varying(100) NOT NULL,
    label character varying(255) NOT NULL,
    is_terminal boolean NOT NULL,
    is_success boolean NOT NULL
);


--
-- Name: event_lead_links; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.event_lead_links (
    event_id character varying(150) NOT NULL,
    lead_id bigint NOT NULL,
    linked_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: field_warnings; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.field_warnings (
    warning_id bigint NOT NULL,
    workflow_id character varying(100) NOT NULL,
    batch_id character varying(100) NOT NULL,
    source_file character varying(255) NOT NULL,
    row_number integer NOT NULL,
    field_name character varying(100) NOT NULL,
    reason character varying(255) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: field_warnings_warning_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.field_warnings_warning_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: field_warnings_warning_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.field_warnings_warning_id_seq OWNED BY app.field_warnings.warning_id;


--
-- Name: ingestion_files; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.ingestion_files (
    file_id bigint NOT NULL,
    file_path character varying(500) NOT NULL,
    file_type character varying(20) NOT NULL,
    workflow_id character varying(100),
    batch_id character varying(100),
    content_sha256 character varying(64) NOT NULL,
    status character varying(20) DEFAULT 'processing'::character varying NOT NULL,
    metrics jsonb DEFAULT '{}'::jsonb NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    completed_at timestamp with time zone,
    CONSTRAINT chk_file_type CHECK (((file_type)::text = ANY ((ARRAY['lead_csv'::character varying, 'event_jsonl'::character varying])::text[]))),
    CONSTRAINT chk_ingestion_status CHECK (((status)::text = ANY ((ARRAY['processing'::character varying, 'completed'::character varying, 'failed'::character varying])::text[])))
);


--
-- Name: ingestion_files_file_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.ingestion_files_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ingestion_files_file_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.ingestion_files_file_id_seq OWNED BY app.ingestion_files.file_id;


--
-- Name: interaction_events; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.interaction_events (
    event_id character varying(150) NOT NULL,
    event_type character varying(100) NOT NULL,
    workflow_id character varying(100) NOT NULL,
    call_id character varying(150),
    occurred_at timestamp with time zone NOT NULL,
    phone_lookup_hash bytea,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    source_file character varying(255) NOT NULL,
    line_number integer NOT NULL,
    ingested_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: lead_rejections; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.lead_rejections (
    rejection_id bigint NOT NULL,
    workflow_id character varying(100) NOT NULL,
    batch_id character varying(100) NOT NULL,
    source_file character varying(255) NOT NULL,
    row_number integer NOT NULL,
    reason character varying(255) NOT NULL,
    rejected_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: lead_rejections_rejection_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.lead_rejections_rejection_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: lead_rejections_rejection_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.lead_rejections_rejection_id_seq OWNED BY app.lead_rejections.rejection_id;


--
-- Name: leads; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.leads (
    lead_id bigint NOT NULL,
    workflow_id character varying(100) NOT NULL,
    batch_id character varying(100) NOT NULL,
    external_ref character varying(255) NOT NULL,
    phone_lookup_hash bytea NOT NULL,
    phone_encrypted bytea NOT NULL,
    customer_name_encrypted bytea NOT NULL,
    attributes jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: leads_lead_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.leads_lead_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: leads_lead_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.leads_lead_id_seq OWNED BY app.leads.lead_id;


--
-- Name: field_warnings warning_id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.field_warnings ALTER COLUMN warning_id SET DEFAULT nextval('app.field_warnings_warning_id_seq'::regclass);


--
-- Name: ingestion_files file_id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.ingestion_files ALTER COLUMN file_id SET DEFAULT nextval('app.ingestion_files_file_id_seq'::regclass);


--
-- Name: lead_rejections rejection_id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.lead_rejections ALTER COLUMN rejection_id SET DEFAULT nextval('app.lead_rejections_rejection_id_seq'::regclass);


--
-- Name: leads lead_id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.leads ALTER COLUMN lead_id SET DEFAULT nextval('app.leads_lead_id_seq'::regclass);


--
-- Name: dispositions dispositions_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.dispositions
    ADD CONSTRAINT dispositions_pkey PRIMARY KEY (workflow_id, code);


--
-- Name: event_lead_links event_lead_links_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.event_lead_links
    ADD CONSTRAINT event_lead_links_pkey PRIMARY KEY (event_id);


--
-- Name: field_warnings field_warnings_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.field_warnings
    ADD CONSTRAINT field_warnings_pkey PRIMARY KEY (warning_id);


--
-- Name: field_warnings field_warnings_source_file_row_number_field_name_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.field_warnings
    ADD CONSTRAINT field_warnings_source_file_row_number_field_name_key UNIQUE (source_file, row_number, field_name);


--
-- Name: ingestion_files ingestion_files_file_path_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.ingestion_files
    ADD CONSTRAINT ingestion_files_file_path_key UNIQUE (file_path);


--
-- Name: ingestion_files ingestion_files_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.ingestion_files
    ADD CONSTRAINT ingestion_files_pkey PRIMARY KEY (file_id);


--
-- Name: interaction_events interaction_events_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.interaction_events
    ADD CONSTRAINT interaction_events_pkey PRIMARY KEY (event_id);


--
-- Name: lead_rejections lead_rejections_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.lead_rejections
    ADD CONSTRAINT lead_rejections_pkey PRIMARY KEY (rejection_id);


--
-- Name: lead_rejections lead_rejections_source_file_row_number_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.lead_rejections
    ADD CONSTRAINT lead_rejections_source_file_row_number_key UNIQUE (source_file, row_number);


--
-- Name: leads leads_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.leads
    ADD CONSTRAINT leads_pkey PRIMARY KEY (lead_id);


--
-- Name: leads leads_workflow_id_phone_lookup_hash_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.leads
    ADD CONSTRAINT leads_workflow_id_phone_lookup_hash_key UNIQUE (workflow_id, phone_lookup_hash);


--
-- Name: idx_event_links_lead; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_event_links_lead ON app.event_lead_links USING btree (lead_id);


--
-- Name: idx_events_call_id; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_events_call_id ON app.interaction_events USING btree (call_id);


--
-- Name: idx_events_occurred_at; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_events_occurred_at ON app.interaction_events USING btree (occurred_at);


--
-- Name: idx_events_phone; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_events_phone ON app.interaction_events USING btree (workflow_id, phone_lookup_hash);


--
-- Name: idx_ingestion_files_status; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_ingestion_files_status ON app.ingestion_files USING btree (status);


--
-- Name: idx_rejections_workflow_batch; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_rejections_workflow_batch ON app.lead_rejections USING btree (workflow_id, batch_id);


--
-- Name: idx_warnings_workflow_batch; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_warnings_workflow_batch ON app.field_warnings USING btree (workflow_id, batch_id);


--
-- Name: event_lead_links event_lead_links_event_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.event_lead_links
    ADD CONSTRAINT event_lead_links_event_id_fkey FOREIGN KEY (event_id) REFERENCES app.interaction_events(event_id);


--
-- Name: event_lead_links event_lead_links_lead_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.event_lead_links
    ADD CONSTRAINT event_lead_links_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES app.leads(lead_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 7MZSpxPSZTkISrcl26lf9tnm7lFVSiV7c6vaOYIZWUdRdxNFkIrbjbdQVhfaGSf
