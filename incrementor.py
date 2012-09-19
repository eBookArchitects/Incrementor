#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
Created on Jul 10, 2012

Generate a sequence of numbers
using a special replace expression
in your regular exression.

@authors: Chris, Toby
@copy: Creative Commons Attribution 2.0 Generic (http://creativecommons.org/licenses/by/2.0/)
@python-ver: Python 3.2
'''


import sublime
import sublime_plugin
import re
from functools import partial
from types import GeneratorType


class IncrementorHighlight(object):
    """
    Highlights regions or regular expression matches.
    """

    def __init__(self, view):
        self.view = view

    def window(self):
        return self.view.window()

    def run(self, matchArg=None, startRegionsArg=None):
        startRegions = startRegionsArg
        match = matchArg
        view = self.view
        if startRegions and match:
            matchRegions = view.find_all(match)

            # Check if regions are in the given selections.
            positiveMatch = list()
            # Create list of non-empty regions.
            nEmptyRegions = [sRegion for sRegion in startRegions if not sRegion.empty()]

            # If there is at least one empty region proceed to check in matches are in region.
            if len(nEmptyRegions) == 0:
                positiveMatch = matchRegions
            else:
                for mRegion in matchRegions:
                    for sRegion in startRegions:
                        if sRegion.contains(mRegion):
                            positiveMatch.append(mRegion)

            view.add_regions("Incrementor", positiveMatch, "comments", "", sublime.DRAW_OUTLINED)
        else:
            view.erase_regions("Incrementor")


class IncrementorCommand(object):
    """
    Highlights regions or regular expression matches.
    """

    def __init__(self, view):
        self.view = view

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

    def run(self, find, replace, startRegionsArg=None):

        def regionSort(thisList):
            for region in thisList:
                currentBegin = region.begin()
                currentEnd = region.end()
                if currentBegin > currentEnd:
                    region = sublime.Region(currentEnd, currentBegin)

            return sorted(thisList, key=lambda region: region.begin())

        startRegions = startRegionsArg
        startRegions = regionSort(startRegions)
        view = self.view
        reFind = re.compile(find)
        myReplace = self.parse_replace(replace)
        try:
            editMe = self.view.begin_edit()
            if startRegions and replace:
                # Check if regions are in the given selections.
                positiveMatch = list()
                # Create list of non-empty regions.
                nEmptyRegions = [sRegion for sRegion in startRegions if not sRegion.empty()]

                # If there is at least one empty region proceed to check in matches are in region.
                if len(nEmptyRegions) == 0:
                    positiveMatch = self.match_gen(find)
                    for match in positiveMatch:
                        myString = view.substr(match)
                        newString = reFind.sub(partial(self.inc_replace, myReplace), myString)
                        view.replace(editMe, match, newString)
                else:
                    adjust = 0
                    for sRegion in startRegions:
                        matchRegions = self.match_gen(find)
                        print "This" , sRegion
                        if adjust:
                            newBeg = sRegion.begin() + adjust
                            newEnd = sRegion.end() + adjust
                            sRegion = sublime.Region(newBeg, newEnd)
                            print "Adjusted" , sRegion
                            print adjust
                            print view.substr(sRegion)
                        for mRegion in matchRegions:
                            if sRegion.contains(mRegion):
                                myString = view.substr(mRegion)
                                newString = reFind.sub(partial(self.inc_replace, myReplace), myString)
                                view.erase(editMe, mRegion)
                                charLen = view.insert(editMe, mRegion.begin(), newString)
                                adjustment = charLen - mRegion.size()
                                adjust = adjust + adjustment
                                newEnd = sRegion.end() + adjustment
                                sRegion = sublime.Region(sRegion.begin(), newEnd)

            else:
                for match in positiveMatch:
                    myString = view.substr(match)
                    newString = reFind.sub(partial(self.inc_replace, myReplace), myString)
                    view.replace(editMe, match, newString)
        finally:
            self.view.end_edit(editMe)

    def make_step(self, start=1, step=1):
        num = start
        while True:
            yield num
            num = num + step

    def inc_replace(self, pattern_list, match):
        replace_string = ''
        for i in range(len(pattern_list)):
            if isinstance(pattern_list[i], GeneratorType):
                replace_string = replace_string + str(pattern_list[i].next())
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
                if len(arg_list) == 2:
                    replace_list[i] = self.make_step(start=arg_list[0], step=arg_list[1])
                else:
                    replace_list[i] = self.make_step(start=arg_list[0])
        return replace_list


class IncrementorPromptCommand(sublime_plugin.WindowCommand):
    """
    Prompts for find and replace strings.
    """

    def view(self):
        return self.window.active_view()

    def run(self):
        self.starterRegions = []
        for sRegion in self.window.active_view().sel():
            region = sublime.Region(sRegion.end(), sRegion.begin())
            self.starterRegions.append(region)
        self.window.active_view().sel().clear()
        self.get_find()

    def find(self, find):
        self.findStr = find
        self.get_replace()

    def highlighter(self, regex=None):
        highlighter = IncrementorHighlight(view=self.view())
        if regex:
            highlighter.run(matchArg=regex, startRegionsArg=self.starterRegions)
        else:
            highlighter.run()

    def get_find(self):
        self.window.show_input_panel("Find:", unicode(), self.find, self.highlighter, self.highlighter)

    def replace(self, replace):
        self.replaceStr = replace
        # Removes highlight.
        self.window.active_view().run_command("gen_rep_highlight")
        # Runs the replace.
        # self.window.active_view().run_command("gen_rep", {"find": self.findStr, "replace": self.replaceStr, "startRegionsArg": self.starterRegions})
        IncrementorIt = IncrementorCommand(view=self.view())
        IncrementorIt.run(find=self.findStr, replace=self.replaceStr, startRegionsArg=self.starterRegions)

    def get_replace(self):
        self.window.show_input_panel("Replace:", unicode(), self.replace, None, self.highlighter)
