import React, { useRef, useState, useEffect } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import { Upload, Search, PlayIcon } from "lucide-react";

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

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onloadend = () => {
      setVideoFile({
        file,
        dataUrl: reader.result,
      });
    };
    reader.readAsDataURL(file);
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
      const timeToStart = 7 * 60 + 12.6; // Seek to 7:12.6 only once
      playerRef.current.currentTime(timeToStart);
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

  // Updated handleSubmit with API functionality
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!videoFile || !query) {
      alert("Please upload a video and enter a query");
      return;
    }

    try {
      const formData = new FormData();
      formData.append("video_file", videoFile.file);
      formData.append("query", query);
      // Append additional fields if needed

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
      apiResponse?.answer?.timestampstart &&
        setManualTimestamp(apiResponse.answer.timestampstart);
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
    jumpToTimestamp(parseFloat(apiResponse.answer.timestamp));
  };

  const handleJumpToManualTimestamp = () => {
    const time = parseFloat(manualTimestamp);
    if (isNaN(time) || time < 0) {
      alert("Please enter a valid timestamp (non-negative number).");
      return;
    }
    jumpToTimestamp(time);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white shadow-2xl rounded-2xl w-full max-w-4xl p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center text-blue-800 mb-6">
          Video Timestamp Query
        </h1>

        <div className="space-y-6">
          {/* File Upload */}
          <div className="flex items-center space-x-4">
            <label className="cursor-pointer relative">
              <input
                ref={fileInputRef}
                type="file"
                accept="video/*"
                className="hidden"
                onChange={handleFileUpload}
              />
              <div
                onClick={() => fileInputRef.current.click()}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition flex items-center"
              >
                <Upload className="mr-2" /> Upload Video
              </div>
            </label>
            {videoFile && (
              <span className="text-sm text-gray-600 truncate">
                {videoFile.file.name}
              </span>
            )}
          </div>

          {/* Video Player */}
          {videoFile && (
            <div className="w-full aspect-video bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                className="video-js vjs-default-skin"
                controls
                preload="auto"
                width="100%"
                height="100%"
              />
            </div>
          )}

          {/* Query Input Form */}
          {videoFile && (
            <>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="flex space-x-4">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter your video query"
                    className="flex-grow px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="submit"
                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition flex items-center"
                  >
                    <Search className="mr-2" /> Find Timestamp
                  </button>
                </div>

                {/* API Result Display */}
                {apiResponse && (
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg text-center flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-blue-800">Result</h3>
                      <p className="text-gray-700">
                        {apiResponse.answer?.timestamp
                          ? `Timestamp found: ${apiResponse.answer.timestamp} seconds`
                          : "No timestamp found"}
                      </p>
                    </div>
                    {apiResponse.answer?.timestamp && (
                      <button
                        type="button"
                        onClick={handleJumpToApiTimestamp}
                        className="ml-4 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
                      >
                        Jump
                      </button>
                    )}
                  </div>
                )}
              </form>

              {/* Manual Timestamp Input */}
              <div className="flex space-x-4">
                <input
                  type="number"
                  step="0.01"
                  value={manualTimestamp}
                  onChange={(e) => setManualTimestamp(e.target.value)}
                  placeholder="Enter manual timestamp (seconds)"
                  className="flex-grow px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleJumpToManualTimestamp}
                  className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition flex items-center"
                >
                  <PlayIcon className="mr-2" /> Jump to Time
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoTimestampApp;
