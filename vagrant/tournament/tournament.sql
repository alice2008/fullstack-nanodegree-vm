-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;
CREATE TABLE players ( id serial PRIMARY KEY,
					name text NOT NULL
					);

CREATE TABLE matches ( match_id serial PRIMARY KEY,
					winner_id int REFERENCES players(id) ON DELETE CASCADE,
					loser_id int REFERENCES players(id) ON DELETE CASCADE,
					CHECK(winner_id <> loser_id)
					);

