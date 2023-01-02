import requests
import time
import json
from pprint import pprint

class Cloud():
  def __init__(self, cloud_token):
    self.cloud_token = cloud_token
  
  def create_dir(self, dir_path):
    pass
  
  def upload_from_url(url):
    pass

class Yadisk(Cloud):
  api_url = 'https://cloud-api.yandex.net'

  def create_dir(self, dir_path):
    api_route = '/v1/disk/resources'
    api_req_url = self.api_url + api_route
    api_req_headers = {'Authorization': self.cloud_token}
    api_req_params = {'path': dir_path}

    api_resp = requests.put(api_req_url, headers=api_req_headers,
      params=api_req_params)
    
    api_req_status_code = api_resp.status_code
    if api_req_status_code == 409:
      print(f'Error Yandex Disk API method {api_route}: '
      f'HTTP request status code is {api_req_status_code}, '
      f'directory {dir_path} is already exists.')
      return 1
    if api_req_status_code != 201:
      print(f'Error Yandex Disk API method {api_route}: '
      f'HTTP request status code is {api_req_status_code}')
      return 1

  def upload_from_url(self, url, file_path):
    api_route = '/v1/disk/resources/upload'
    api_req_url = self.api_url + api_route
    api_req_headers = {'Authorization': self.cloud_token}
    api_req_params = {
      'url': url,
      'path': file_path
      }

    api_resp = requests.post(api_req_url, headers=api_req_headers,
    params=api_req_params)
    
    api_req_status_code = api_resp.status_code
    if api_req_status_code != 202:
      print(f'Error Yandex Disk API method {api_route}: '
      f'HTTP request status code is {api_req_status_code}')
      return 1
    
  def get_upload_url(self, file_path):
    api_route = '/v1/disk/resources/upload'
    api_req_url = self.api_url + api_route
    api_req_headers = {'Authorization': self.cloud_token}
    api_req_params = {
      'path': file_path
      }

    api_resp = requests.get(api_req_url, headers=api_req_headers,
    params=api_req_params)

    api_req_status_code = api_resp.status_code
    if api_req_status_code != 200:
      print(f'Error Yandex Disk API method {api_route}: '
      f'HTTP request status code is {api_req_status_code}')
      return 1

    return api_resp.json()['href']

  def upload_json(self, obj, file_path):
    api_upload_url = self.get_upload_url(file_path)
    json_str = json.dumps(obj, indent=2)
    file_bytes = json_str.encode('UTF-8')

    api_resp = requests.put(api_upload_url, data=file_bytes)

    api_req_status_code = api_resp.status_code
    if api_req_status_code != 201:
      print(f'Error Yandex Disk API file uploading: '
      f'HTTP request status code is {api_req_status_code}')
      return 1

class VKuser():
  api_url = 'https://api.vk.com/method'
  api_version = '5.131'

  def __init__(self, user_id):
    if isinstance(user_id, int):
      self.user_id = user_id
    elif isinstance(user_id, str):
      self.user_id = None
      self.screen_name = user_id

  def resolve_screen_name(self, api_token, screen_name):
    api_method = 'utils.resolveScreenName'
    api_req_url = self.api_url + '/' + api_method + '/'
    api_req_params = {
      'v': self.api_version,
      'access_token': api_token,
      'screen_name': screen_name
    }

    api_resp = requests.get(api_req_url, params=api_req_params)

    api_req_status_code = api_resp.status_code
    if api_req_status_code != 200:
      print(f'Error VK API method {api_method}: '
      f'HTTP request status code is {api_req_status_code}')
      return
      
    if 'error' in api_resp.json():
      error_dict = api_resp.json()['error']
      print(f'Error VK API method {api_method}:\n'
      f'error code: {error_dict["error_code"]}\n'
      f'error message: {error_dict["error_msg"]}')
      return

    if len(api_resp.json()['response']) == 0:
      print(f'Error VK API method {api_method}: '
        f'VK screen name {screen_name} not found.')
      return

    type_object = api_resp.json()['response']['type']
    if not type_object == 'user':
      print(f'Error: {self.screen_name} is not user, '
      f'it is {type_object}')
      return

    return int(api_resp.json()['response']['object_id'])

  def get_user_id(self, api_token):
    if self.user_id is None:
      self.user_id = self.resolve_screen_name(api_token,
      self.screen_name)
    return self.user_id

  def get_albums(self, api_token, albums: list=None):
    api_method = 'photos.getAlbums'
    api_req_url = self.api_url + '/' + api_method + '/'
    user_id = self.get_user_id(api_token)
    if user_id is None:
      return
    api_req_params = {
      'v': self.api_version,
      'access_token': api_token,
      'owner_id': user_id
    }
    if albums:
      album_ids = ','.join(albums)
      api_req_params['album_ids'] = album_ids
    else:
      api_req_params['need_system'] = 1

    api_resp = requests.get(api_req_url, params=api_req_params)

    api_req_status_code = api_resp.status_code
    if api_req_status_code != 200:
      print(f'Error VK API method {api_method}: '
      f'HTTP request status code is {api_req_status_code}')
      return

    if 'error' in api_resp.json():
      error_dict = api_resp.json()['error']
      print(f'Error VK API method {api_method}:\n'
      f'error code: {error_dict["error_code"]}\n'
      f'error message: {error_dict["error_msg"]}')
      return
    
    return api_resp.json()['response']['items']

  def get_photos(self, api_token, user_album_id, photos_amt):
    api_method = 'photos.get'
    api_req_url = self.api_url + '/' + api_method + '/'
    user_id = self.get_user_id(api_token)
    if user_id is None:
      return
    api_req_params = {
      'v': self.api_version,
      'access_token': api_token,
      'owner_id': user_id,
      'album_id': user_album_id,
      'extended': 1,
      'count': photos_amt
    }

    api_resp = requests.get(api_req_url, params=api_req_params)

    api_req_status_code = api_resp.status_code
    if api_req_status_code != 200:
      print(f'Error VK API method {api_method}: '
      f'HTTP request status code is {api_req_status_code}')
      return

    if 'error' in api_resp.json():
      error_dict = api_resp.json()['error']
      print(f'Error VK API method {api_method}:\n'
      f'error code: {error_dict["error_code"]}\n'
      f'error message: {error_dict["error_msg"]}')
      return

    return api_resp.json()['response']['items']

  def backup_photos_to_cloud(self, api_token: str, cloud: Cloud):
    all_albums_uploading_answer = not input('Загрузить все альбомы?\n'
      'Enter - да, любой символ и Enter - только фотографии профиля: ')
    if all_albums_uploading_answer:
      print('Выбрана загрузка всех альбомов.', end='\n\n')
    else:
      print('Выбрана загрузка только фотографий профиля.', end='\n\n')
    
    print('Получение информации об альбомах пользователя... ', end='')
    if all_albums_uploading_answer:
      albums = self.get_albums(api_token)
    else:
      profile_photos_album_id = '-6'
      albums = \
        self.get_albums(api_token, albums=[profile_photos_album_id])
    if albums is None:
      return
    albums_amt = len(albums)
    print(f'OK: альбомов {albums_amt}', end='\n\n')
    
    album_photos_max_amt_input = \
      input('Сколько сохранять фотографий из альбома?\n'
      'Enter - 5 фотографий, число и Enter - задать количество: ')
    if (isinstance(album_photos_max_amt_input, str) and 
      album_photos_max_amt_input.isnumeric()):
      album_photos_max_amt = int(album_photos_max_amt_input)
    else:
      album_photos_max_amt = 5
    print(f'Выбрано сохранение не более {album_photos_max_amt} '
      'фото с альбома.', end='\n\n')

    user_id = self.get_user_id(api_token)
    if user_id is None:
      return

    
    backup_dir_path = (f'/vk_user_id_{user_id}'
      '_photos_backup')
    print('Создание в облаке директории для пользователя... ', end='')
    if not cloud.create_dir(backup_dir_path) is None:
      return
    print(f'OK: {backup_dir_path}', end='\n\n')

    album_count = 0
    for album in albums:
      album_count += 1
      album_json = []
      album_name = album["title"]
      album_size = album['size']
      print(f'Альбом [{album_count}/{albums_amt}] {album_name}, {album_size} фото.')
      album_dir_path = (f'{backup_dir_path}/{album_name}')

      if album_photos_max_amt > album_size:
        album_photos_amt = album_size
      else:
        album_photos_amt = album_photos_max_amt
      if album_photos_amt > 1000:
        album_photos_amt = 1000
      if album_photos_amt < album_size:
        print(f'Будут загружены только {album_photos_amt} фото.')
      
      print('Создание в облаке директории для альбома... ', end='')
      if not cloud.create_dir(album_dir_path) is None:
        return
      print(f'OK: {album_dir_path}')

      print('Получение информации о фотографиях альбома... ', end='')
      album_photos = \
        self.get_photos(api_token, album['id'], album_photos_amt)
      if album_photos is None:
        return
      print('OK.')

      # key is photo name, value is photos list
      repeated_names_photos_1 = dict()
      # key is photo name, value is photo
      uniq_name_photos = dict()
      for photo in album_photos:
        photo_name = str(photo['likes']['count'])
        if photo_name in repeated_names_photos_1:
          repeated_names_photos_1[photo_name].append(photo)
        elif photo_name in uniq_name_photos.keys():
            repeated_names_photos_1[photo_name] = [
              uniq_name_photos.pop(photo_name),
              photo
            ]
        else:
          uniq_name_photos[photo_name] = photo

      # key is photo name, value is photos list
      repeated_names_photos_2 = dict()
      for repeated_photo_name,photos in repeated_names_photos_1.items():
        for photo in photos:
          photo_date = \
            time.strftime('%Y-%m-%d_%H-%M-%S', time.gmtime(photo['date']))
          photo_name = f'{repeated_photo_name}_{photo_date}'
          if photo_name in repeated_names_photos_2:
            repeated_names_photos_2[photo_name].append(photo)
          elif photo_name in uniq_name_photos.keys():
              repeated_names_photos_2[photo_name] = [
                uniq_name_photos.pop(photo_name),
                photo
              ]
          else:
            uniq_name_photos[photo_name] = photo

      for repeated_photo_name,photos in repeated_names_photos_2.items():
        for photo in photos:
          photo_name = f'{repeated_photo_name}_{photo["id"]}'
          uniq_name_photos[photo_name] = photo

      photo_count = 0
      print(f'Загрузка в облако '
        f'фото [0/{len(uniq_name_photos)}]', end='')
      
      for file_name,album_photo in uniq_name_photos.items():
        photo_sizes_types = dict()
        for photo_size in album_photo['sizes']:
          photo_sizes_types[photo_size['type']] = photo_size['url']
        for size_type in ('w', 'z', 'y', 'x', 'm', 's'):
          if size_type in photo_sizes_types.keys():
            photo_max_size_type = size_type
            break
        album_json.append({
          'file_name': file_name,
          'size': photo_max_size_type
        })
        photo_url = photo_sizes_types[photo_max_size_type]
        photo_file_path = f'{album_dir_path}/{file_name}'
        photo_count += 1
        print(f'\rЗагрузка в облако '
          f'фото [{photo_count}/{len(uniq_name_photos)}]...', end='')
        if not cloud.upload_from_url(photo_url, photo_file_path) is None:
          return
      print('\rЗагрузка фотографий альбома в облако завершена.')
      print('Создание в директории альбома json-файла... ', end='')
      json_file_path = f'{album_dir_path}/{album_name}.json'
      if not cloud.upload_json(album_json, json_file_path) is None:
          return
      print(f'OK: {json_file_path}', end='\n\n')

def get_vk_user_id():
  vk_user_id = input('Введите ID или видимое имя пользователя VK: ')
  if vk_user_id.isnumeric():
    if not input('Вы ввели ID? Enter - да, любой символ и Enter - нет: '):
      vk_user_id = int(vk_user_id)
      print('ID пользователя VK получен.', end='\n\n')
      return vk_user_id
  print('Видимое имя пользователя VK получено.', end='\n\n')
  return vk_user_id

def get_vk_token():
  vk_token = None
  while not vk_token:
    vk_token = input('Введите ключ API VK: ')
  print('Ключ API VK получен.', end='\n\n')
  return vk_token

def get_cloud():
  yadisk_or_gdrive = not input('Яндекс.Диск или Google Drive?\n'
    'Enter - Яндекс.Диск, любой символ и Enter - Google Drive: ')
  if yadisk_or_gdrive:
    print('Выбрано облако Яндекс.Диск.', end='\n\n')
  else:
    print('Выбрано облако Google Drive.', end='\n\n')
  cloud_token = None
  while not cloud_token:
    cloud_token = input('Введите ключ API выбранного облака: ')
  if yadisk_or_gdrive:
    cloud = Yadisk(cloud_token)
  # else:
  #   cloud = Gdrive(cloud_token)
  print('Ключ API получен.', end='\n\n')
  return cloud

VKuser(get_vk_user_id()).backup_photos_to_cloud(
  get_vk_token(),
  get_cloud()
)