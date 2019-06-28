from mobiglas import default


class Operation:

    def __init__(self, ctx, name):
        config = default.get('data/raid_info.json')
        defaults = config.operation_defaults
        self._config = config
        self._name = name
        self._owner = ctx.author
        self._author = ctx.author
        self._min_commanders = defaults.min_commanders
        self._max_commanders = defaults.max_commanders
        self._min_players = defaults.min_players
        self._max_players = defaults.max_players
        self._comms = defaults.comms
        self._details = defaults.details
        self._link = defaults.link
        self._date = defaults.date
        self._commander_assignment = defaults.commander_assignment

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = value
