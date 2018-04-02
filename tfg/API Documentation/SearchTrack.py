import spotipy
import spotipy.util as util
import json
import sys

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # Something just like this
    track_id = '6RUKPb4LETWmmr3iAEQktW'
    sp = spotipy.Spotify(auth=token)
    track_info = sp.track(track_id)
    print(json.dumps(track_info, indent=1))

    print(track_info['id'])

    print(track_info['popularity'])

    print(track_info['external_urls']['spotify'])

    print(track_info['album']['name'])

    print(track_info['album']['release_date'])

    duration_s = track_info['duration_ms'] / 1000

    duration_min = duration_s / 60

    i = 0

    while i + 1 < duration_min:
        i = i + 1

    duration_s = duration_min - i

    duration_s = duration_s * 60

    print("Min: ", i, " Seg: ", duration_s)

    print(track_info['album']['images'][1]['url'])

    print(track_info['preview_url'])
else:
    print("Can't get token for", username)
