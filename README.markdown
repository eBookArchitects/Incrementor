# Sublime Text 2 Plugin: The Incrementor

A Sublime Text 2 Plugin that can generate a sequence of numbers using search and replace.

There is a Sublime Text 3 port available [here](https://github.com/born2c0de/Incrementor).

Example (Before):

    10. Bob
    12. Larse
    15. Billy

> Find: `[0-9]+\.`
> Replace: `\i\.`

Example (After):

    1. Bob
    2. Larse
    3. Billy

You can also take start and step arguments `\i(start,step)` in parenthesis.

Example (Before):

    10. Bob
    12. Larse
    15. Billy

> Find: `[0-9]+\.`
> Replace: `\i(10,10)\.`

Example (After):

    10. Bob
    20. Larse
    30. Billy

Lastly, The Incrementor also supports negative steps! `\i(start,-step)`

Example (Before):

    10. Bob
    12. Larse
    15. Billy

> Find: `[0-9]+\.`
> Replace: `\i(100,-10)\.`

Example (After):

    100. Bob
    90. Larse
    80. Billy

## Using

Use the keybinding to prompt for your find and replace.

Windows: [Ctrl + G, Ctrl + R]
Mac OSX: [Super + G, Super + R]
Linux: [Ctrl + G, Ctrl + R]

## Installing

Use Github [here](https://github.com/eBookArchitects/Incrementor.git) or [Sublime Package Control](http://wbond.net/sublime_packages/package_control)

### Linux:

    Copy the directory to: "~/.config/sublime-text-2/Packages"

### Windows 7:

    Copy the directory to: "C:\Users\<username>\AppData\Roaming\Sublime Text 2\Packages"

### Windows XP:

    Copy the directory to: "C:\Documents and Settings\<username>\Application Data\Sublime Text 2\Packages"

## Todo

- Replace based on order of selection as well as their direction. (Difficult)
- Scroll to matching pattern like sublime's default find window. (Easy)
- Allow prepending 0s to the initial number. (001, 002, 003, 004, etc.) (Intermediate)
- Add number of replaced items in statusbar after completion. (Intermediate)

## Contributors

Don't forget to add yourself!

[eBook Architects](info@ebookarchitects.com), [Chris](cdcasey@gmail.com), [Toby](codenamekt@gmail.com), [AJ](anthony@ebookarchitects.com)

## License

[Creative Commons Attribution 2.0 Generic](http://creativecommons.org/licenses/by/2.0/)
