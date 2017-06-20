import spotipy
if __name__ == '__main__':
    name = 'Ed Sheeran'
    spotify = spotipy.Spotify()
    results = spotify.search(q='artist:' + name, type='artist')
    print(results)



