import { useState } from "react";
import { FaChevronDown, FaChevronRight, FaVideo } from "react-icons/fa";

const Sidebar = ({ topicId, onVideoSelect }) => {
  const [expandedTopics, setExpandedTopics] = useState([]);

  // Mock data for topics and videos
  const topics = {
    programming: [
      {
        id: "topic1",
        title: "JavaScript Fundamentals",
        videos: [
          {
            id: "video1",
            title: "Variables and Data Types",
            youtubeId: "DHjqpvDnNGE",
          },
          {
            id: "video2",
            title: "Functions and Scope",
            youtubeId: "xUI5Tsl2JpY",
          },
          {
            id: "video3",
            title: "Objects and Arrays",
            youtubeId: "HB1ZC7czKRs",
          },
        ],
      },
      {
        id: "topic2",
        title: "React Basics",
        videos: [
          {
            id: "video4",
            title: "Components and Props",
            youtubeId: "FJDVKeh7RJI",
          },
          {
            id: "video5",
            title: "State and Lifecycle",
            youtubeId: "qh3dYM6Keuw",
          },
          {
            id: "video6",
            title: "Hooks Introduction",
            youtubeId: "TNhaISOUy6Q",
          },
        ],
      },
      {
        id: "topic3",
        title: "Advanced JavaScript",
        videos: [
          {
            id: "video7",
            title: "Promises and Async/Await",
            youtubeId: "li7FzDHYZpc",
          },
          {
            id: "video8",
            title: "Closures and Prototypes",
            youtubeId: "HcW5-P2SNec",
          },
          { id: "video9", title: "ES6+ Features", youtubeId: "NCwa_xi0Uuc" },
        ],
      },
    ],
    "web-development": [
      {
        id: "topic1",
        title: "HTML & CSS Basics",
        videos: [
          {
            id: "video1",
            title: "HTML Structure and Elements",
            youtubeId: "UB1O30fR-EE",
          },
          {
            id: "video2",
            title: "CSS Styling Fundamentals",
            youtubeId: "yfoY53QXEnI",
          },
          {
            id: "video3",
            title: "Responsive Design",
            youtubeId: "srvUrASNj0s",
          },
        ],
      },
      {
        id: "topic2",
        title: "Frontend Frameworks",
        videos: [
          {
            id: "video4",
            title: "Introduction to React",
            youtubeId: "Tn6-PIqc4UM",
          },
          {
            id: "video5",
            title: "Vue.js Essentials",
            youtubeId: "qZXt1Aom3Cs",
          },
          {
            id: "video6",
            title: "Angular Fundamentals",
            youtubeId: "k5E2AVpwsko",
          },
        ],
      },
      {
        id: "topic3",
        title: "Backend Development",
        videos: [
          { id: "video7", title: "Node.js Basics", youtubeId: "TlB_eWDSMt4" },
          {
            id: "video8",
            title: "RESTful API Design",
            youtubeId: "rtWH70_MMHM",
          },
          {
            id: "video9",
            title: "Database Integration",
            youtubeId: "Cz3WcZLRaWc",
          },
        ],
      },
    ],
    "machine-learning": [
      {
        id: "topic1",
        title: "ML Fundamentals",
        videos: [
          {
            id: "video1",
            title: "Introduction to ML",
            youtubeId: "ukzFI9rgwfU",
          },
          {
            id: "video2",
            title: "Supervised Learning",
            youtubeId: "bQI5uDxrFfA",
          },
          {
            id: "video3",
            title: "Unsupervised Learning",
            youtubeId: "IUn8k5zSI6g",
          },
        ],
      },
      {
        id: "topic2",
        title: "Neural Networks",
        videos: [
          {
            id: "video4",
            title: "Perceptrons and Layers",
            youtubeId: "aircAruvnKk",
          },
          { id: "video5", title: "Backpropagation", youtubeId: "Ilg3gGewQ5U" },
          { id: "video6", title: "CNN Architecture", youtubeId: "ArPaAX_PhIs" },
        ],
      },
      {
        id: "topic3",
        title: "Deep Learning",
        videos: [
          { id: "video7", title: "RNNs and LSTMs", youtubeId: "SEnXr6v2ifU" },
          { id: "video8", title: "Transformers", youtubeId: "TQQlZhbC5ps" },
          { id: "video9", title: "GANs", youtubeId: "Sw9r8CL98N0" },
        ],
      },
    ],
    "data-science": [
      {
        id: "topic1",
        title: "Data Analysis",
        videos: [
          { id: "video1", title: "Pandas Basics", youtubeId: "vmEHCJofslg" },
          { id: "video2", title: "Data Cleaning", youtubeId: "bDhvCp3_lYw" },
          {
            id: "video3",
            title: "Exploratory Analysis",
            youtubeId: "xi0vhXFPegw",
          },
        ],
      },
      {
        id: "topic2",
        title: "Visualization",
        videos: [
          {
            id: "video4",
            title: "Matplotlib and Seaborn",
            youtubeId: "DAQNHzOcO5A",
          },
          {
            id: "video5",
            title: "Interactive Visualizations",
            youtubeId: "vTingdk_a_Q",
          },
          {
            id: "video6",
            title: "Dashboard Creation",
            youtubeId: "nus1VbRjW9w",
          },
        ],
      },
      {
        id: "topic3",
        title: "Statistics",
        videos: [
          {
            id: "video7",
            title: "Descriptive Statistics",
            youtubeId: "SzZ6GpcfoQY",
          },
          {
            id: "video8",
            title: "Hypothesis Testing",
            youtubeId: "0oc49DyA3hU",
          },
          {
            id: "video9",
            title: "Regression Analysis",
            youtubeId: "PaFPbb66DxQ",
          },
        ],
      },
    ],
    "business-intelligence": [
      {
        id: "topic1",
        title: "BI Fundamentals",
        videos: [
          {
            id: "video1",
            title: "Introduction to BI",
            youtubeId: "KFgP9Jk8jkE",
          },
          { id: "video2", title: "Data Warehousing", youtubeId: "J326LIUrZM8" },
          { id: "video3", title: "ETL Processes", youtubeId: "OW5AkILhV3Q" },
        ],
      },
      {
        id: "topic2",
        title: "BI Tools",
        videos: [
          { id: "video4", title: "Power BI Basics", youtubeId: "TmhQCQr_DCA" },
          {
            id: "video5",
            title: "Tableau Fundamentals",
            youtubeId: "jEgVto5QME8",
          },
          { id: "video6", title: "SQL for BI", youtubeId: "kbKty5ZVKMY" },
        ],
      },
      {
        id: "topic3",
        title: "Advanced BI",
        videos: [
          { id: "video7", title: "KPIs and Metrics", youtubeId: "qoXM9U_j_Xc" },
          {
            id: "video8",
            title: "Predictive Analytics",
            youtubeId: "Yk0LpFMGBe4",
          },
          { id: "video9", title: "BI Strategy", youtubeId: "hnVdJzZZzL4" },
        ],
      },
    ],
    cybersecurity: [
      {
        id: "topic1",
        title: "Security Fundamentals",
        videos: [
          {
            id: "video1",
            title: "Introduction to Cybersecurity",
            youtubeId: "3UxObo7GlL0",
          },
          {
            id: "video2",
            title: "Network Security Basics",
            youtubeId: "E03gh1huvW4",
          },
          {
            id: "video3",
            title: "Cryptography Essentials",
            youtubeId: "jhXCTbFnK8o",
          },
        ],
      },
      {
        id: "topic2",
        title: "Ethical Hacking",
        videos: [
          {
            id: "video4",
            title: "Penetration Testing",
            youtubeId: "3Kq1MIfTWCE",
          },
          {
            id: "video5",
            title: "Vulnerability Assessment",
            youtubeId: "ycwWkuMCyQw",
          },
          {
            id: "video6",
            title: "Social Engineering",
            youtubeId: "Vo1urF6S4Bc",
          },
        ],
      },
      {
        id: "topic3",
        title: "Security Operations",
        videos: [
          {
            id: "video7",
            title: "Incident Response",
            youtubeId: "Dk-ZqQ-bfy4",
          },
          {
            id: "video8",
            title: "Threat Intelligence",
            youtubeId: "qwA6MmbeQNo",
          },
          {
            id: "video9",
            title: "Security Monitoring",
            youtubeId: "rvKQtqMrNLw",
          },
        ],
      },
    ],
  };

  const currentTopics = topics[topicId] || [];

  const toggleTopic = (topicId) => {
    if (expandedTopics.includes(topicId)) {
      setExpandedTopics(expandedTopics.filter((id) => id !== topicId));
    } else {
      setExpandedTopics([...expandedTopics, topicId]);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>
          {topicId.charAt(0).toUpperCase() + topicId.slice(1).replace("-", " ")}
        </h2>
        <p>Course Content</p>
      </div>

      <div className="sidebar-content">
        {currentTopics.map((topic) => (
          <div key={topic.id} className="topic-accordion">
            <div className="topic-header" onClick={() => toggleTopic(topic.id)}>
              {expandedTopics.includes(topic.id) ? (
                <FaChevronDown className="accordion-icon" />
              ) : (
                <FaChevronRight className="accordion-icon" />
              )}
              <span>{topic.title}</span>
            </div>

            {expandedTopics.includes(topic.id) && (
              <div className="video-list">
                {topic.videos.map((video) => (
                  <div
                    key={video.id}
                    className="video-item"
                    onClick={() => onVideoSelect(video)}
                  >
                    <FaVideo className="video-icon" />
                    <span>{video.title}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
