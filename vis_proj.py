
from sklearn.manifold import TSNE
from pandas.core.frame import DataFrame
import tekore as tk
import numpy as np
import pandas as pd
from numpy.polynomial.chebyshev import chebfit,chebval
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt, mpld3
from sklearn.cluster import KMeans
import os
import requests
import time
import urllib




def interval_vec(interval_list, title):
    dur = 0
    for i in interval_list:
        dur += i.duration
    titles = [f'average {title} interval duration', 'num of intervals']
    data= dur / len(interval_list), len(interval_list)
    return pd.Series(index = titles, data=data)

def section_vec(section_list, duration):
    loudness = 0
    tempo = 0
    key = 0
    loud_l =[]
    tempo_l = []
    key_l = []
    key_c, tempo_c, loud_c = 0,0,0
    for i in section_list:
        percentage = i.duration / duration
        loudness += percentage * i.loudness
        tempo += percentage * i.tempo
        key += percentage * i.key
        if len(loud_l):
            key_c += key_l[-1] != i.key
            tempo_c += tempo_l[-1] < i.tempo
            loud_c += loud_l[-1] < i.loudness
        loud_l.append(i.loudness)
        tempo_l.append(i.tempo)
        key_l.append(i.key)
    titles = ["average loudness", "average tempo","average key", "loudness std", "tempo std", "key std", "key change", "tempo change", "loudness change", "num sections"]
    data = loudness, tempo, key, np.std(loud_l), np.std(tempo_l), np.std(key_l), key_c /(len(section_list) -1), tempo_c /(len(section_list) -1), loud_c /(len(section_list) -1), len(section_list)
    return pd.Series(index=titles, data=data)

def segment_vec(segment_list, duration):
    last_timbre = []
    last_pitches = []
    timbre_avg = np.zeros(12)
    pitches_avg = np.zeros(12)
    matrix = np.empty((len(segment_list), 25))
    dur_vec = []
    x_vec = []
    for seg in segment_list:
        cur_p =list(seg.pitches)
        cur_t =  list(seg.timbre)
        x_vec.append(seg.start)
        dur_vec.append(seg.duration)
        matrix[-1] = [seg.loudness_max ] + cur_p + cur_t

    data = np.nan_to_num(matrix.T) @ dur_vec
    func =  chebfit(x_vec,np.nan_to_num(np.sum(matrix, axis=1)),12)
    print(f"x shape: {len(x_vec)}, sum shape: {np.sum(matrix, axis=1).shape}")
    result =  chebfit(x_vec,np.nan_to_num(np.sum(matrix, axis=1)),8)
    print(result)
    titles = ["loudness_max avg"] + [f"pitches {i} avg" for i in range(12)] +[f"ptimbre {i} avg" for i in range(12)] + [f"poly coef{i % 31} {i % 25}" for i in range(result.shape[0])] 
    
    
#     return  pd.Series(index=titles, data =list(data) + list(data_std))
    return pd.Series(index=titles , data=np.concatenate([result,data]))
                    
def song_vector(song):
    duration = song.track['duration']
    song_meta = pd.Series(index=['tempo', 'loudness'], data = [song.track['tempo'], song.track['loudness']])
    sections_vec = section_vec(song.sections, duration)
    bars_vec = interval_vec(song.bars, "bars")
    beats_vec = interval_vec(song.beats, "beats")
    # segments_vec = segment_vec(song.segments, duration)
    return pd.concat([song_meta, sections_vec,bars_vec, beats_vec])
    



def get_user_token():
# get the user token from the web
    print("copy the web address after you log in to your potify account")
    token  = tk.prompt_for_user_token(client_id, client_secret,SPOTIFY_REDIRECT_URI, scope = 'user-library-read playlist-read-private')
    return tk.Spotify(token)


def get_playlist(spotify):
    # choosing one of the users playlist
    print('\nChoose one of your playlists:\n')
    for i in range(len(spotify.followed_playlists().items)):
        print(f"{i + 1}) {spotify.followed_playlists().items[i].name} - {spotify.followed_playlists().items[i].tracks.total}")
    playlist_idx = int(input("")) - 1
    return spotify.playlist_items(spotify.followed_playlists().items[playlist_idx].id, as_tracks=False).items

def get_track_feat(id):
    audio_feat = spotify.track_audio_features(id)
    return pd.Series({"acousticness":audio_feat.acousticness,
                     "danceability" :audio_feat.danceability,
                     "energy":audio_feat.energy,
                     "liveness": audio_feat.liveness,
                     "loudness": audio_feat.loudness,
                     "speechiness": audio_feat.speechiness,
                     "tempo": audio_feat.tempo,
                     "valence": audio_feat.valence})

def get_songs_data(tracks)-> pd.DataFrame: 
    songs_s = []
    songs_id =[i.track.id for i in tracks]
    artists_s = pd.Series()
    for i in range(len(tracks)):
        print(f"idx: {i} length list: {len(songs_s)} ")
        if not i + 1 % 100:
            time.sleep(15)
            print("sleeping!")
            pd.concat(songs_s, axis=1).T.to_csv("test_df.csv")
        track = tracks[i]
        song = track.track
        id = song.id
        print(id)
        song_data = song_vector(spotify.track_audio_analysis(id))
        song_f = get_track_feat(id)
        song_date = pd.Series(data=[song.album.release_date.split('-')[0]], index=["release year"])
        artists_s = pd.concat([artists_s,pd.Series(data=["|".join([i.name for i in song.artists])],index=[song.name + '-' + song.artists[0].name])])
        song_data = pd.concat([song_f, song_data, song_date]).rename(song.name + '-' + song.artists[0].name )
        songs_s.append(song_data)
    add = artists_s.str.get_dummies()
    result = pd.concat(songs_s, axis=1)
    all = pd.concat([result.T, add], axis=1)
    all['id'] = songs_id
    return all
 
def get_img(sp):
    i = 1
    songs_id = ["3QV4M9OwkkhN66dIURw3Ta"]
    # urls = [sp.track(id).album.images[0].url for id in songs_id]
    for id in songs_id:
        if os.path.exists(f"Visualization\\tmpv\{id}.jpeg"):
            continue
        with open(f"Visualization\\tmpv\{id}.jpeg", 'wb') as img:
            url = sp.track(id).album.images[0].url
            print(f"{sp.track(id).name} - {url}")
            #urllib.request.urlretrieve(url, f"Visualization\\tmpv\{id}.jpeg")
            img.write(requests.get(url=url).content)
            i += 1
            if not  i % 5: 
                time.sleep(30)
            time.sleep(5 if i % 2 else 7)
    
    
    
    
client_id = '4cc0d73dc6ae4e64b7318da7236f7f04'
client_secret = '3a88b3d055854dcb9cfe1a1ed8784942'
SPOTIFY_REDIRECT_URI= "http://localhost/"
app_token = tk.request_client_token(client_id, client_secret)
spotify = get_user_token()

def get_sdaved_tracks_ids():
    ids =[]
    offset = 0
    cur_tracks =spotify.saved_tracks(limit=50, offset=offset).items
    while len(cur_tracks):
        ids += [cur_tracks[i].track.id for i in range(len(cur_tracks))]
        offset += 50
        cur_tracks =spotify.saved_tracks(limit=50, offset=offset).items
    return ids


g = get_sdaved_tracks_ids()

# tracks = []
# F = 'Y'
# for i in range(1):
    # tracks = tracks + list(get_playlist(spotify))
#     get_img(spotify, tracks)
#     F = input('F = ')
# df = get_songs_data(tracks)
# df.to_csv("test_df1.csv", encoding="Windows-1255")
# # get_img(spotify)
# # df = df= pd.read_csv("test_df1.csv", index_col=0, encoding="Windows-1255")
# df = df[~df.isin([np.nan, np.inf, -np.inf]).any(1)]
# ids = df['id']
# df = df.drop(['id'], axis=1).astype(float)
# #Normalizing the needed columns (other columns are one hot vector or year)

# df.iloc[:,:24] = (df.iloc[:,:24]-df.iloc[:,:24].mean())/df.iloc[:,:24].std()
# # dropping columns which did not contribute
# dff =  df.drop(['loudness change','key change', 'tempo change'], axis=1)

# # Now lets do it all again w/o the year
# dff_wo_year =  dff.drop(['release year'], axis=1)
# kmeans = KMeans(n_clusters=5)
# kmeans.fit(dff_wo_year)

# #T-SNE analysis
# X_embedded = TSNE(n_components=2).fit_transform(dff_wo_year)
# rdf = pd.DataFrame(data=X_embedded, index=df.index).reset_index()
# rdf['release year'] = df['release year'].tolist()
# rdf['labels'] = kmeans.labels_
# rdf = rdf.astype(str)
# rdf['id'] = ids.reset_index(drop=True)
# rdf.to_csv("Visualization\\tsne_res.csv", encoding="Windows-1255")
#works
# urllib.request.urlretrieve("https://p.scdn.co/mp3-preview/66a332835c611a8a388e97d0495e3efa18ed96e8?cid=4cc0d73dc6ae4e64b7318da7236f7f04", "Visualization\\tmp_p\\testt.mp3")
# df = df.rename(columns=df.iloc[0])
# df = df[1:]
# df = df.replace(np.inf,np.nan)
# df = df.replace(-np.inf,np.nan).dropna(axis=1)
# print((df[df == np.nan]).shape)
# df.to_csv("test_df.csv")

'urllib.request.urlretrieve("https://p.scdn.co/mp3-preview/66a332835c611a8a388e97d0495e3efa18ed96e8?cid=4cc0d73dc6ae4e64b7318da7236f7f04", "tmp_p\\testt.mp3")'
