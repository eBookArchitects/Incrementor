#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on Jul 10, 2012

A Sublime Text 2 Plugin that can generate a sequence of numbers
using search and replace.

@copy: [Creative Commons Attribution 2.0 Generic](http://creativecommons.org/licenses/by/2.0/)
@python-ver: Python 2.6
'''


import sublime
import sublime_plugin
import re
from functools import partial
from types import GeneratorType


class State(object):
    last_find_input = ""
    last_replace_input = ""
    starterRegions = []


class IncrementorHighlightHelperCommand(sublime_plugin.TextCommand):
    """
    Highlights regions or regular expression matches.
    """

    def window(self):
        return self.view.window()

    def run(self, edit, regex):
        starterRegions = State.starterRegions
        view = self.view
        print('regex', regex)
        if starterRegions and regex:
            matchRegions = view.find_all(regex)

            # Check if regions are in the given selections.
            positiveMatch = list()
            # Create list of non-empty regions.
            nEmptyRegions = [sRegion for sRegion in starterRegions if not sRegion.empty()]

            # If there is at least one empty region proceed to check in matches are in region.
            if len(nEmptyRegions) == 0:
                positiveMatch = matchRegions
            else:
                for mRegion in matchRegions:
                    for sRegion in starterRegions:
                        if sRegion.contains(mRegion):
                            positiveMatch.append(mRegion)

            view.add_regions("Incrementor", positiveMatch, "comments", "", sublime.DRAW_OUTLINED)
        else:
            view.erase_regions("Incrementor")


class IncrementorInternalHelperCommand(sublime_plugin.TextCommand):
    """
    Highlights regions or regular expression matches.
    """

    def window(self):
        return self.view.window()

    def match_gen(self, regex):
        position = 0
        while True:
            region = self.view.find(regex, position)
            if region:
                yield region
                position = region.end() - 1
            else:
                break

    def run(self, edit, find, replace):
        starterRegions=State.starterRegions

        def regionSort(thisList):
            for region in thisList:
                currentBegin = region.begin()
                currentEnd = region.end()
                if currentBegin > currentEnd:
                    region = sublime.Region(currentEnd, currentBegin)

            return sorted(thisList, key=lambda region: region.begin())

        starterRegions = starterRegions
        starterRegions = regionSort(starterRegions)
        view = self.view
        reFind = re.compile(find)
        myReplace = self.parse_replace(replace)

        if starterRegions and replace:
            # Check if regions are in the given selections.
            # Create list of non-empty regions.
            nEmptyRegions = [sRegion for sRegion in starterRegions if not sRegion.empty()]

            # If there is at least one empty region proceed to check in matches are in region.
            if len(nEmptyRegions) == 0:
                positiveMatch = self.match_gen(find)
                for match in positiveMatch:
                    myString = view.substr(match)
                    newString = reFind.sub(partial(self.inc_replace, myReplace), myString)
                    view.replace(edit, match, newString)
            else:
                adjust = 0
                for sRegion in starterRegions:
                    matchRegions = self.match_gen(find)
                    # print( "This" , sRegion )
                    if adjust:
                        newBeg = sRegion.begin() + adjust
                        newEnd = sRegion.end() + adjust
                        sRegion = sublime.Region(newBeg, newEnd)
                        # print( "Adjusted" , sRegion )
                        # print( adjust )
                        # print( view.substr(sRegion) )
                    for mRegion in matchRegions:
                        if sRegion.contains(mRegion):
                            myString = view.substr(mRegion)
                            newString = reFind.sub(partial(self.inc_replace, myReplace), myString)
                            view.erase(edit, mRegion)
                            charLen = view.insert(edit, mRegion.begin(), newString)
                            adjustment = charLen - mRegion.size()
                            adjust = adjust + adjustment
                            newEnd = sRegion.end() + adjustment
                            sRegion = sublime.Region(sRegion.begin(), newEnd)

        else:
            positiveMatch = self.match_gen(find)
            for match in positiveMatch:
                myString = view.substr(match)
                newString = reFind.sub(partial(self.inc_replace, myReplace), myString)
                view.replace(edit, match, newString)

    def make_step(self, start=1, step=1, repeat_after=None):
        # optional repeat_after argument specifies the limit of the incrementation.
        # after the limit is reached, return to the start value and resume incrementing
        num = start
        while True:
            yield num
            num = num + step
            if repeat_after:# return to start value if we're past repeat_after
                if step < 0:
                    if num < repeat_after:
                        num = start
                else:
                    if num > repeat_after:
                        num = start

    def inc_replace(self, pattern_list, match):
        replace_string = ''
        for i in range(len(pattern_list)):
            if isinstance(pattern_list[i], GeneratorType):
                replace_string = replace_string + str(next(pattern_list[i]))
            else:
                replace_string = replace_string + match.expand(pattern_list[i])
        return replace_string

    def parse_replace(self, replace):
        replace_list = re.split(r"(\\i\(.+?\)|\\i)", replace)
        replace_list[:] = [item for item in replace_list if item != '']
        for i in range(len(replace_list)):
            if replace_list[i] == "\\i":
                replace_list[i] = self.make_step()
            elif re.match(r"^\\i\(.+?\)$", replace_list[i]):
                arg_list = [int(num) for num in re.split(r'\\i|\(|,| |\)', replace_list[i]) if num != '']
                if len(arg_list) == 3:
                    replace_list[i] = self.make_step(start=arg_list[0], step=arg_list[1], repeat_after=arg_list[2])
                elif len(arg_list) == 2:
                    replace_list[i] = self.make_step(start=arg_list[0], step=arg_list[1])
                else:
                    replace_list[i] = self.make_step(start=arg_list[0])
        return replace_list


class IncrementorPromptCommand(sublime_plugin.TextCommand):
    """
    Prompts for find and replace strings.
    """

    def run(self, edit):
        self.window = self.view.window() or sublime.active_window()
        State.starterRegions = []

        for sRegion in self.window.active_view().sel():
            region = sublime.Region(sRegion.end(), sRegion.begin())
            State.starterRegions.append(region)
        self.get_find()

    def find(self, find):
        self.findStr = find
        State.last_input = find
        self.get_replace()

    def highlighter(self, regex=None):
        self.window.run_command( "incrementor_highlight_helper", { 'regex': regex } )

    def get_find(self):
        self.window.show_input_panel("Find:", State.last_find_input, self.find, self.highlighter, self.highlighter)

    def replace(self, replace):
        self.replaceStr = replace

        # Removes highlight.
        self.view.erase_regions("Incrementor")

        # Runs the replace.
        arguments = { 'find': self.findStr, 'replace': self.replaceStr }
        self.window.run_command( "incrementor_internal_helper", arguments )

    def get_replace(self):
        self.window.show_input_panel("Replace:", State.last_replace_input, self.replace, None, self.highlighter)
