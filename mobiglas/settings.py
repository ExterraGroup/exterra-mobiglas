class GuildConfig:
    def __init__(self, data):
        self._data = data
        self.prefix = self.settings['prefix']
        self.offset = self.settings['offset']
        self.has_configured = self.settings['done']

    @property
    def settings(self):
        return self._data['prefix']


class RaidData:
    def __init__(self, data):
        self._data = data


class MotionData:
    def __init__(self, data):
        self._data = data


class CitizenData:
    def __init__(self, bot, data):
        self._bot = bot
        self._data = data
        self.raid_reports = data.get('raid_reports')


class GuildData:
    def __init__(self, ctx, data):
        self.ctx = ctx
        self._data = data

    @property
    def config(self):
        return GuildConfig(self._data['configure_dict'])

    @property
    def raids(self):
        return self._data['raidchannel_dict']

    def raid(self, channel_id=None):
        channel_id = channel_id or self.ctx.channel.id
        data = self.raids.get(channel_id)
        return RaidData(data) if data else None

    @property
    def motions(self):
        return self._data['motionchannel_dict']

    def motion(self, channel_id=None):
        channel_id = channel_id or self.ctx.channel.id
        data = self.motions.get(channel_id)
        return MotionData(data) if data else None

    @property
    def citizens(self):
        return self._data['citizen']

    def citizen(self, member_id=None):
        member_id = member_id or self.ctx.author.id
        citizen_data = self.citizen.get(member_id)
        if not citizen_data:
            return None
        return CitizenData(self.ctx.bot, citizen_data)
