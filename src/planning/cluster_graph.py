from pydot import Node, Edge, Dot
from collections import defaultdict

import htmlentitydefs
import re
import string
import database as db

# this pattern matches substrings of reserved and non-ASCII characters
from database.model import Team, RouteDistance

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


def make_nodes(plan, teams, names=True):
    nodes = {}
    for team in plan:
        team_part = plan[team].index(team)
        if names:
            teamname = escape(teams[team].name.encode("latin1"))
        else:
            teamname = "Team %s" % team
        nodes[team] = Node(team,
                           label=u"%s\\n%s" % (teamname, types[team_part]),
                           style="filled",
                           fillcolor=colors[team_part])
    return nodes


def graph_way(team, team_plan, nodes, distances=None, with_dist=False, with_label=False):
    edges = []
    for station in team_plan:
        if station != team:
            edge_args = {}
            length = distances[team][station] / 1000.0
            if with_dist:
                edge_args.update(dict(len=length*2, w=100))
            if with_label:
                edge_args.update(dict(label="%0.1fkm" % length,
                                      fontcolor="gray"))

            edge = Edge(nodes[team], nodes[station], **edge_args)
            edges.append(edge)
    return edges


def fetch_teams():
    teams = {}
    for team in db.session.query(Team).filter_by(deleted=False).filter_by(confirmed=True, backup=False):
        teams[str(team.id)] = team
    return teams


def fetch_distances():
    distances = defaultdict(dict)
    for dist in db.session.query(RouteDistance):
        distances[str(dist.location_from.team_id)][str(dist.location_to.team_id)] = dist.distance

    return distances


def process_plan(filename, plan, names=True, with_dist=False, with_label=False):
    graph = Dot(overlap="false", splines="true", esep=.2)
    teams = fetch_teams()

    distances = fetch_distances()

    nodes = make_nodes(plan, teams, names)

    for team_node in nodes:
        graph.add_node(nodes[team_node])

    for team in plan:
        edges = graph_way(team, plan[team], nodes, distances, with_dist, with_label)
        for edge in edges:
            graph.add_edge(edge)

    if with_dist:
        graph.write_png(filename, prog="neato")
    else:
        graph.write_png(filename, prog="dot")
