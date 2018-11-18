
from functools import partial
from PySide2 import QtWidgets, QtCore

from hotbox_designer import templates
from hotbox_designer.interactive import Shape
from hotbox_designer.geometry import get_combined_rects
from hotbox_designer.qtutils import set_shortcut
from hotbox_designer.data import copy_hotbox_data
from hotbox_designer.arrayutils import (
    move_elements_to_array_end, move_elements_to_array_begin,
    move_up_array_elements, move_down_array_elements)

from .editarea import ShapeEditArea
from .menu import MenuWidget
from .attributes import AttributeEditor


class HotboxEditor(QtWidgets.QWidget):
    hotboxDataModified = QtCore.Signal(object)

    def __init__(self, hotbox_data, software, parent=None):
        super(HotboxEditor, self).__init__(parent, QtCore.Qt.Window)
        self.setWindowTitle("Hotbox editor")
        self.options = hotbox_data['general']
        self.software = software
        self.clipboard = []
        self.undo_manager = UndoManager(hotbox_data)

        self.shape_editor = ShapeEditArea(self.options)
        self.shape_editor.selectedShapesChanged.connect(self.selection_changed)
        self.shape_editor.centerMoved.connect(self.move_center)
        method = self.set_data_modified
        self.shape_editor.increaseUndoStackRequested.connect(method)

        self.menu = MenuWidget()
        self.menu.copyRequested.connect(self.copy)
        self.menu.pasteRequested.connect(self.paste)
        self.menu.deleteRequested.connect(self.delete_selection)
        self.menu.sizeChanged.connect(self.editor_size_changed)
        self.menu.editCenterToggled.connect(self.edit_center_mode_changed)
        self.menu.useSnapToggled.connect(self.use_snap)
        self.menu.snapValuesChanged.connect(self.snap_value_changed)
        self.menu.centerValuesChanged.connect(self.move_center)
        width, height = self.options['width'], self.options['height']
        self.menu.set_size_values(width, height)
        x, y = self.options['centerx'], self.options['centery']
        self.menu.set_center_values(x, y)
        self.menu.undoRequested.connect(self.undo)
        self.menu.redoRequested.connect(self.redo)
        method = partial(self.create_shape, templates.SQUARE_BUTTON)
        self.menu.addButtonRequested.connect(method)
        method = partial(self.create_shape, templates.TEXT)
        self.menu.addTextRequested.connect(method)
        method = partial(self.create_shape, templates.BACKGROUND, before=True)
        self.menu.addBackgroundRequested.connect(method)
        method = self.set_selection_move_down
        self.menu.moveDownRequested.connect(method)
        method = self.set_selection_move_up
        self.menu.moveUpRequested.connect(method)
        method = self.set_selection_on_top
        self.menu.onTopRequested.connect(method)
        method = self.set_selection_on_bottom
        self.menu.onBottomRequested.connect(method)

        set_shortcut("Ctrl+Z", self.shape_editor, self.undo)
        set_shortcut("Ctrl+Y", self.shape_editor, self.redo)
        set_shortcut("Ctrl+C", self.shape_editor, self.copy)
        set_shortcut("Ctrl+V", self.shape_editor, self.paste)
        set_shortcut("del", self.shape_editor, self.delete_selection)
        set_shortcut("Ctrl+D", self.shape_editor, self.deselect_all)

        self.attribute_editor = AttributeEditor(self.software)
        self.attribute_editor.optionSet.connect(self.option_set)
        self.attribute_editor.rectModified.connect(self.rect_modified)
        self.attribute_editor.imageModified.connect(self.image_modified)

        self.hlayout = QtWidgets.QHBoxLayout()
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.addStretch(1)
        self.hlayout.addWidget(self.shape_editor)
        self.hlayout.addStretch(1)
        self.hlayout.addWidget(self.attribute_editor)

        self.vlayout = QtWidgets.QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.vlayout.setSpacing(0)
        self.vlayout.addWidget(self.menu)
        self.vlayout.addLayout(self.hlayout)

    def copy(self):
        self.clipboard = [
            s.options.copy() for s in self.shape_editor.selection]

    def paste(self):
        clipboad_copy = [s.copy() for s in self.clipboard]
        shape_datas = self.hotbox_data()['shapes'][:] + clipboad_copy
        hotbox_data = {
            'general': self.options,
            'shapes': shape_datas}
        self.set_hotbox_data(hotbox_data)
        self.undo_manager.set_data_modified(hotbox_data)
        self.hotboxDataModified.emit(hotbox_data)
        # select new shapes
        shapes = self.shape_editor.shapes [-len(self.clipboard):]
        self.shape_editor.selection.replace(shapes)
        self.shape_editor.update_selection()
        self.shape_editor.repaint()

    def undo(self):
        result = self.undo_manager.undo()
        if result is False:
            return
        data = self.undo_manager.data
        self.set_hotbox_data(data)
        self.hotboxDataModified.emit(self.hotbox_data())

    def redo(self):
        self.undo_manager.redo()
        data = self.undo_manager.data
        self.set_hotbox_data(data)
        self.hotboxDataModified.emit(self.hotbox_data())

    def deselect_all(self):
        self.shape_editor.selection.clear()
        self.shape_editor.update_selection()
        self.shape_editor.repaint()

    def set_data_modified(self):
        self.undo_manager.set_data_modified(self.hotbox_data())
        self.hotboxDataModified.emit(self.hotbox_data())

    def use_snap(self, state):
        snap = self.menu.snap_values() if state else None
        self.shape_editor.transform.snap = snap
        self.shape_editor.repaint()

    def snap_value_changed(self):
        self.shape_editor.transform.snap = self.menu.snap_values()
        self.set_data_modified()
        self.shape_editor.repaint()

    def edit_center_mode_changed(self, state):
        self.shape_editor.edit_center_mode = state
        self.shape_editor.repaint()

    def option_set(self, option, value):
        for shape in self.shape_editor.selection:
            shape.options[option] = value
        self.shape_editor.repaint()
        self.set_data_modified()

    def editor_size_changed(self):
        size = self.menu.get_size()
        self.shape_editor.setFixedSize(size)
        self.options['width'] = size.width()
        self.options['height'] = size.height()
        self.set_data_modified()

    def move_center(self, x, y):
        self.options['centerx'] = x
        self.options['centery'] = y
        self.menu.set_center_values(x, y)
        self.shape_editor.repaint()
        self.set_data_modified()

    def rect_modified(self, option, value):
        shapes = self.shape_editor.selection
        for shape in shapes:
            shape.options[option] = value
            if option == 'shape.height':
                shape.rect.setHeight(value)
                continue
            elif option == 'shape.width':
                shape.rect.setWidth(value)
                continue

            width = shape.rect.width()
            height = shape.rect.height()
            if option == 'shape.left':
                shape.rect.setLeft(value)
            else:
                shape.rect.setTop(value)
            shape.rect.setWidth(width)
            shape.rect.setHeight(height)

        rects = [shape.rect for shape in self.shape_editor.selection]
        rect = get_combined_rects(rects)
        self.shape_editor.manipulator.set_rect(rect)
        self.shape_editor.repaint()

    def selection_changed(self):
        shapes = self.shape_editor.selection
        options = [shape.options for shape in shapes]
        self.attribute_editor.set_options(options)

    def create_shape(self, template, before=False):
        options = template.copy()
        shape = Shape(options)
        shape.rect.moveCenter(self.shape_editor.rect().center())
        shape.synchronize_rect()
        if before is True:
            self.shape_editor.shapes.insert(0, shape)
        else:
            self.shape_editor.shapes.append(shape)
        self.shape_editor.repaint()
        self.set_data_modified()

    def image_modified(self):
        for shape in self.shape_editor.selection:
            shape.synchronize_image()
        self.shape_editor.repaint()

    def set_selection_move_down(self):
        array = self.shape_editor.shapes
        elements = self.shape_editor.selection
        move_down_array_elements(array, elements)
        self.shape_editor.repaint()
        self.set_data_modified()

    def set_selection_move_up(self):
        array = self.shape_editor.shapes
        elements = self.shape_editor.selection
        move_up_array_elements(array, elements)
        self.shape_editor.repaint()
        self.set_data_modified()

    def set_selection_on_top(self):
        array = self.shape_editor.shapes
        elements = self.shape_editor.selection
        self.shape_editor.shapes = move_elements_to_array_end(array, elements)
        self.shape_editor.repaint()
        self.set_data_modified()

    def set_selection_on_bottom(self):
        array = self.shape_editor.shapes
        elements = self.shape_editor.selection
        shapes = move_elements_to_array_begin(array, elements)
        self.shape_editor.shapes = shapes
        self.shape_editor.repaint()
        self.set_data_modified()

    def delete_selection(self):
        for shape in reversed(self.shape_editor.selection.shapes):
            self.shape_editor.shapes.remove(shape)
            self.shape_editor.selection.remove(shape)
        rects = [shape.rect for shape in self.shape_editor.selection]
        rect = get_combined_rects(rects)
        self.shape_editor.manipulator.set_rect(rect)
        self.shape_editor.repaint()
        self.set_data_modified()

    def hotbox_data(self):
        return {
            'general': self.options,
            'shapes': [shape.options for shape in self.shape_editor.shapes]}

    def set_hotbox_data(self, hotbox_data, reset_stacks=False):
        self.options = hotbox_data['general']
        self.shape_editor.options = self.options
        shapes = [Shape(options) for options in hotbox_data['shapes']]
        self.shape_editor.shapes = shapes
        self.shape_editor.manipulator.rect = None
        self.shape_editor.repaint()
        if reset_stacks is True:
            self.undo_manager.reset_stacks()


class UndoManager():
    def __init__(self, data):
        self._current_state = data
        self._modified = False
        self._undo_stack = []
        self._redo_stack = []

    @property
    def data(self):
        return copy_hotbox_data(self._current_state)

    def undo(self):
        if not self._undo_stack:
            print ('no undostack')
            return False
        self._redo_stack.append(copy_hotbox_data(self._current_state))
        self._current_state = copy_hotbox_data(self._undo_stack[-1])
        del self._undo_stack[-1]
        return True

    def redo(self):
        if not self._redo_stack:
            return False

        self._undo_stack.append(copy_hotbox_data(self._current_state))
        self._current_state = copy_hotbox_data(self._redo_stack[-1])
        del self._redo_stack[-1]
        return True

    def set_data_modified(self, data):
        self._redo_stack = []
        self._undo_stack.append(copy_hotbox_data(self._current_state))
        self._current_state = copy_hotbox_data(data)
        self._modified = True

    def set_data_saved(self):
        self._modified = False

    @property
    def data_saved(self):
        return not self._modified

    def reset_stacks(self):
        self._undo_stack = []
        self._redo_stack = []
