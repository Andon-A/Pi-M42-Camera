# This is our settings menu.

class basicMenu:
    def __init__(self):
        # Set ourselves up.
        # Ideally this is a general purpose menu.
        self._menuSelect = 0 # Our default menu, the main menu.
        self._optionSelect = 0 # Our current option.
        self._selectedOptions = [] # Our stored options.
        self._menus = []
        self._menuNames = []
        # self._menus = [["Default",["Default"]]]
    
    def addMenu(self, menu, options):
        menu = str(menu) # We can only work with strings.
        # Our menus must be uniquely named.
        if menu in self._menuNames:
            return False
        # Even if it is only one option, our options must be in an iterable form.
        if type(options) not in (list, tuple):
            return False
        options = list(options)
        self._menus.append([menu, options])
        self._menuNames.append(menu)
        self._selectedOptions.append(0) # Add a value so we can store the selection.
        return True
    
    def addOption(self, menuNum, option):
        if len(self._menus) <= menuNum:
            # Bad index.
            return False
        option = option
        self._menus[menuNum][1].append(option)
        return True
    
    def nextMenu(self):
        # Save our current selection.
        self._selectedOptions[self._menuSelect] = selv._optionSelect
        # Select our next menu
        self._menuSelect += 1
        # Roll over if we have gone too far.
        if self._menuSelect >= len(self._menus):
            self._menuSelect = 0
        # Set our current option to the previously stored item.
        self._optionSelect = self._selectedOptions[self._menuSelect]
        return self._menuSelect
    
    def prevMenu(self):
        # Selects the previous menu item.
        self._menuSelect -= 1
        # Roll over if we have gone too far.
        if self._menuSelect < 0:
            self._menuSelect = len(self._menus) - 1
        return self._menuSelect

    def nextOption(self):
        # Selects the next option.
        max_select = len(self._menus[self._menuSelect][1]) - 1
        self._optionSelect += 1
        # Stop if we go too far.
        if self._optionSelect > max_select:
            self._optionSelect = max_select
        return self._optionSelect
    
    def prevOption(self):
        # Selects the previous option
        self._optionSelect -= 1
        # Stop if we go too far.
        if self._optionSelect < 0:
            self._optionSelect = 0
        return self._optionSelect
    
    def getCurrentSelect(self):
        # Returns the menu and option that we currently have selected.
        menu = self._menus[self._menuSelect][0]
        option = self._menus[self._menuSelect][1][self._optionSelect]
        return (menu, option)
    
    def getAllSaved(self):
        # Returns the menu and options that we have saved for all menus.
        selects = []
        for m in range(0, len(self._menus)):
            menu = self._menus[m][0]
            opt  = self._menus[m][1][self._selectedOptions[m]]
            selects.append((menu, opt))
        return selects
        

# Our "Live" menu, or the one we use while we're shooting.
liveMenu = basicMenu()
liveMenu.addMenu("ISO", ["AUTO", 100, 200, 400, 800, 1600]) # Standard and half steps.
liveMenu.addMenu("Exposure", [ 'AUTO', '1/3200', '1/2500', '1/2000', '1/1600', '1/1250', '1/1000',
                               '1/800', '1/640', '1/500', '1/400', '1/320', '1/250', '1/200',
                               '1/160', '1/125', '1/100', '1/80', '1/60', '1/50', '1/40', '1/30',
                               '1/25', '1/20', '1/15', '1/13', '1/10', '1/8', '1/6', '1/5', '1/4',
                               '0.3"', '0.4"', '0.5"', '0.6"', '0.8"', '1"', '1"3', '1"6', '2"',
                               '2"5', '3"2', '4"', '5"', '6"', '8"', '10"', '13"', '15"', '20"',
                               '25"', '30"']) # Given in seconds. Strings that we parse later.
# liveMenu.addMenu("Mode", ["Still", "Video"])
