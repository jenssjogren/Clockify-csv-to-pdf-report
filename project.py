class Project:
    def __init__(self, name):
        self.name = name
        self.total_time = 0.0
        self.tasks = {}

    def set_name(self, name):
        self.name = name

    def add_time(self, task, time):
        try:
            self.tasks[task] += float(time)
        except KeyError:
            self.tasks[task] = float(time)

        self.total_time += time

    def get_name(self):
        return self.name

    def get_total_time(self):
        return self.total_time

    def get_tasks(self):
        return self.tasks
