import time
import json
import requests
# from pprint import pprint

class User_vk:

    def __init__(self, user_id):
        self.token = token
        self.user_id = user_id
        self.version = version

    def get_groups(self):
        response = requests.get(
                'https://api.vk.com/method/groups.get?',
                params = {
                    'user_id': self.user_id,
                    'count': 1000,  # default 1000
                    'extended': 0,
                    'access_token': self.token,
                    'v': self.version
                    }
                )
        print('.')
        time.sleep(time_sleep)
        return response.json()

    def get_friends_id(self):
        friends_id = list()
        response = requests.get(
                'https://api.vk.com/method/friends.get?',
                params = {
                    'user_id': self.user_id,
                    'count': 5000,  # default 5000
                    'access_token': self.token,
                    'v': self.version
                    }
                )
        print('.')
        time.sleep(time_sleep)
        try:
            for friend in response.json()["response"]["items"]:
                friends_id.append(friend)
        except KeyError:
            print('key error')
        return friends_id


def original_groups(user_id):
    user = User_vk(user_id)
    user_orig_groups = user.get_groups()['response']['items']
    friends_id = user.get_friends_id()
    number_friend = 0
    total_friend = len(friends_id)
    for friend_id in friends_id:
        number_friend += 1
        try:
            friend = User_vk(friend_id)
            friend_groups = friend.get_groups()['response']['items']
            user_orig_groups = list(set(user_orig_groups) - set(friend_groups))
        except KeyError:
            continue
        finally:
            if number_friend % 10 == 0:
                print(f'Сравнили с {number_friend} друзьями, осталось {total_friend - number_friend}')
    return user_orig_groups

def data_group(group_id):
    response = requests.get(
                    'https://api.vk.com/method/groups.getById?',
                    params = {
                        'group_id': group_id,
                        'fields': 'members_count',
                        'access_token': token,
                        'v': version
                        }
                    )
    print('.')
    time.sleep(time_sleep)
    group = response.json()
    return group['response'][0]


def create_file(groups_id):
    print('Получение данных по оригинальным группам...')
    groups = list()
    for group in groups_id:
        one_group = dict()
        one_group['name'] = data_group(group)['name']
        one_group['id'] = data_group(group)['id']
        one_group['members_count'] = data_group(group)['members_count']
        groups.append(one_group)
    print('Данные получены, идет запись...')
    with open('groups.json', 'w') as f:
        json.dump(groups, f, ensure_ascii=False, indent=4)
    print('Данные успешно сохранены.')


if __name__ == '__main__':
    time_sleep = 0.001
    main_user_id = 171691064
    version = '5.103'
    token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    groups = original_groups(main_user_id)
    print('Сравнение групп окончено успешно.')
    if len(groups) == 0:
        print(f'У пользователя {main_user_id} нет оригинальных групп, сохранять нечего')
    else:
        print(f'У пользователя {main_user_id} {len(groups)} оригинальных групп, запись данных...')
        create_file(groups)
    print("Программа завершена.")
