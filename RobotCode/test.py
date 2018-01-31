import weakref


class AppComm(object):
    def __init__(self, parent):
        self.robot = weakref.ref(parent)


    def SetObjective(self, objective):
        self.robot().objective = objective
        return



class Controller(object):
    def __init__(self):
        self.appComm = AppComm(self)
        self.objective = ""


c = Controller()
print(c.objective)
c.appComm.SetObjective("new objective")

print(c.objective)
