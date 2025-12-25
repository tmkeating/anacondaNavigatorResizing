# Anaconda Navigator Resizing Patches

This repository contains patched files for Anaconda Navigator to resolve issues with window sizing and scaling on high-DPI displays (or just stubborn window managers).

## Changes Made

1.  **`app/main.py`**: 
    - Forces `QT_SCALE_FACTOR` to `0.75` (unless overridden).
    - Disables `QT_AUTO_SCREEN_SCALE_FACTOR`.
    - Sets `QT_API` to `pyside6`.

2.  **`widgets/main_window/__init__.py`**:
    - Reduced minimum window width from 1200px to 400px.
    - Reduced initial window size to 800x600.
    - Disabled saving/restoring window geometry to prevent "stuck" large windows.

3.  **`widgets/tabs/home.py`**:
    - Removed minimum width constraint on the environment selector combobox.

4.  **`widgets/tabs/tabwidget.py`**:
    - Removed code that forced all sidebar buttons to be the same width as the widest one.

5.  **`widgets/dialogs/preferences.py`**:
    - Reduced minimum size constraints for the Preferences dialog and its internal text editor.

6.  **`utils/styles.py`**:
    - Implemented global pixel scaling (0.75x) for all SASS variables.
    - Implemented global font scaling (0.75x) for all CSS font definitions.
    - Reduced icon sizes from 32px to 24px.

## Installation

To apply these patches, replace the corresponding files in your Anaconda Navigator installation directory (typically `~/anaconda3/lib/pythonX.X/site-packages/anaconda_navigator/`).
