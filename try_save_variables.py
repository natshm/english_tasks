class Stash:
    seed = 0
    tasks = None
    tasks_types = ['Все доступные']
    wins = dict()
    losses = dict()
    generator = None

    def clean(self):
        self.tasks = None

    def clean_stats(self):
        self.wins.clear()
        self.losses.clear()

    def count_wins(self):
        return len(self.wins.keys())

    def count_losses(self):
        return len(self.losses.keys())


stash = Stash()
