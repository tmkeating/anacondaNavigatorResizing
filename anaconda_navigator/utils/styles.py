# -*- coding: utf-8 -*-

# pylint: disable=invalid-name

# -----------------------------------------------------------------------------
# Copyright (c) 2016-2017 Anaconda, Inc.
#
# May be copied and distributed freely only as part of an Anaconda or
# Miniconda installation.
# -----------------------------------------------------------------------------

"""Styles for the application."""

from __future__ import annotations

import ast
import contextlib
import enum
import os
import re
import string
import typing
from pathlib import Path

from qtpy.QtCore import QSize  # pylint: disable=no-name-in-module
from qtpy.QtGui import QColor, QIcon

from anaconda_navigator.config import CONF
from anaconda_navigator.static import images
from anaconda_navigator.static.css import DATA_PATH
from anaconda_navigator.static.css import GLOBAL_SASS_STYLES_PATH

BLUR_SIZE = 10


class ColorMode(str, enum.Enum):
    """Color mode options."""

    light = 'light'
    dark = 'dark'

    @classmethod
    def current(cls) -> ColorMode:
        """Return current color mode."""
        return cls.dark if CONF.get('main', 'dark_mode', False) else cls.light

    @classmethod
    def get_image_path(cls) -> Path:
        """Return image path corresponding to current color mode."""
        return Path(images.__file__).resolve().parent / cls.current().value


class SassVariables:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Enum to hold SASS defined variables."""

    def __init__(self) -> None:
        """Enum to hold SASS defined variables."""
        self.SHADOW_BLUR_RADIUS = 7  # Used for dialogs
        self.WIDGET_APPLICATION_TOTAL_WIDTH = 200
        self.WIDGET_APPLICATION_TOTAL_HEIGHT = 220
        self.WIDGET_CONTENT_PADDING = 5
        self.WIDGET_CONTENT_TOTAL_HEIGHT = 150
        self.WIDGET_CONTENT_TOTAL_WIDTH = 150
        self.WIDGET_CONTENT_PADDING = 5
        self.WIDGET_CONTENT_MARGIN = 5
        self.WIDGET_ENVIRONMENT_TOTAL_HEIGHT = 40
        self.WIDGET_IMPORT_ENVIRONMENT_TOTAL_HEIGHT = 45
        self.WIDGET_ENVIRONMENT_TOTAL_WIDTH = 25
        self.WIDGET_APPLICATION_TOTAL_WIDTH = 200
        self.WIDGET_APPLICATION_TOTAL_HEIGHT = 220
        self.WIDGET_CHANNEL_DIALOG_WIDTH = 300
        self.WIDGET_CHANNEL_TOTAL_WIDTH = 225
        self.WIDGET_CHANNEL_TOTAL_HEIGHT = 45
        self.WIDGET_CHANNEL_PADDING = 5
        self.WIDGET_RUNNING_APPS_WIDTH = 350
        self.WIDGET_RUNNING_APPS_TOTAL_WIDTH = 260
        self.WIDGET_RUNNING_APPS_TOTAL_HEIGHT = 40
        self.WIDGET_RUNNING_APPS_PADDING = 8
        self.WIDGET_LOGIN_CARD_TOTAL_WIDTH = 240
        self.WIDGET_LOGIN_CARD_TOTAL_HEIGHT = 150

        self.ICON_ACTION_NOT_INSTALLED = os.path.join(images.IMAGE_PATH, 'icons', 'check-box-blank.svg')
        self.ICON_ACTION_INSTALLED = os.path.join(images.IMAGE_PATH, 'icons', 'check-box-checked-active.svg')
        self.ICON_ACTION_REMOVE = os.path.join(images.IMAGE_PATH, 'icons', 'mark-remove.svg')
        self.ICON_ACTION_ADD = os.path.join(images.IMAGE_PATH, 'icons', 'mark-install.svg')
        self.ICON_ACTION_UPGRADE = os.path.join(images.IMAGE_PATH, 'icons', 'mark-upgrade.svg')
        self.ICON_ACTION_DOWNGRADE = os.path.join(images.IMAGE_PATH, 'icons', 'mark-downgrade.svg')
        self.ICON_UPGRADE_ARROW = os.path.join(images.IMAGE_PATH, 'icons', 'update-app-active.svg')
        self.ICON_SPACER = os.path.join(images.IMAGE_PATH, 'conda-manager-spacer.svg')
        self.ICON_PYTHON = os.path.join(images.IMAGE_PATH, 'python-logo.svg')
        self.ICON_ANACONDA = os.path.join(images.IMAGE_PATH, 'anaconda-logo.svg')

        self.COLOR_FOREGROUND_NOT_INSTALLED = '#666'
        self.COLOR_FOREGROUND_UPGRADE = '#00A3E0'
        self.SIZE_ICONS = (24, 24)

    def process_palette(self) -> dict[str, QIcon | QColor | QSize]:
        """Turn the styles _palette into QIcons or QColors for use in the model."""
        palette: dict[str, QIcon | QColor | QSize] = {}

        for key in dir(self):
            item: QIcon | QColor | QSize | None = None

            if key.startswith('ICON_'):
                item = QIcon(getattr(self, key))
            elif key.startswith('COLOR_'):
                item = QColor(getattr(self, key))
            elif key.startswith('SIZE_'):
                item = QSize(*getattr(self, key))

            if item:
                palette[key] = item

        return palette

    def __repr__(self):
        """Return a pretty formatted representation of the enum."""
        keys = []
        representation = 'SASS variables enum: \n'
        for key in self.__dict__:
            if key[0] in string.ascii_uppercase:
                keys.append(key)

        for key in sorted(keys):
            representation += f'    {key} = {self.__dict__[key]}\n'
        return representation


SASS_VARIABLES = SassVariables()


def load_sass_variables(*, path: str | None = None, theme: str | None = None) -> SassVariables:
    """Parse Sass file styles and get custom values for used in code."""
    global SASS_VARIABLES  # pylint: disable=global-statement
    SASS_VARIABLES = SassVariables()

    if path:
        with open(path, 'rt', encoding='utf-8') as f:
            data = f.read()
    elif theme:
        data = read_files(lambda filename: filename == f'{theme}.scss')
    else:
        return SASS_VARIABLES

    pattern = re.compile(r'[$]\S*:.*?;')
    variables = re.findall(pattern, data)
    for var in variables:
        name, value = var[1:-1].split(':')
        if name[0] in string.ascii_uppercase:
            value = value.strip()
            with contextlib.suppress(BaseException):
                value = ast.literal_eval(value)
            setattr(SASS_VARIABLES, name, value)
    return SASS_VARIABLES


def read_files(match: typing.Callable[[str], bool]) -> str:
    """Recursively walk, find all matched files, and merge their contents into a single string."""
    matched_path = []
    merged_contents = []

    for root, _, files in os.walk(DATA_PATH):
        for filename in files:
            if match(filename):
                matched_path.append(os.path.join(root, filename))

    matched_path.sort()

    for path in matched_path:
        with open(path, 'r', encoding='utf-8') as f:
            merged_contents.append(f.read())

    return '\n'.join(merged_contents)


def load_style_sheet() -> str:
    """Load css styles file and parse to include custom variables."""
    load_sass_variables(path=GLOBAL_SASS_STYLES_PATH)

    theme = ColorMode.current().value
    data = read_files(lambda filename: filename == f'{theme}.css')

    load_sass_variables(theme=theme)

    styled_images: Path = ColorMode.get_image_path()
    styled_icons: Path = styled_images / 'icons'

    data = data.replace(
        '$IMAGE_PATH', Path(images.IMAGE_PATH).as_posix()
    ).replace(
        '$STYLED_IMAGE_PATH', styled_images.as_posix()
    ).replace(
        '$STYLED_ICONS_PATH', styled_icons.as_posix()
    )

    # Global scaling for all pixel values
    def scale_pixels(match):
        value = int(match.group(1))
        # Don't scale 0 or 1 px to 0 (unless it was 0)
        if value <= 1:
            return f'{value}px'
        new_value = int(value * 0.75)
        return f'{new_value}px'

    data = re.sub(r'(\d+)px', scale_pixels, data)

    return data
