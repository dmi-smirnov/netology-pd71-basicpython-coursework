import sys
sys.path.append('/tmp')
from secret import vk_token,yadisk_token,gdrive_token
import requests
import time
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

    api_req_status_code = api_resp.status_code
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

  def get_albums(self, api_token):
    api_method = 'photos.getAlbums'
    api_req_url = self.api_url + '/' + api_method + '/'
    user_id = self.get_user_id(api_token)
    if user_id is None:
      return
    api_req_params = {
      'v': self.api_version,
      'access_token': api_token,
      'owner_id': user_id,
      'need_system': 1
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

  def backup_photos_to_cloud(self, api_token: str, cloud: Cloud, album_photos_max_amt=5):
    albums = self.get_albums(api_token)
    if albums is None:
      return
    
    user_id = self.get_user_id(api_token)
    if user_id is None:
      return

    backup_dir_path = (f'/vk_user_id_{user_id}'
      '_photos_backup')
    if not cloud.create_dir(backup_dir_path) is None:
      return

    albums_amt = len(albums)
    album_count = 0
    for album in albums:
      album_name = album["title"]
      album_dir_path = (f'{backup_dir_path}/{album_name}')
      if not cloud.create_dir(album_dir_path) is None:
        return

      album_id = album['id']
      album_size = album['size']
      if album_photos_max_amt > album_size:
        album_photos_amt = album_size
      else:
        album_photos_amt = album_photos_max_amt
      if album_photos_amt > 1000:
        album_photos_amt = 1000
      if album_photos_amt < album_size:
        print(f'Album {album_name} contains {album_size} photos, '
          f'but only {album_photos_amt} photos will be uploaded.')
      album_photos = self.get_photos(api_token, album_id, album_photos_amt)
      if album_photos is None:
        return

      # key is photo name, value is photos list
      repeated_names_photos_1 = dict()
      # key is photo name, value is photo
      uniq_name_photos = dict()
      for photo in album_photos:
        photo_name = photo['likes']['count']
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
      album_count += 1
      print(f'Uploading album [{album_count}/{albums_amt}] {album_name}: '
          f'photo [0/{len(uniq_name_photos)}]', end='')
      for file_name,album_photo in uniq_name_photos.items():
        max_size_photo = max(album_photo['sizes'],
          key=lambda d: d['type'])
        photo_url = max_size_photo['url']
        file_path = f'{album_dir_path}/{file_name}'
        # pprint(album_photo['sizes'])
        # if 'width' in album_photo:
        #   print(album_photo['width'], album_photo['height'])
        # print(max_size_photo['width'], max_size_photo['height'], max_size_photo['type'])
        photo_count += 1
        print(f'\rUploading album [{album_count}/{albums_amt}] {album_name}: '
          f'photo [{photo_count}/{len(uniq_name_photos)}]', end='')
        if not cloud.upload_from_url(photo_url, file_path) is None:
          return
      print()

def main():
  # Запрос на ввод данных, трубуемых по заданию

  # vk_user_id = 'kuznya201386'
  # vk_user_id = 764687792
  vk_user_id = 'dmi.smirnov'
  # vk_user_id = 'linka_evelin'
  # vk_user_id = 'kitsuneri'

  vk_user = VKuser(vk_user_id)
  album_photos_max_amt = 100 
  cloud = Yadisk(yadisk_token)
  # vk_user.backup_photos_to_cloud(vk_token, cloud, album_photos_max_amt)
  vk_user.backup_photos_to_cloud(vk_token, cloud)

main()