"use client";

import { useRef, useState, useEffect } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import { Upload, Search, PlayIcon } from "lucide-react";
import "./App.css";
import "./index.css";
import "./styles.css";

// IndexedDB Utility Functions
const DATABASE_NAME = "VideoQueryDB";
const STORE_NAME = "videoFiles";

const initIndexedDB = () => {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DATABASE_NAME, 1);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };

    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = (event) => reject(event.target.error);
  });
};

const saveFileToIndexedDB = (file) => {
  return new Promise(async (resolve, reject) => {
    try {
      const db = await initIndexedDB();
      const transaction = db.transaction([STORE_NAME], "readwrite");
      const store = transaction.objectStore(STORE_NAME);

      const fileData = {
        id: "current_video",
        file: file,
        timestamp: Date.now(),
      };

      const request = store.put(fileData);

      request.onsuccess = () => resolve(fileData);
      request.onerror = (event) => reject(event.target.error);
    } catch (error) {
      reject(error);
    }
  });
};

const getFileFromIndexedDB = () => {
  return new Promise(async (resolve, reject) => {
    try {
      const db = await initIndexedDB();
      const transaction = db.transaction([STORE_NAME], "readonly");
      const store = transaction.objectStore(STORE_NAME);

      const request = store.get("current_video");

      request.onsuccess = (event) => {
        resolve(event.target.result ? event.target.result.file : null);
      };

      request.onerror = (event) => reject(event.target.error);
    } catch (error) {
      reject(error);
    }
  });
};

const VideoTimestampApp = () => {
  const [query, setQuery] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [apiResponse, setApiResponse] = useState(null);
  const [manualTimestamp, setManualTimestamp] = useState("");
  const [isReady, setIsReady] = useState(false);

  const videoRef = useRef(null);
  const playerRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
      }
    };
  }, []);

  useEffect(() => {
    // Initialize IndexedDB when component mounts
    initIndexedDB();
  }, []);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      // Save file to IndexedDB
      await saveFileToIndexedDB(file);

      const reader = new FileReader();
      reader.onloadend = () => {
        setVideoFile({
          file,
          dataUrl: reader.result,
        });
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error("Error saving file to IndexedDB:", error);
    }
  };

  useEffect(() => {
    if (!videoFile || !videoRef.current) return;

    // Dispose of the previous player instance if it exists
    if (playerRef.current) {
      playerRef.current.dispose();
    }

    console.log("✅ Initializing Video.js player...");

    // Initialize Video.js only when videoRef is available
    const player = videojs(videoRef.current, {
      controls: true,
      autoplay: false,
      preload: "auto",
      sources: [
        {
          src: videoFile.dataUrl,
          type: videoFile.file.type,
        },
      ],
    });

    playerRef.current = player;

    // Seek to a specific timestamp once metadata is loaded
    player.on("loadedmetadata", () => {
      console.log("📍 Video metadata loaded, seeking...");
      const timeToStart = 7 * 60 + 12.6;
      player.currentTime(timeToStart);
      player.play();
    });

    return () => {
      if (playerRef.current) {
        console.log("🗑️ Disposing Video.js player...");
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [videoFile]);

  useEffect(() => {
    if (isReady && playerRef.current) {
      // Additional setup if needed
    }
  }, [isReady]);

  const jumpToTimestamp = (timestamp) => {
    if (playerRef.current) {
      try {
        playerRef.current.currentTime(timestamp);
        playerRef.current.play();
      } catch (error) {
        console.error("Error jumping to timestamp:", error);
        alert("Failed to jump to the specified timestamp.");
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Retrieve file from IndexedDB
      const storedFile = await getFileFromIndexedDB();

      if (!storedFile || !query) {
        alert("Please upload a video and enter a query");
        return;
      }

      const formData = new FormData();
      formData.append("video_file", storedFile);
      formData.append("query", query);

      const response = await fetch(
        "http://127.0.0.1:8000/process_video_and_find_answer/",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      setApiResponse(result);

      if (result?.answer?.timestampstart) {
        setManualTimestamp(result.answer.timestampstart);
      }
    } catch (error) {
      console.error("Error processing video:", error);
      alert(`Error processing video: ${error.message}`);
    }
  };

  const handleJumpToApiTimestamp = () => {
    if (!apiResponse?.answer?.timestamp) {
      alert("No timestamp available from API.");
      return;
    }
    jumpToTimestamp(Number.parseFloat(apiResponse.answer.timestamp));
  };

  const handleJumpToManualTimestamp = () => {
    const time = Number.parseFloat(manualTimestamp);
    if (isNaN(time) || time < 0) {
      alert("Please enter a valid timestamp (non-negative number).");
      return;
    }
    jumpToTimestamp(time);
  };

  return (
    <div className="app-container">
      <div className="card">
        <div className="header">
          <h1>Video Timestamp Finder</h1>
          <p>Upload a video and find specific moments with ease</p>
        </div>

        <div className="content">
          {/* File Upload */}
          <div className="file-upload">
            <label>Upload Video</label>
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                onChange={handleFileUpload}
              />
              <button onClick={() => fileInputRef.current.click()}>
                Select Video
              </button>
              {videoFile && (
                <span className="file-name">{videoFile.file.name}</span>
              )}
            </div>
          </div>

          {/* Video Player */}
          {videoFile && (
            <div className="video-container">
              <video
                ref={videoRef}
                className="video-js vjs-default-skin"
                controls
                preload="auto"
              />
            </div>
          )}

          {/* Query Input */}
          {videoFile && (
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="What moment are you looking for?"
                  className="input-field"
                />
                <button type="submit" className="button">
                  Find Moment
                </button>
              </div>

              {/* API Response */}
              {apiResponse && (
                <div className="response-box">
                  <p>
                    {apiResponse.answer?.timestamp
                      ? `Found at ${apiResponse.answer.timestamp} seconds`
                      : "No match found"}
                  </p>
                  {apiResponse.answer?.timestamp && (
                    <button
                      onClick={handleJumpToApiTimestamp}
                      className="jump-button"
                    >
                      Jump
                    </button>
                  )}
                </div>
              )}

              {/* Manual Timestamp */}
              <div className="input-group">
                <input
                  type="number"
                  value={manualTimestamp}
                  onChange={(e) => setManualTimestamp(e.target.value)}
                  placeholder="Enter timestamp"
                  className="input-field"
                />
                <button
                  onClick={handleJumpToManualTimestamp}
                  className="jump-button"
                >
                  Jump
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoTimestampApp;
