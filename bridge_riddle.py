#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import itertools
import collections
from operator import attrgetter

START_PLACE_NAME = "Peak"
END_PLACE_NAME = "Safety"
LIMIT_TIME = 17

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
		return "t = %smin" % self.time

	@property
	def _people_locations_string(self):
		return " | ".join(location + " ("+", ".join([unicode(p) for p in self.people_locations[location]])+")"
		                                             for location in sorted(self.people_locations.iterkeys()))

	def __unicode__(self):
		return self._time_string + ": " + self._people_locations_string

	@property
	def dotstring(self):
		return "\"" + self._time_string + "\\n" + self._people_locations_string + "\""

	@property
	def is_alive(self):
		return self.time <= LIMIT_TIME

	@property
	def criticity(self):
		return self.time / TIME_LIMIT

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

	current_state = initial_state
	for move in current_state.possible_moves:
		moved_state = current_state.executeMove(move)
		print "\t" + initial_state.dotstring + " -> " + moved_state.dotstring + ";"

	print "}"
