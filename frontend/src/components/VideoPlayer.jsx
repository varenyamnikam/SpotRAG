import { useState, useEffect } from "react";
import {
  FaThumbsUp,
  FaThumbsDown,
  FaShare,
  FaDownload,
  FaEllipsisH,
  FaRegBell,
  FaSearch,
} from "react-icons/fa";

// Backend API URL
const YOUTUBE_API_URL = "http://127.0.0.1:8000/process_youtube_video/";

// Mock data for comments
const COMMENTS = [
  {
    id: 1,
    user: {
      name: "Alex Johnson",
      avatar: "https://randomuser.me/api/portraits/men/32.jpg",
    },
    text: "This video was incredibly helpful! I've been struggling with this concept for weeks and now it finally makes sense.",
    likes: 124,
    time: "2 weeks ago",
    replies: [
      {
        id: 101,
        user: {
          name: "Sarah Miller",
          avatar: "https://randomuser.me/api/portraits/women/44.jpg",
        },
        text: "I agree! The explanation at 3:42 was particularly clear.",
        likes: 18,
        time: "1 week ago",
      },
    ],
  },
  {
    id: 2,
    user: {
      name: "Michael Chen",
      avatar: "https://randomuser.me/api/portraits/men/67.jpg",
    },
    text: "Great content as always. Would love to see a follow-up video on advanced techniques!",
    likes: 89,
    time: "3 days ago",
    replies: [],
  },
  {
    id: 3,
    user: {
      name: "Emily Rodriguez",
      avatar: "https://randomuser.me/api/portraits/women/28.jpg",
    },
    text: "I've watched this three times now and learn something new each time. The examples are so practical.",
    likes: 56,
    time: "5 days ago",
    replies: [],
  },
  {
    id: 4,
    user: {
      name: "David Wilson",
      avatar: "https://randomuser.me/api/portraits/men/52.jpg",
    },
    text: "Question: Does this approach work for larger datasets as well? I'm working with millions of records.",
    likes: 12,
    time: "1 day ago",
    replies: [
      {
        id: 102,
        user: {
          name: "Channel Owner",
          avatar: "https://randomuser.me/api/portraits/men/1.jpg",
          isVerified: true,
        },
        text: "Yes, it scales well! Check out my other video on optimization techniques for large datasets.",
        likes: 34,
        time: "1 day ago",
      },
    ],
  },
];

// Mock video metadata generator
const generateVideoMetadata = (video) => {
  const viewCount = Math.floor(Math.random() * 900000) + 100000;
  const formattedViews =
    viewCount > 1000000
      ? `${(viewCount / 1000000).toFixed(1)}M`
      : `${Math.floor(viewCount / 1000)}K`;

  const likes = Math.floor(viewCount * (Math.random() * 0.05 + 0.02));
  const formattedLikes =
    likes > 1000 ? `${(likes / 1000).toFixed(1)}K` : likes.toString();

  const uploadDate = new Date();
  uploadDate.setDate(uploadDate.getDate() - Math.floor(Math.random() * 365));

  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const formattedDate = `${
    months[uploadDate.getMonth()]
  } ${uploadDate.getDate()}, ${uploadDate.getFullYear()}`;

  return {
    views: formattedViews,
    likes: formattedLikes,
    uploadDate: formattedDate,
    channelName: "EduTech Academy",
    channelAvatar: "https://randomuser.me/api/portraits/men/1.jpg",
    subscribers: "1.2M",
    isSubscribed: Math.random() > 0.5,
    description: `In this comprehensive tutorial, we explore ${
      video?.title || "advanced concepts"
    } in detail.

This video covers:
• Core principles and fundamentals
• Practical examples and use cases
• Common pitfalls and how to avoid them
• Advanced techniques for experienced users

📚 Resources mentioned in this video:
- Documentation: https://docs.example.com
- GitHub repository: https://github.com/example/repo
- Practice exercises: https://exercises.example.com

🔔 Subscribe for weekly tutorials and updates!

#Tutorial #Learning #Education`,
  };
};

const VideoPlayer = ({ selectedVideo }) => {
  const [videoMetadata, setVideoMetadata] = useState(null);
  const [comments, setComments] = useState([]);
  const [showAllDescription, setShowAllDescription] = useState(false);
  const [query, setQuery] = useState("");
  const [apiResponse, setApiResponse] = useState(null);
  const [manualTimestamp, setManualTimestamp] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  useEffect(() => {
    if (selectedVideo) {
      // Generate mock metadata for the selected video
      setVideoMetadata(generateVideoMetadata(selectedVideo));
      // Set mock comments
      setComments(COMMENTS);
    }
  }, [selectedVideo]);

  // API call for query using YouTube URL
  const handleQuerySubmit = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      alert("Please enter a query");
      return;
    }

    if (!selectedVideo || !selectedVideo.youtubeId) {
      alert("No video selected");
      return;
    }

    setIsSearching(true);
    setUploadProgress(0);

    try {
      const youtubeUrl = `https://www.youtube.com/watch?v=${selectedVideo.youtubeId}`;

      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          const newProgress = prev + 5;
          return newProgress > 90 ? 90 : newProgress;
        });
      }, 1000);

      // Make API request to the YouTube endpoint
      const response = await fetch(YOUTUBE_API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          youtube_url: youtubeUrl,
          query: query,
        }),
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error: ${response.status} ${errorText}`);
      }

      const result = await response.json();
      setApiResponse(result);

      // Update video metadata if available
      if (result.video_info) {
        const updatedMetadata = {
          ...videoMetadata,
          views: `${Math.floor(Math.random() * 500) + 100}K`,
          likes: `${Math.floor(Math.random() * 50) + 10}K`,
          uploadDate: new Date().toLocaleDateString(),
          channelName: result.video_info.author,
          subscribers: "1.2M",
          description: `${result.video_info.title}\n\nThis video is ${
            result.video_info.length_seconds
          } seconds long.\n\n${videoMetadata?.description || ""}`,
        };
        setVideoMetadata(updatedMetadata);
      }

      if (result?.answer?.timestampstart) {
        setManualTimestamp(result.answer.timestampstart.toString());
      } else if (result?.answer?.timestamp) {
        // Handle different timestamp formats
        const timestamp =
          typeof result.answer.timestamp === "string"
            ? parseFloat(result.answer.timestamp.split(" - ")[0])
            : result.answer.timestamp;
        setManualTimestamp(timestamp.toString());
      }

      setIsSearching(false);
    } catch (error) {
      console.error("Error submitting query:", error);
      alert(`Error: ${error.message}`);
      setIsSearching(false);
    }
  };

  const handleJumpToTimestamp = () => {
    const time = Number.parseFloat(manualTimestamp);
    if (isNaN(time) || time < 0) {
      alert("Please enter a valid timestamp (non-negative number).");
      return;
    }

    // In a real implementation with YouTube iframe API, we would use:
    // player.seekTo(time, true);

    // For now, we'll use postMessage to control the iframe
    const iframe = document.querySelector(".youtube-player iframe");
    if (iframe) {
      iframe.contentWindow.postMessage(
        JSON.stringify({
          event: "command",
          func: "seekTo",
          args: [time, true],
        }),
        "*"
      );
    }
  };

  const formatDescription = (text) => {
    if (!text) return "";

    // Split by newlines and process each line
    const lines = text.split("\n");

    return lines.map((line, index) => {
      // Convert URLs to links
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const processedLine = line.replace(
        urlRegex,
        '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
      );

      // Add line breaks
      return (
        <p key={index} dangerouslySetInnerHTML={{ __html: processedLine }} />
      );
    });
  };

  if (!selectedVideo) {
    return (
      <div className="video-player-container">
        <div className="video-placeholder">
          <h2>Select a video from the sidebar to start watching</h2>
        </div>
      </div>
    );
  }

  return (
    <div className="video-player-container">
      {/* Video Player */}
      <div className="youtube-player">
        <iframe
          width="100%"
          height="100%"
          src={`https://www.youtube.com/embed/${selectedVideo.youtubeId}?enablejsapi=1`}
          title={selectedVideo.title}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        ></iframe>
      </div>

      {/* Video Title and Actions */}
      <div className="video-title-section">
        <h1>{selectedVideo.title}</h1>
      </div>

      {/* Video Info Banner */}
      <div className="video-info-banner">
        <p>Enter your query below to find specific moments in this video</p>
      </div>

      {/* Query Search Box */}
      <div className="query-search-box">
        <form onSubmit={handleQuerySubmit}>
          <div className="query-input-group">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What moment are you looking for in this video?"
              className="query-input"
            />
            <button
              type="submit"
              className="query-button"
              disabled={isSearching}
            >
              {isSearching ? "Searching..." : "Find Moment"}
            </button>
          </div>

          {isSearching && (
            <div className="upload-progress">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <span>
                {uploadProgress}% - Processing video and finding answer...
              </span>
            </div>
          )}

          {apiResponse && (
            <div className="query-response">
              <p>
                {apiResponse.answer?.text ||
                  `Found at ${
                    apiResponse.answer?.timestamp ||
                    apiResponse.answer?.timestampstart
                  } seconds`}
              </p>
              <button onClick={handleJumpToTimestamp} className="jump-button">
                Jump to Timestamp
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Video Stats and Actions */}
      <div className="video-stats-section">
        <div className="video-stats">
          <span className="views">{videoMetadata?.views || "0"} views</span>
          <span className="upload-date">
            {videoMetadata?.uploadDate || "Unknown date"}
          </span>
        </div>

        <div className="video-actions">
          <button className="action-button">
            <FaThumbsUp />
            <span>{videoMetadata?.likes || "0"}</span>
          </button>
          <button className="action-button">
            <FaThumbsDown />
            <span>Dislike</span>
          </button>
          <button className="action-button">
            <FaShare />
            <span>Share</span>
          </button>
          <button className="action-button">
            <FaDownload />
            <span>Download</span>
          </button>
          <button className="action-button">
            <FaEllipsisH />
          </button>
        </div>
      </div>

      {/* Channel Info */}
      <div className="channel-section">
        <div className="channel-info">
          <img
            src={videoMetadata?.channelAvatar}
            alt={videoMetadata?.channelName}
            className="channel-avatar"
          />
          <div className="channel-details">
            <h3>{videoMetadata?.channelName || "Channel Name"}</h3>
            <p>{videoMetadata?.subscribers || "0"} subscribers</p>
          </div>
        </div>

        <button
          className={`subscribe-button ${
            videoMetadata?.isSubscribed ? "subscribed" : ""
          }`}
        >
          {videoMetadata?.isSubscribed ? (
            <>
              <FaRegBell />
              <span>Subscribed</span>
            </>
          ) : (
            <span>Subscribe</span>
          )}
        </button>
      </div>

      {/* Description */}
      <div className="video-description">
        <div
          className={`description-text ${showAllDescription ? "expanded" : ""}`}
        >
          {formatDescription(videoMetadata?.description)}
        </div>
        <button
          className="show-more-button"
          onClick={() => setShowAllDescription(!showAllDescription)}
        >
          {showAllDescription ? "Show less" : "Show more"}
        </button>
      </div>

      {/* Comments Section */}
      <div className="comments-section">
        <div className="comments-header">
          <h3>{comments.length} Comments</h3>
          <div className="comments-sort">
            <FaSearch />
            <span>Sort by</span>
          </div>
        </div>

        {/* Comment Input */}
        <div className="comment-input-container">
          <img
            src="https://randomuser.me/api/portraits/men/85.jpg"
            alt="Your Avatar"
            className="user-avatar"
          />
          <input
            type="text"
            placeholder="Add a comment..."
            className="comment-input"
          />
        </div>

        {/* Comments List */}
        <div className="comments-list">
          {comments.map((comment) => (
            <div key={comment.id} className="comment">
              <img
                src={comment.user.avatar}
                alt={comment.user.name}
                className="comment-avatar"
              />
              <div className="comment-content">
                <div className="comment-header">
                  <span className="comment-author">{comment.user.name}</span>
                  <span className="comment-time">{comment.time}</span>
                </div>
                <p className="comment-text">{comment.text}</p>
                <div className="comment-actions">
                  <button className="comment-action">
                    <FaThumbsUp />
                    <span>{comment.likes}</span>
                  </button>
                  <button className="comment-action">
                    <FaThumbsDown />
                  </button>
                  <button className="comment-action">Reply</button>
                </div>

                {/* Replies */}
                {comment.replies.length > 0 && (
                  <div className="comment-replies">
                    {comment.replies.map((reply) => (
                      <div key={reply.id} className="comment reply">
                        <img
                          src={reply.user.avatar}
                          alt={reply.user.name}
                          className="comment-avatar"
                        />
                        <div className="comment-content">
                          <div className="comment-header">
                            <span className="comment-author">
                              {reply.user.name}
                              {reply.user.isVerified && (
                                <span className="verified-badge">✓</span>
                              )}
                            </span>
                            <span className="comment-time">{reply.time}</span>
                          </div>
                          <p className="comment-text">{reply.text}</p>
                          <div className="comment-actions">
                            <button className="comment-action">
                              <FaThumbsUp />
                              <span>{reply.likes}</span>
                            </button>
                            <button className="comment-action">
                              <FaThumbsDown />
                            </button>
                            <button className="comment-action">Reply</button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
