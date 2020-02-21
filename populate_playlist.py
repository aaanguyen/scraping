import sys, json, spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import date


playlists = {
    'shazam_discovery_us': '4B2hxmDkBW1Hux2NcVp7hU',
    'shazam_discovery_canada': '3fG26aIk6OqSwo7nS0iWJH',
    'shazam_top200us': '0pw4biduKpuwd0qXUHD3q5',
    'soundcloud_newandhotUS': '4PURPAQZ4wzH6VnPZWkHUd',
    'soundcloud_top50us': '75Cymdvg0kSmGDJRJDEsGW',
    'youtube': ''
}


def populate(sp, playlist_id, data, all_track_ids):
    username = 'aa_nguyen'
    todays_date = date.today()
    first_100_ids = []
    second_100_ids = []
    missing_tracks = []

    for idx, item in enumerate(data):
        title_and_artist = "-".join([item['title'],item['artist']])
        if title_and_artist in all_track_ids:
            id_to_add = all_track_ids[title_and_artist]
        else:
            q = " ".join([item['title'], item['artist'].split(" ")[0]])
            search_result = sp.search(q,limit=1,type='track')
            if search_result['tracks']['items']:
                print(search_result['tracks']['items'][0]['id'], search_result['tracks']['items'][0]['name'], search_result['tracks']['items'][0]['artists'][0]['name'])
                id_to_add = search_result['tracks']['items'][0]['id']
                all_track_ids[title_and_artist] = id_to_add
            else:
                missing_tracks.append("{title} - {artist}".format(title=item['title'],artist=item['artist']))
                continue
        if idx < 100 and id_to_add not in first_100_ids:
            first_100_ids.append(id_to_add)
        elif idx >= 100 and id_to_add not in second_100_ids:
            second_100_ids.append(id_to_add)

    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)

    if token:
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        sp.user_playlist_replace_tracks(username, playlist_id, first_100_ids)
        if second_100_ids:
            results = sp.user_playlist_add_tracks(username, playlist_id, second_100_ids)
            print(results)
    else:
        print("Can't get token for", username)

    sp.user_playlist_change_details(username, playlist_id, description="Last updated: {date}. Missing tracks: {list}".format(date=todays_date, list=", ".join(missing_tracks)))


def main(filename):
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist_id = playlists[filename.split('.')[0]]
    with open(filename, 'r') as f:
        data = json.load(f)
    with open('track_id_list.json', 'r') as f:
        all_track_ids = json.load(f)
    populate(sp, playlist_id, data, all_track_ids)
    with open('track_id_list.json', 'w') as f:
        json.dump(all_track_ids, f, indent=4)

if __name__ == "__main__":
    main(sys.argv[1])
