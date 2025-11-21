from pydantic import BaseModel
from typing import List, Optional


class ExternalUrls(BaseModel):
    spotify: str


class Device(BaseModel):
    id: Optional[str] = None
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: Optional[int] = None
    supports_volume: bool
    repeat_state: Optional[str] = None
    shuffle_state: Optional[bool] = None


class Context(BaseModel):
    type: str
    href: str
    external_urls: ExternalUrls
    uri: str


class Image(BaseModel):
    url: str
    height: int
    width: int


class Artist(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class Album(BaseModel):
    album_type: str
    total_tracks: int
    available_markets: List[str]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    type: str
    uri: str
    artists: List[Artist]


class ExternalIds(BaseModel):
    isrc: Optional[str] = None


class Track(BaseModel):
    album: Album
    artists: List[Artist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalIds
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    popularity: int
    preview_url: Optional[str] = None
    track_number: int
    type: str
    uri: str
    is_local: bool


class Actions(BaseModel):
    interrupting_playback: Optional[bool] = None
    pausing: Optional[bool] = None
    resuming: Optional[bool] = None
    seeking: Optional[bool] = None
    skipping_next: Optional[bool] = None
    skipping_prev: Optional[bool] = None
    toggling_repeat_context: Optional[bool] = None
    toggling_shuffle: Optional[bool] = None
    toggling_repeat_track: Optional[bool] = None
    transferring_playback: Optional[bool] = None
    disallows: Optional[dict] = None


class CurrentPlaying(BaseModel):
    device: Optional[Device] = None
    context: Optional[Context] = None
    timestamp: int
    progress_ms: Optional[int] = None
    is_playing: bool
    item: Optional[Track] = None
    currently_playing_type: str
    actions: Optional[Actions] = None
