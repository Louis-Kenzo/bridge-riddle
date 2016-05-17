#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import itertools
import collections
from operator import attrgetter

START_PLACE_NAME = "Peak"
END_PLACE_NAME = "Safety"
LIMIT_TIME = 17.0

class Person:
	def __init__(self, name, bridge_crossing_time):
		self.name  = name
		self.bridge_crossing_time = bridge_crossing_time

	def __unicode__(self):
		return self.name

class Move:
	def __init__(self, persons, origin, target):
		if isinstance(persons, collections.Iterable):
			assert(1 <= len(persons) <= 2)
			self.persons = persons
		else:
			self.persons = [persons]

		self.origin  = origin
		self.target  = target

	@property
	def time(self):
		return max([p.bridge_crossing_time for p in self.persons])

	def __unicode__(self):
		return u"{origin} ————({names} | {time}min)————► {target}".format(names = ", ".join([unicode(p) for p in self.persons]),
		                                                              origin = self.origin,
		                                                              target = self.target,
		                                                              time   = self.time)

	def __str__(self):
		return unicode(self).replace(u"—", "-").replace(u"►", ">")

	@property
	def dotstring(self):
		return "\"" + ", ".join([unicode(p) for p in self.persons]) + "\""

class State:
	def __init__(self, people_locations, lantern_location, time = 0.0):
		self.people_locations = people_locations
		self.lantern_location = lantern_location
		self.time = time

	@property
	def possible_destinations(self):
		return [l for l in self.people_locations.iterkeys() if l != self.lantern_location]

	@property
	def people_with_lantern(self):
		return sorted(self.people_locations[self.lantern_location],
		              key = attrgetter("bridge_crossing_time"))

	@property
	def possible_groups(self):
		return itertools.chain(self.people_with_lantern, itertools.combinations(self.people_with_lantern, 2))

	@property
	def possible_moves(self):
		return [Move(persons = group,
		              origin = self.lantern_location,
		              target = destination)
		        for group in self.possible_groups
		        for destination in self.possible_destinations]

	@property
	def sane_moves(self):
		return [Move(persons = group,
		              origin = self.lantern_location,
		              target = destination)
		        for group in self.possible_groups
		        for destination in self.possible_destinations
		        if destination == START_PLACE_NAME and isinstance(group, Person) \
		        or destination == END_PLACE_NAME   and isinstance(group, collections.Iterable) and len(group) == 2]

	def executeMove(self, move):
		for p in move.persons:
			assert p in self.people_locations[move.origin], "Impossible move"

		moved_people_locations = {}
		for l in self.people_locations.iterkeys():
			moved_people_locations[l] = copy.copy(self.people_locations[l])

		for p in move.persons:
			moved_people_locations[move.origin].remove(p)
			moved_people_locations[move.target].add(p)

		return State(people_locations = moved_people_locations,
		             lantern_location = move.target,
		             time = self.time + move.time)

	@property
	def _time_string(self):
		return "%s min" % self.time

	@property
	def _people_locations_string(self):
		return "\\n".join(location + ": "+", ".join([unicode(p) for p in sorted(self.people_locations[location], key=attrgetter("bridge_crossing_time"))])+""
		                                             for location in sorted(self.people_locations.iterkeys()) if self.people_locations[location])

	def __unicode__(self):
		return self._time_string + ": " + self._people_locations_string

	@property
	def dotstring_id(self):
		return "\"" + self._time_string + "\\n" + self._people_locations_string + "\""

	@property
	def dotstring(self):
		if self.is_victory:
			return self.dotstring_id + " [ penwidth=3 style=filled fillcolor=green ]"
		else:
			return self.dotstring_id + " [ colorscheme=rdylgn11 fontcolor={} ]".format(int(1.0+(1.0-self.criticity)*10.0))

	@property
	def is_alive(self):
		return self.time <= LIMIT_TIME

	@property
	def is_victory(self):
		return self.is_alive and len(self.people_locations[START_PLACE_NAME]) == 0

	@property
	def criticity(self):
		return max(min(self.time / LIMIT_TIME, 1.0), 0.0)

def dotstringMove(initial_state, move, moved_state):
	print "\t" + initial_state.dotstring
	print "\t" + moved_state.dotstring
	return "\t" + initial_state.dotstring_id \
	     + " -> " + moved_state.dotstring_id \
	     + " [ label=" + move.dotstring + " ]"

def recursivelyPrintDotstringMove(state):
	if state.is_alive and not state.is_victory:
		for move in state.sane_moves:
			moved_state = state.executeMove(move)
			print dotstringMove(state, move, moved_state)
			recursivelyPrintDotstringMove(moved_state)

if __name__ == "__main__":
	me            = Person(name = "Me",            bridge_crossing_time = 1)
	lab_assistant = Person(name = "Lab assistant", bridge_crossing_time = 2)
	janitor       = Person(name = "Janitor",       bridge_crossing_time = 5)
	professor     = Person(name = "Professor",     bridge_crossing_time = 10)

	initial_state = State(people_locations = {START_PLACE_NAME: {me, lab_assistant, janitor, professor},
	                                          END_PLACE_NAME: set()},
	                      lantern_location = START_PLACE_NAME,
	                      time = 0)

	print "digraph \"Bridge Riddle graph\" {"
	recursivelyPrintDotstringMove(initial_state)
	print "}"
