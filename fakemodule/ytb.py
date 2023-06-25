from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import spotipy,json,pickle,os,re,datetime,urllib.parse
from spotipy.oauth2 import SpotifyClientCredentials
from urllib.parse import parse_qs, urlparse

with open('jsonfile/API.json', 'r') as f:
    Config = json.load(f)
client_id= Config['sclient_id']
client_secret= Config['sclient_secret']
sp = spotipy.Spotify(auth_manager= SpotifyClientCredentials(client_id=client_id,client_secret=client_secret))
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
def youtube_authenticate():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "jsonfile/API.json"
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("jsonfile/token.pickle"):
        with open("jsonfile/token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open("jsonfile/token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(api_service_name, api_version, credentials=creds)


def get_channel_details(youtube, **kwargs):
    return youtube.channels().list(
        part="statistics,snippet,contentDetails",
        **kwargs
    ).execute()
def get_channel_videos(youtube, **kwargs):
    return youtube.search().list(
        **kwargs
    ).execute()

def search(youtube, **kwargs):
    return youtube.search().list(
        part="snippet",
        **kwargs
    ).execute()

def get_video_details(youtube, **kwargs):
    return youtube.videos().list(
        part="snippet,contentDetails,statistics",
        **kwargs
    ).execute()


def time_public(time):
    pip= datetime.datetime.strptime(time[0:19], "%Y-%m-%dT%H:%M:%S")  
    a = datetime.datetime.now()
    c = a - pip
    d, h, m = c.days, c.seconds // 3600, c.seconds // 60 % 60
    if m==0:
        pu=('{} Giây Trước'.format(c))
    if h==0:
        pu=('{} Phút Trước'.format(m))
    if d==0:
        pu=('{} Giờ Trước'.format(h))
    if d>=1:
        pu=('{} Ngày Trước'.format(d))
        if d%7==0:
            t=d//7
            pu=('{} Tuần Trước'.format(t))
    if d>=30:
        w=d//30
        if w>=12:
            y=w//12
            pu=('{} Năm Trước'.format(y))
        else:
            pu=('{} Tháng Trước'.format(w))
    return(pu)

def getidspo(value):
    query = urllib.parse.urlparse(value)
    if query.hostname in ('open.spotify.com'):
        if query.path[:10] == '/playlist/':
            return query.path.split('/')[2]
        if query.path[:7] == '/track/':
            return query.path.split('/')[2]
        if query.path[:7] == '/album/':
            return query.path.split('/')[2]

    return None

def to_seconds(timestr):
    d,h, m, s = timestr.split(':')
    hh=+int(d)*24
    h=int(h)+hh
    return int(h) * 3600 + int(m) * 60 + int(s)
def print_video_infos(youtube,video_response):
    items = video_response.get("items")[0]
    # get the snippet, statistics & content details from the video response
    snippet         = items["snippet"]
    statistics      = items["statistics"]
    content_details = items["contentDetails"]
    # get infos from the snippet
    channel_title = snippet["channelTitle"]
    title         = snippet["title"]
    description   = snippet["description"]
    publish_time  = snippet["publishedAt"]
    res = 0
    max_image = None
    for item in snippet['thumbnails']:
        if res < snippet['thumbnails'][item]['width']:
            res = snippet['thumbnails'][item]['width']
            max_image = item
    image=(snippet['thumbnails'][max_image]['url'])
    # get stats infos

    view_count    = statistics["viewCount"]
    # get duration from content details
    duration = content_details["duration"]
    channel_id= snippet["channelId"]
    response = get_channel_details(youtube, id=channel_id)

    res = 0
    max_image = None
    for item in response['items'][0]['snippet']['thumbnails']:
        if res < response['items'][0]['snippet']['thumbnails'][item]['width']:
            res = response['items'][0]['snippet']['thumbnails'][item]['width']
            max_image = item
    imagechan=(response['items'][0]['snippet']['thumbnails'][max_image]['url'])

    linkchane=f'https://www.youtube.com/channel/{channel_id}'
    pu=time_public(publish_time)
    if "M" not in duration:
        duration+="00M"
    if "S" not in duration:
        duration+="00S"
    if "H" not in duration:
        if "D" in duration:
            cc=duration.find('T')+1
        else:
            cc=2
        aa=duration[:cc]+'00H'
        duration=aa+duration[cc:]
    if "D" not in duration:
        aa='P00DT'
        duration=aa+duration[2:]
    parsed_duration=re.search(f"P(\d+D)?T(\d+H)?(\d+M)?(\d+S)", duration)
    parsed_duration=parsed_duration.groups()
    duration_str = ""
    for d in parsed_duration:
        if d:
            duration_str += f"{d[:-1]}:"
    duration_str = duration_str.strip(":")
    duration_str=to_seconds(duration_str)
    return{
        'Title': title,
        'imagechannel':imagechan,
        'imagevideo':image,
        'linkchannel':linkchane,
        'Description':description,
        'Channel_name': channel_title,
       'Publish_time': pu,
        'Duration': duration_str,
        'views': view_count
        }

def parse_channel_url(url):
    """
    This function takes channel `url` to check whether it includes a
    channel ID, user ID or channel name
    """
    path = urllib.parse.urlparse(url).path
    id = path.split("/")[-1]
    if "/c/" in path:
        return "c", id
    elif "/channel/" in path:
        return "channel", id
    elif "/user/" in path:
        return "user", id


def get_channel_id_by_url(youtube, url):
    """
    Returns channel ID of a given `id` and `method`
    - `method` (str): can be 'c', 'channel', 'user'
    - `id` (str): if method is 'c', then `id` is display name
        if method is 'channel', then it's channel id
        if method is 'user', then it's username
    """
    # parse the channel URL
    method, id = parse_channel_url(url)
    if method == "channel":
        # if it's a channel ID, then just return it
        return id
    elif method == "user":
        # if it's a user ID, make a request to get the channel ID
        response = get_channel_details(youtube, forUsername=id)
        items = response.get("items")
        if items:
            channel_id = items[0].get("id")
            return channel_id
    elif method == "c":
        # if it's a channel name, search for the channel using the name
        # may be inaccurate
        response = search(youtube, q=id, maxResults=1)
        items = response.get("items")
        if items:
            channel_id = items[0]["snippet"]["channelId"]
            return channel_id
    raise Exception(f"Cannot find ID:{id} with {method} method")


def get_video_id_by_url(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urllib.parse.urlparse(value)
    
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = urllib.parse.parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    
    return None

def extract_playlist_id(playlist_url):
    # Normal playlists start with PL, Mixes start with RD + first video ID,
    # Liked videos start with LL, Uploads start with UU,
    # Favorites lists start with FL
    # Album playlists start with OL
    idregx = re.compile(r'((?:RD|PL|LL|UU|FL|OL)[-_0-9a-zA-Z]+)$')

    playlist_id = None
    if idregx.match(playlist_url):
        playlist_id = playlist_url  # ID of video

    if '://' not in playlist_url:
        playlist_url = '//' + playlist_url
    parsedurl = urlparse(playlist_url)
    if parsedurl.netloc in ('youtube.com', 'www.youtube.com'):
        query = parse_qs(parsedurl.query)
        if 'list' in query and idregx.match(query['list'][0]):
            playlist_id = query['list'][0]
    
    return playlist_id
def songbyid(id):
    meta = sp.track(id)
    name = meta['name']
    artist=meta['artists'][0]['name']
    return {
        'name':name,
        'artists':artist}
def ambum(id):
    ids = []
    item = sp.album(id)
    for itema in item['tracks']['items']:
        ids.append(itema['id'])
    return ids

def playlist(id):
    ids = []
    item = sp.playlist(id)
    for itema in item['tracks']['items']:
        track = itema['track']
        ids.append(track['id'])
    return ids
