--
-- PostgreSQL database dump
--

\restrict Au4aTOE2eomCeXMla6k8HdutaWSbJL6bBlUklmHuDa4qjp1iBc77bFnvsQBf04g

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
-- Data for Name: dispositions; Type: TABLE DATA; Schema: app; Owner: -
--

INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'renewed', 'Policy renewed', true, true);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'payment_link_sent', 'Payment link sent', false, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'callback_requested', 'Callback requested', false, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'not_interested', 'Not interested', true, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'wrong_number', 'Wrong number', true, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'already_renewed_elsewhere', 'Renewed with another insurer', true, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'language_barrier', 'Language barrier', false, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('motor_renewal', 'dnd', 'Do not disturb', true, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('policy_feedback', 'feedback_captured', 'Feedback captured', true, true);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('policy_feedback', 'partial_feedback', 'Partial feedback', false, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('policy_feedback', 'callback_requested', 'Callback requested', false, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('policy_feedback', 'refused', 'Refused', true, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('policy_feedback', 'wrong_number', 'Wrong number', true, false);
INSERT INTO app.dispositions (workflow_id, code, label, is_terminal, is_success) VALUES ('policy_feedback', 'dnd', 'Do not disturb', true, false);


--
-- PostgreSQL database dump complete
--

\unrestrict Au4aTOE2eomCeXMla6k8HdutaWSbJL6bBlUklmHuDa4qjp1iBc77bFnvsQBf04g
