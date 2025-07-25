-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.match (
  match_id text NOT NULL,
  round text NOT NULL,
  round_order integer NOT NULL,
  bracket_order integer NOT NULL,
  tournament_id text NOT NULL,
  result_type text,
  fall_time text,
  tech_time text,
  winner_id text,
  CONSTRAINT match_pkey PRIMARY KEY (match_id),
  CONSTRAINT match_tournament_id_fkey FOREIGN KEY (tournament_id) REFERENCES public.tournament(tournament_id),
  CONSTRAINT match_winner_id_fkey FOREIGN KEY (winner_id) REFERENCES public.participant(participant_id)
);
CREATE TABLE public.participant (
  participant_id text NOT NULL,
  role_id text NOT NULL,
  school_id text NOT NULL,
  year integer NOT NULL,
  weight_class text NOT NULL,
  seed integer,
  CONSTRAINT participant_pkey PRIMARY KEY (participant_id),
  CONSTRAINT participant_school_id_fkey FOREIGN KEY (school_id) REFERENCES public.school(school_id),
  CONSTRAINT participant_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.role(role_id)
);
CREATE TABLE public.participant_match (
  match_id text NOT NULL,
  participant_id text NOT NULL,
  is_winner boolean,
  score integer,
  next_match_id text,
  CONSTRAINT participant_match_pkey PRIMARY KEY (match_id, participant_id),
  CONSTRAINT participant_match_participant_id_fkey FOREIGN KEY (participant_id) REFERENCES public.participant(participant_id),
  CONSTRAINT participant_match_match_id_fkey FOREIGN KEY (match_id) REFERENCES public.match(match_id),
  CONSTRAINT participant_match_next_match_id_fkey FOREIGN KEY (next_match_id) REFERENCES public.match(match_id)
);
CREATE TABLE public.person (
  person_id text NOT NULL,
  first_name text NOT NULL,
  last_name text NOT NULL,
  search_name text,
  date_of_birth date,
  city_of_origin text,
  state_of_origin text,
  CONSTRAINT person_pkey PRIMARY KEY (person_id)
);
CREATE TABLE public.role (
  role_id text NOT NULL,
  person_id text NOT NULL,
  role_type text CHECK (role_type = ANY (ARRAY['wrestler'::text, 'coach'::text])),
  CONSTRAINT role_pkey PRIMARY KEY (role_id),
  CONSTRAINT role_person_id_fkey FOREIGN KEY (person_id) REFERENCES public.person(person_id)
);
CREATE TABLE public.school (
  school_id text NOT NULL,
  name text NOT NULL,
  location text,
  mascot text,
  school_type text,
  school_url text,
  CONSTRAINT school_pkey PRIMARY KEY (school_id)
);
CREATE TABLE public.tournament (
  tournament_id text NOT NULL,
  name text NOT NULL,
  date date NOT NULL,
  year integer,
  location text,
  CONSTRAINT tournament_pkey PRIMARY KEY (tournament_id)
);