#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        db = psycopg2.connect("dbname=tournament")
        cursor = db.cursor()
    except:
        print ("Error: cannot onnection to tournament database!")
    return db, cursor


def deleteMatches():
    """Remove all the match records from the database."""
    DB, c = connect()
    c.execute("DELETE FROM matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB, c = connect()
    c.execute("DELETE FROM players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB, c = connect()
    c.execute("SELECT count(*) AS num FROM players")
    player_count = c.fetchone()
    return player_count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB, c = connect()
    c.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    DB, c = connect()

    # in the 1st submission, reviewer said that I would double-count the players
    # But players.id can only appear in winnder_id, or loser_id or none in one match
    # so by counting players.id appearance as winner_id and loser_id,
    # adding two together should give the total of matches the player has played so far, not just one-round match only.
    # adding a fake pair in tournament_test.py in testPairings()

    query = "SELECT players.id, players.name, \
    (SELECT count(*) FROM matches WHERE winner_id = players.id) AS num_of_wins, \
    (SELECT count(*) FROM matches WHERE winner_id = players.id OR loser_id = players.id) AS num_of_matches \
    FROM players \
    ORDER BY num_of_wins DESC \
    "
    c.execute(query)
    standings_list = c.fetchall()
    #print standings_list

    DB.close()
    return standings_list



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB, c = connect()
    c.execute("INSERT INTO matches (winner_id, loser_id) VALUES (%s, %s)", (winner, loser))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    pairs = []
    i = 0
    if len(standings) % 2 != 0:
        raise ValueError("Number of players should be even number!")
    while i < len(standings):
        pair = (standings[i][0], standings[i][1], standings[i+1][0], standings[i+1][1])
        pairs.append(pair)
        i += 2
    return pairs


