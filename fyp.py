import json

from static import *
from functions import *
from models import *
from collections import deque

import csv

class Vertex:
    def __init__(self, id):
        self.id = id
        self.adjacent = set()

    def add_edge(self, other_id):
        self.adjacent.add(other_id)

    def remove_edge(self, other_id):
        self.adjacent.discard(other_id)

    def to_dict(self):
        return {
            "id": self.id,
            "adjacent": list(self.adjacent)
        }

    @classmethod
    def from_dict(cls, data):
        v = cls(data["id"])
        v.adjacent = set(data["adjacent"])
        return v



class Graph:
    def __init__(self):
        self.vertices = {}
        self.update(USERS_DB)

    def add_vertex(self, id):
        if id not in self.vertices:
            self.vertices[id] = Vertex(id)

    def add_edge(self, id1, id2):
        self.add_vertex(id1)
        self.add_vertex(id2)
        self.vertices[id1].add_edge(id2)
        self.vertices[id2].add_edge(id1)

    def remove_edge(self, id1, id2):
        if id1 in self.vertices:
            self.vertices[id1].remove_edge(id2)
        if id2 in self.vertices:
            self.vertices[id2].remove_edge(id1)

    def to_dict(self):
        return {id: vertex.to_dict() for id, vertex in self.vertices.items()}

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        graph = cls()
        with open(filename, 'r') as f:
            data = json.load(f)
            for id, vdata in data.items():
                graph.vertices[id] = Vertex.from_dict(vdata)
        return graph

    def update(self, users_file):
        users = []
        with open(users_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(User(row["id"], row["username"]))

        for i in range(len(users)):
            for j in range(i, len(users)):
                print(f"{users[i].name} and {users[j].name} are Freinds? {are_friends(users[i].name, users[j].name)}")
                if are_friends(users[i].name, users[j].name):
                    self.add_edge(users[i].id, users[j].id)

        self.save_to_file(GRAPH_DB)

    def bfs(self, start, deep):
        if start not in self.vertices:
            return []

        visited = set()
        queue = deque([(start, 0)])
        result = []

        while queue:
            current, depth = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if depth == deep:
                result.append(current)
            elif depth < deep:
                for neighbor in self.vertices[current].adjacent:
                    if neighbor not in visited:
                        queue.append((neighbor, depth + 1))

        return result





g = Graph()


print(g.bfs("1",2))










