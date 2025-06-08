import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaCode,
  FaRobot,
  FaDatabase,
  FaChartBar,
  FaGlobe,
  FaShieldAlt,
} from "react-icons/fa";

const TopicsPage = () => {
  const navigate = useNavigate();
  const [hoveredTopic, setHoveredTopic] = useState(null);

  const topics = [
    {
      id: "programming",
      title: "Programming",
      icon: <FaCode size={48} />,
      color: "#4f46e5",
      description:
        "Learn coding fundamentals and advanced programming techniques",
    },
    {
      id: "web-development",
      title: "Web Development",
      icon: <FaGlobe size={48} />,
      color: "#8b5cf6",
      description: "Master HTML, CSS, JavaScript and modern web frameworks",
    },
    {
      id: "machine-learning",
      title: "Machine Learning",
      icon: <FaRobot size={48} />,
      color: "#10b981",
      description:
        "Explore AI, neural networks, and machine learning algorithms",
    },
    {
      id: "data-science",
      title: "Data Science",
      icon: <FaDatabase size={48} />,
      color: "#f59e0b",
      description:
        "Master data analysis, visualization, and statistical methods",
    },
    {
      id: "business-intelligence",
      title: "Business Intelligence",
      icon: <FaChartBar size={48} />,
      color: "#ef4444",
      description: "Discover tools and techniques for business data analysis",
    },
    {
      id: "cybersecurity",
      title: "Cybersecurity",
      icon: <FaShieldAlt size={48} />,
      color: "#06b6d4",
      description:
        "Learn network security, ethical hacking, and threat prevention",
    },
  ];

  const handleTopicClick = (topicId) => {
    navigate(`/lectures/${topicId}`);
  };

  return (
    <div className="topics-container">
      <div className="topics-header">
        <h1>Choose a Learning Path</h1>
        <p>Select a topic to explore video lectures and resources</p>
      </div>

      <div className="topics-grid">
        {topics.map((topic) => (
          <div
            key={topic.id}
            className={`topic-card ${
              hoveredTopic === topic.id ? "hovered" : ""
            }`}
            style={{
              borderColor: topic.color,
              boxShadow:
                hoveredTopic === topic.id
                  ? `0 10px 25px ${topic.color}40`
                  : "none",
            }}
            onClick={() => handleTopicClick(topic.id)}
            onMouseEnter={() => setHoveredTopic(topic.id)}
            onMouseLeave={() => setHoveredTopic(null)}
          >
            <div className="topic-icon" style={{ color: topic.color }}>
              {topic.icon}
            </div>
            <div className="topic-content">
              <h2>{topic.title}</h2>
              <p>{topic.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TopicsPage;
