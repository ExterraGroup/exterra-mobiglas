from mobiglas.utils import add_guild_role, remove_guild_role, santinize_roles, format_logs, colour, \
    permissions, clean


async def clear_roles(ctx, guild_member):
    """Clear all role(s) from a discord Member
    :param ctx: Session Context
    :param guild_member: discord.Member
    :return: String[] of logs
    """
    unverified_roles = []
    for member_role in guild_member.roles:
        unverified_roles.append(member_role.name)
    await remove_guild_role(ctx, guild_member, unverified_roles, reason='Removing unvalidated permissions')

    logger = format_logs(santinize_roles(unverified_roles), prepend='Removing role: ')

    return logger


async def sort_roles(ctx, user_datum, guild_member):
    """Add and remove role(s) from a discord Member based on a source of truth
    :param ctx: Session Context
    :param user_datum: user data from the site
    :param guild_member: discord.Member
    :return: String[] of logs
    """
    logger = []
    rank = user_datum['rank']
    roles = user_datum['roles']

    verified_roles = [rank['name']]
    for role in roles:
        for config in role['discordRoleConfigs']:
            verified_roles.append(config['name'])
    for cert in user_datum['certifications']:
        if cert['passed']:
            verified_roles.append(cert['certification']['title'])

    unverified_roles = []
    for member_role in guild_member.roles:
        unverified_roles.append(member_role.name)

    add_roles = list(set(verified_roles) - set(unverified_roles))
    remove_roles = list(set(unverified_roles) - set(verified_roles))

    await add_guild_role(ctx, guild_member, add_roles, reason='Adding missing permissions')
    await remove_guild_role(ctx, guild_member, remove_roles, reason='Removing unvalidated permissions')

    # logs
    logger.extend(format_logs(add_roles, prepend='Adding role: '))
    logger.extend(format_logs(santinize_roles(remove_roles), prepend='Removing role: '))

    return logger


async def create_guild_role(ctx, *role_datum):
    """Create roles in discord based on a source of truth
    :param ctx: Session Context
    :param role_datum: role data from the site
    :return: String[] of logs
    """
    logger = []
    reason = 'Creating Role'

    existing_roles = []
    for role in ctx.guild.roles:
        existing_roles.append(role.name)

    for datums in role_datum:
        for datum in datums:
            config = datum['discordRoleConfigs'][0]
            role_name = config['name']

            if role_name in existing_roles:
                continue

            await ctx.guild.create_role(name=role_name,
                                        permissions=permissions(config['permissions']),
                                        colour=colour(int(config['color'].replace('#', '0x'), 0)),
                                        hoist=config['hoist'],
                                        mentionable=config['mentionable'],
                                        reason=reason)
            logger.append(f"{reason}: {role_name}")

    return logger


async def align_nickname(user_datum, guild_member):
    """Modifies user nickname to rsi handle
    :param user_datum: user data from the site
    :param guild_member: discord.Member
    :return: String[] of logs
    """
    logger = []

    handle = user_datum['handle']
    current_nick = guild_member.nick
    current_name = guild_member.name

    # do nothing if username = handle = current_nick
    if handle == current_name and current_nick is None:
        return logger

    if handle != current_nick:
        reason = f"Changing username=[{current_name}], nickname=[{current_nick}] to __verified__ rsi handle [{handle}]"
        await guild_member.edit(nick=handle, reason=reason)
        logger.append(reason)
    return logger


def get_rank(user_datum):
    """Returns the name of rank
    rank {
        name
    }
    :param user_datum: user data from site
    :return: str
    """
    rank_datum = user_datum['rank']
    if rank_datum is None:
        return None

    return rank_datum['name']


def get_roles(user_datum):
    """Returns a list of roles
    roles [
        {
            title
        }
    ]
    :param user_datum: user data from site
    :return: str
    """
    roles_datum = user_datum['roles']
    if roles_datum is None:
        return None

    return ', '.join([d['title'] for d in roles_datum])


def get_certs(user_datum):
    certs = user_datum['certifications']
    if certs is None:
        return None

    cert_builder = []
    for cert in certs:
        if cert['passed']:
            cert_builder.append(cert['certification']['title'])
    return ', '.join(cert_builder)


def format_orgs(user_datum):
    orgs = user_datum['orgs']
    org_builder = []
    if orgs is None:
        return "N/A"
    else:
        for org in orgs:
            org_builder.extend([f"\n[U] **Name:** {org['name']}",
                                f"[U] SID: {org['sid']}",
                                f"[U] Rank: {org['rank']}",
                                f"[U] Roles: {clean(', '.join(org['roles']))}"])
    return '\n'.join(org_builder)


def member_status(user):
    if user is None:
        return 'Not Found', False
    elif not user['isMember']:
        return 'Not a Member', False
    elif not user['verified']:
        return 'Not Verified', False

    if user['isAffiliate']:
        return 'Affiliate', True
    else:
        return 'Employee', True
