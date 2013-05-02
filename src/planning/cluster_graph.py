from pydot import Node, Edge, Dot

import htmlentitydefs
import re
import string
import database as db

# this pattern matches substrings of reserved and non-ASCII characters
from database.model import Team

pattern = re.compile(r"[&<>\"\x80-\xff]+")

# create character map
entity_map = {}

for i in range(256):
    entity_map[chr(i)] = "&#%d;" % i

for entity, char in htmlentitydefs.entitydefs.items():
    if entity_map.has_key(char):
        entity_map[char] = "&%s;" % entity


def escape_entity(m, get=entity_map.get):
    return string.join(map(get, m.group()), "")


def escape(string):
    return pattern.sub(escape_entity, string)


colors = {0: "#ffbbbb",
          1: "#bbffbb",
          2: "#bbbbff"}

types = {0: "Vorspeise",
         1: "Hauptgang",
         2: "Nachspeise"}


def make_nodes(plan, teams):
    nodes = {}
    for team in plan:
        team_part = plan[team].index(team)
        teamname = escape(teams[team].name.encode("latin1"))
        nodes[team] = Node(team,
                           label=u"%s\\n%s" % (teamname, types[team_part]),
                           style="filled",
                           fillcolor=colors[team_part])
    return nodes


def graph_way(team, team_plan, nodes):
    edges = []
    for station in team_plan:
        if station != team:
            edges.append(Edge(nodes[team], nodes[station]))
    return edges


def fetch_teams():
    teams = {}
    for team in db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True):
        teams[str(team.id)] = team
    return teams


def process_plan(filename, plan):
    graph = Dot()
    teams = fetch_teams()

    nodes = make_nodes(plan, teams)

    for team_node in nodes:
        graph.add_node(nodes[team_node])

    for team in plan:
        edges = graph_way(team, plan[team], nodes)
        for edge in edges:
            graph.add_edge(edge)

    graph.set_prog("circo")
    graph.write_png(filename)