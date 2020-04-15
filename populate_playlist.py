import sys, json, spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import date

MAX_DESCRIPTION_LENGTH = 300

playlists = {
    'shazam_discovery_us': '',
    'shazam_discovery_canada': '',
    'shazam_top200us': '',
    'shazam_top200global': '',
    'soundcloud_newandhotUS': '',
    'soundcloud_top50us': '',
    'new_additions': ''
}


def populate(sp, playlist_id, scraped_data, all_track_ids):

    def update_target_playlist(token):
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        sp.user_playlist_change_details(username, playlist_id, description="Last updated: {date}. Missing tracks: {list}".format(date=todays_date, list=", ".join(missing_tracks)[:MAX_DESCRIPTION_LENGTH]))
        sp.user_playlist_replace_tracks(username, playlist_id, first_100_ids)
        if second_100_ids:
            results = sp.user_playlist_add_tracks(username, playlist_id, second_100_ids)
        print("{} updated".format(sys.argv[1].replace('.json','')))

    def update_new_additions(token):
        sp = spotipy.Spotify(auth=token)
        sp.trace = False
        sp.user_playlist_add_tracks(username, playlists['new_additions'], new_additions)

    def build_query(item):
        query = " ".join([item['title'], item['artist'].split(" ")[0]]) if item['artist'] else item['title']
        if sys.argv[1][:10] == "soundcloud":
            query += " year:{}-{}".format(str(date.today().year-1),str(date.today().year))
        return query

    def update_missing_tracks_description(item):
        missing_track = item['title']
        if item['artist']:
            missing_track += " - {}".format(item['artist'])
        missing_track = " ".join(w.capitalize() for w in missing_track.split())
        missing_tracks.append(missing_track)

    username = ''
    todays_date = date.today()
    first_100_ids = []
    second_100_ids = []
    missing_tracks = []
    new_additions = []

    for idx, item in enumerate(scraped_data):
        if item['artist']:
            title_and_artist = "-".join([item['title'],item['artist']])
        else:
            title_and_artist = item['title']
        if title_and_artist in all_track_ids:
            id_to_add = all_track_ids[title_and_artist]
        else:
            query = build_query(item)
            search_result = sp.search(query,limit=1,type='track')
            if search_result['tracks']['items']:
                print(search_result['tracks']['items'][0]['id'], search_result['tracks']['items'][0]['name'], search_result['tracks']['items'][0]['artists'][0]['name'])
                id_to_add = search_result['tracks']['items'][0]['id']
                all_track_ids[title_and_artist] = id_to_add
                new_additions.append(id_to_add)
            else:
                update_missing_tracks_description(item)
                continue
        if idx < 100 and id_to_add not in first_100_ids:
            first_100_ids.append(id_to_add)
        elif idx >= 100 and id_to_add not in second_100_ids:
            second_100_ids.append(id_to_add)

    scope = 'playlist-modify-public'
    token = util.prompt_for_user_token(username, scope)
    if token:
        update_target_playlist(token)
        update_new_additions(token)
    else:
        print("Can't get token for", username)



def main():
    client_credentials_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    playlist_id = playlists[sys.argv[1].replace('.json','')]

    with open(sys.argv[1], 'r') as f:
        scraped_data = json.load(f)

    with open('track_id_list.json', 'r') as f:
        all_track_ids_data = json.load(f)

    populate(sp, playlist_id, scraped_data, all_track_ids_data)

    with open('track_id_list.json', 'w') as f:
        json.dump(all_track_ids_data, f, indent=4)

if __name__ == "__main__":
    main()
