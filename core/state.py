"""Process-wide singletons shared by every browser session."""
import streamlit as st

from .config import DATA_DIR
from .store import ProfileStore, RoomHub


@st.cache_resource
def get_hub() -> RoomHub:
    hub = RoomHub(DATA_DIR / "rooms.json")
    hub.cleanup()
    return hub


@st.cache_resource
def get_profile() -> ProfileStore:
    return ProfileStore(DATA_DIR / "profile.json")
