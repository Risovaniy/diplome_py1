import time
import json
import requests


class User_vk:
    
    def __init__(self, user_id):
        self.token = token
        self.user_id = user_id
        self.version = version

    def check_name_or_id(self):
        response = requests.get(
                'https://api.vk.com/method/users.get?',
                params = {
                    'user_ids': self.user_id,
                    'access_token': self.token,
                    'v': self.version
                    }
                )
        print('.')
        try:
            result = response.json()['response'][0]['id']
        except Exception:
            try:
                time.sleep(TIME_SLEEP)
                check = response.json()['error']['error_code']
            except KeyError:
                time.sleep(TIME_SLEEP)
                User_vk.check_name_or_id(self)
            else:
                if check == 30:
                    raise ValueError
                elif check == 18:
                    raise ValueError
        else:
            self.user_id = result

    def get_groups(self):
        response = requests.get(
            'https://api.vk.com/method/groups.get?',
            params={
                'user_id': self.user_id,
                'count': 1000,  # default 1000
                'extended': 0,
                'access_token': self.token,
                'v': self.version
            }
        )
        print('.')
        return response.json()

    def reque_friends_get(self):
        response = requests.get(
            'https://api.vk.com/method/friends.get?',
            params={
                'user_id': self.user_id,
                'count': 5000,  # default 5000
                'access_token': self.token,
                'v': self.version
            }
        )
        print('.')
        return response


    def get_friends_id(self):
        friends_id = list()
        response = User_vk.reque_friends_get(self).json()
        for friend in response["response"]["items"]:
            friends_id.append(friend)
        return friends_id


def check_groups(user):
    while True:
        groups = user.get_groups()
        try:
            result = groups['response']['items']
        except KeyError:
            if groups['error']['error_code'] == 6:
                continue
            elif groups['error']['error_code'] == 30:
                raise ValueError
            elif groups['error']['error_code'] == 18:
                raise ValueError
        else:
            return result


def original_groups(user_id):
    user = User_vk(user_id)
    user.check_name_or_id()
    user_orig_groups = check_groups(user)
    friends_id = user.get_friends_id()
    number_f = 0
    total_friend = len(friends_id)

    while number_f < total_friend:
        friend = User_vk(friends_id[number_f])
        try:
            friend_groups = friend.get_groups()['response']['items']
            number_f += 1
        except Exception:
            try:
                check = friend.get_groups()['error']['error_code']
                if check == 30:
                    print(f'Profile {friend.user_id} is private')
                    number_f += 1
                    continue
                elif check == 6:
                    time.sleep(TIME_SLEEP)
                    continue
                elif check == 18:
                    print(f'User {friend.user_id} was deleted or banned')
                    number_f += 1
                    continue
            except KeyError:
                time.sleep(TIME_SLEEP)
                continue
        else:
            user_orig_groups = list(set(user_orig_groups) - set(friend_groups))
        if number_f % 10 == 0:
            print(f'Сравнили с {number_f} друзьями, осталось {total_friend - number_f}')
    return user_orig_groups


def data_group(group_id):
    while True:
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
        try:
            group = response.json()['response'][0]
        except KeyError:
            time.sleep(TIME_SLEEP)
            continue
        else:
            return group


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
    TIME_SLEEP = 0.3
    main_user_id = input('Введите username или id пользователя "Вконтакте"\n')
    token = input('Введите token\n')
    version = '5.103'
    groups = original_groups(main_user_id)
    print('Сравнение групп окончено успешно.')
    if len(groups) == 0:
        print(f'У пользователя {main_user_id} нет оригинальных групп, сохранять нечего')
    else:
        print(f'У пользователя {main_user_id} {len(groups)} оригинальных групп, запись данных...')
        create_file(groups)
    print("Программа завершена.")
