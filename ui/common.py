"""
Common collection of methods that can be applied to style the UI in a user-friendly way.
"""

from PyQt5.QtGui import QCursor
from PyQt5.QtCore import Qt

# Given a widget, make the cursor look like a hand over it.
#   Same as CSS's cursor:pointer, should be used for clickable things.
def cursorPointer(widget):
  widget.setCursor(QCursor(Qt.PointingHandCursor))
