from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from mobiglas.config import settings

config = settings.scorgsite

headers = {'Authorization': 'Bot {}'.format(config.secret)}
client = Client(transport=RequestsHTTPTransport(url=config.url, headers=headers, use_json=True),
                fetch_schema_from_transport=True)


def get_discord_role_configs():
    """
    Queries Graph DB for discord role configurations.
    """
    query = gql('''
    {
      roles(discordRoleConfigs_Enabled: true) {
        discordRoleConfigs {
          name
          mentionable
          enabled
          hoist
          permissions
          color
        }
      }
      ranks(discordRoleConfigs_Enabled: true) {
        discordRoleConfigs {
          name
          mentionable
          enabled
          hoist
          permissions
          color
        }
      }
      certifications(discordRoleConfigs_Enabled: true) {
        discordRoleConfigs {
          name
          mentionable
          enabled
          hoist
          permissions
          color
        }
      }
    }
    ''')
    try:
        return client.execute(query)
    except:
        return None


def get_user_roles(username):
    """
    Queries Graph DB for user role info.
    User roles are directly tied to there discord roles.
    """
    query = gql('''
    query getUser($username: String!) {
      socialAccount(provider: "discord", username: $username) {
        user {
          handle
          isMember
          verified
          isEmployee
          isAffiliate
          roles(discordRoleConfigs_Enabled: true) {
            discordRoleConfigs {
              name
            }
          }
          rank {
            name
          }
          certifications {
            passed
            certification {
              title
            }
          }
        }
      }
    }
    ''')
    try:
        return client.execute(query, variable_values={'username': username})['socialAccount']['user']
    except:
        return None


def get_citizen(handle):
    """
    Queries Graph DB for user info.
    User info consists of Org info, and Rsi profile info
    """
    query = gql('''
    query getCitizen($handle: String!) {
      user(handle: $handle) {
        isMember
        isHidden
        isAdmin
        isAffiliate
        isEmployee
        isStaff
        verified
        rank {
          name
        }
        roles {
          title
        }
        certifications {
          passed
          certification {
            title
          }
        }
      }
      citizen(handle: $handle) {
        avatar
        url
        username
        handle
        citizenRecord
        enlisted
        title
        bio
        location
        languages
        orgs
      }
    }

    ''')
    try:
        response = client.execute(query, variable_values={'handle': handle})
        return response['user'], response['citizen']
    except:
        return None


def get_possible_ships(name):
    """
    Queries Graph DB for a Ship given ship name
    NLP: Best effort approach
    """
    query = gql('''
    query ships($ship_name: String!) {
        ships(name_Icontains: $ship_name) {
            name,
            manufacturer {
                name
            },
            url,
            focus,
            length,
            height,
            beam,
            mass,
            minCrew,
            maxCrew,
            cargoCapacity,
            pledgeCost,
            images
        }
    }
    ''')

    return client.execute(query, variable_values={'ship_name': name})['ships']
