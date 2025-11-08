# Feature: Textual TUI Migration for Sticky Prompt Interface

## Feature Description

Migrate agent-template's CLI from scrolling terminal interface to a full TUI (Text User Interface) using the Textual framework. This will enable a "sticky prompt box" at the bottom of the screen with fixed header/footer, similar to Droid and modern chat interfaces.

## User Story

As a developer using agent-template
I want a fixed chat input box at the bottom with a sticky status bar
So that the conversation scrolls above while the input area stays consistent and visible

## Problem Statement

Current implementation uses a scrolling terminal pattern where:
- Status bar and prompt scroll up with each response
- Multiple status bars visible on screen as conversation grows
- Prompt structure changes position constantly
- No visual separation between conversation area and input area

This works but lacks the polished UX of modern TUI chat interfaces like Droid, Copilot, and others that use fixed layout sections.

## Solution Statement

Migrate to Textual framework to implement:
- **Fixed input area** at bottom with sticky header/footer
- **Scrolling conversation area** above
- **Clear visual separation** between zones
- **Consistent layout** regardless of content

## Reference Implementations

### Droid Pattern
```
[Conversation scrolls here]

 Auto (Off) - all actions require approval              Sonnet 4.5
 shift+tab to cycle modes, tab to cycle reasoning
╭─────────────────────────────────────────────────────────────╮
│ >                                                           │
╰─────────────────────────────────────────────────────────────╯
 [⏱ 7s] ? for help                                    GHOSTTY
```

### Copilot Pattern
```
[Conversation scrolls here]

 ~/path [⎇ branch]                           Model
───────────────────────────────────────────────────
>  Enter @ to mention files or / for commands
───────────────────────────────────────────────────
Ctrl+c Exit · Ctrl+r Expand                   93.9%
```


