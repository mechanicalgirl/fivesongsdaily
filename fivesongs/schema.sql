DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS playlist;
DROP TABLE IF EXISTS song;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE playlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    play_date DATE NOT NULL UNIQUE,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE song (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    artist TEXT,
    title TEXT NOT NULL,
    filepath TEXT NOT NULL,
    duration TEXT,
    album_name TEXT,
    album_art TEXT,
    playlist_id INTEGER,
    created_at DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY(playlist_id) REFERENCES playlist(id)
);

INSERT INTO playlist (play_date) VALUES (CURRENT_DATE);

INSERT INTO song (artist, title, filepath, duration, album_name, album_art, playlist_id) VALUES ('Natasha Blume', 'Black Sea', 'BlackSea-NatashaBlume.mp3', '4:13', 'Natasha Blume', 'BlackSea-NatashaBlume.jpg', 1);
INSERT INTO song (artist, title, filepath, duration, album_name, album_art, playlist_id) VALUES ('Poxy Boggards', 'Nelly the Mermaid', 'NellytheMermaid-PoxyBoggards.mp3', '3:13', 'Anchor Management', 'NellytheMermaid-PoxyBoggards.jpg', 1);
INSERT INTO song (artist, title, filepath, duration, album_name, album_art, playlist_id) VALUES ('This Mortal Coil', 'Song to the Siren', 'SongToTheSiren-ThisMortalCoil.mp3', '3:30', 'It''ll End In Tears', 'SongToTheSiren-ThisMortalCoil.jpg', 1);
INSERT INTO song (artist, title, filepath, duration, album_name, album_art, playlist_id) VALUES ('The Blixunami', 'Splish Splash on Em', 'SplishSplashOnEm-TheBlixunami.mp3', '3:39', '', 'SplishSplashOnEm-TheBlixunami.jpg', 1);
INSERT INTO song (artist, title, filepath, duration, album_name, album_art, playlist_id) VALUES ('Esthero', 'Black Mermaid', 'BlackMermaid-Esthero.mp3', '4:14', 'Everything Is Expensive', 'BlackMermaid-Esthero.jpg', 1);
