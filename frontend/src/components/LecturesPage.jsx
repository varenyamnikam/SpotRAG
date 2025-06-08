import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';
import Sidebar from './Sidebar';
import VideoPlayer from './VideoPlayer';

const LecturesPage = () => {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [selectedVideo, setSelectedVideo] = useState(null);

  const handleVideoSelect = (video) => {
    setSelectedVideo(video);
  };

  const handleBackClick = () => {
    navigate('/');
  };

  return (
    <div className="lectures-container">
      <div className="back-button" onClick={handleBackClick}>
        <FaArrowLeft />
        <span>Back to Topics</span>
      </div>
      
      <div className="lectures-content">
        <div className="sidebar-wrapper">
          <Sidebar topicId={topicId} onVideoSelect={handleVideoSelect} />
        </div>
        
        <div className="video-player-wrapper">
          <VideoPlayer selectedVideo={selectedVideo} />
        </div>
      </div>
    </div>
  );
};

export default LecturesPage;
