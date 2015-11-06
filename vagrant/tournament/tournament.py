#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("delete from matches")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    c = DB.cursor()
    c.execute("delete from players")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    c = DB.cursor()
    c.execute("select count(*) as num from players")
    player_count = c.fetchone()
    return player_count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    c = DB.cursor()
    c.execute("insert into players (name) values (%s)", (name,))
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
    DB = connect()
    c = DB.cursor()
    c.execute("select players.id, players.name, count(matches.player_id1) as num \
        from players left join matches \
        on players.id = matches.player_id1 \
        group by players.id \
        order by players.id")
    win_table = c.fetchall()
    #print win_table
    c.execute("select players.id, players.name, count(matches.player_id2) as num \
    from players left join matches \
    on players.id = matches.player_id2 \
    group by players.id \
    order by players.id")
    lose_table = c.fetchall()
    #print lose_table
    standings_list = []
    for i in range(len(win_table)):
        standing = (win_table[i][0], win_table[i][1], win_table[i][2],
        win_table[i][2] + lose_table[i][2] )
        standings_list.append(standing)
    standings_list = sorted(standings_list, key=lambda standing:standing[2], reverse=True)
    #print standings_list
    DB.close()
    return standings_list



def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    c = DB.cursor()
    c.execute("insert into matches (player_id1, player_id2) values (%s, %s)", (winner, loser))
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
    while i < len(standings):
        pair = (standings[i][0], standings[i][1], standings[i+1][0], standings[i+1][1])
        pairs.append(pair)
        i += 2
    return pairs


