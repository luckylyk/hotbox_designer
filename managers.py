class Selection():
    def __init__(self):
        self.shapes = []
        self.mode = 'replace'

    def set(self, shapes):
        if self.mode == 'add':
            if shapes is None:
                return
            return self.add(shapes)
        elif self.mode == 'replace':
            if shapes is None:
                return self.clear()
            return self.replace(shapes)
        elif self.mode == 'invert':
            if shapes is None:
                return
            return self.invert(shapes)
        elif self.mode == 'remove':
            if shapes is None:
                return
            for shape in shapes:
                if shape in self.shapes:
                    self.remove(shape)

    def replace(self, shapes):
        self.shapes = shapes
        if not self.shapes:
            return None

    def add(self, shapes):
        self.shapes.extend(shapes)

    def remove(self, shape):
        self.shapes.remove(shape)

    def invert(self, shapes):
        for shape in shapes:
            if shape not in self.shapes:
                self.add([shape])
            else:
                self.remove(shape)

    def clear(self):
        self.shapes = []

    def __iter__(self):
        return self.shapes.__iter__()


def get_selection_mode(ctrl, shift):
    if not ctrl and not shift:
        return 'replace'
    elif ctrl and shift:
        return 'invert'
    elif ctrl and not shift:
        return 'add'
    elif not ctrl and shift:
        return 'remove'


class CopyManager():

    def __init__(self, array, selection_checker):
        self._array = array
        self._selection_checker = selection_checker
        self._index = None
        self._clipboard = []

    def set_array(self, array):
        self._array = array

    def set_index(self, index):
        self._index = index

    def cut(self):
        self.copy()
        return [
            e if self._selection_checker(i) is False else None
            for i, e in enumerate(self._array)]

    def copy(self):
        self._clipboard = [
            (i, e) for i, e in enumerate(self._array)
            if self._selection_checker(i)]

    def paste(self):
        if not self._clipboard:
            return

        offset = self._clipboard[-1][0] - self._clipboard[0][0]
        array = [False for _ in range(offset + 1)]
        for i, e in self._clipboard:
            array[i - self._clipboard[0][0]] = e

        insert_index = self._index or len(self._array)
        for elt in array:
            if elt is False:
                if insert_index > len(self._array) - 1:
                    self._array.append(None)
                insert_index += 1
                continue
            if insert_index < len(self._array) - 1:
                self._array[insert_index] = elt
            else:
                self._array.append(elt)
            insert_index += 1
        self._index = insert_index

        return self._array[:]


class UndoManager():
    def __init__(self, data, copier):
        self._copier = copier
        self._current_state = data
        self._modified = False
        self._undo_stack = []
        self._redo_stack = []

    @property
    def data(self):
        return self._copier(self._current_state)

    def undo(self):
        if not self._undo_stack:
            return
        self._redo_stack.append(self._copier(self._current_state))
        self._current_state = self._copier(self._undo_stack[-1])
        del self._undo_stack[-1]

    def redo(self):
        if not self._redo_stack:
            return

        self._undo_stack.append(self._copier(self._current_state))
        self._current_state = self._copier(self._redo_stack[-1])
        del self._redo_stack[-1]

    def set_data_modified(self, data):
        self._redo_stack = []
        self._undo_stack.append(self._copier(self._current_state))
        self._current_state = self._copier(data)
        self._modified = True
        print('MODIFIED', len(self._undo_stack))
        print( self._current_state)

    def set_data_saved(self):
        self._modified = False

    @property
    def data_saved(self):
        return not self._modified


def copy_hotbox_data(data):
    copied = {}
    copied['general'] = data['general'].copy()
    copied['shapes'] = [shape.copy() for shape in data['shapes']]
    return copied
