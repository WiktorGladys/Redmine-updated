class Test:
    name = "Tomek"

    def change_name(self):
        self.name = "Wiktor"


s = Test()
print(s.name)
s.change_name()
print(s.name)