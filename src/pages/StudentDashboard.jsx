import {
  Search,
  BookOpen,
  Image,
  FileText,
  Database,
  Bot,
  Bookmark,
  User,
  LogOut
} from "lucide-react";

import "./Dashboard.css";

function StudentDashboard() {
  return (
    <div className="dashboard">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="sidebar-logo">
          ❄️ PolarConnect
        </div>

        <nav>

          <div className="nav-item active">
            <BookOpen size={20} />
            Dashboard
          </div>

          <div className="nav-item">
            <Search size={20} />
            Search Research
          </div>

          <div className="nav-item">
            <FileText size={20} />
            Expedition Reports
          </div>

          <div className="nav-item">
            <BookOpen size={20} />
            Research Papers
          </div>

          <div className="nav-item">
            <Database size={20} />
            Datasets
          </div>

          <div className="nav-item">
            <Image size={20} />
            Media Gallery
          </div>

          <div className="nav-item">
            <Bot size={20} />
            Polar AI
          </div>

          <div className="nav-item">
            <Bookmark size={20} />
            Saved Research
          </div>

        </nav>

        <div className="sidebar-bottom">

          <div className="nav-item">
            <User size={20} />
            Profile
          </div>

          <div className="nav-item">
            <LogOut size={20} />
            Logout
          </div>

        </div>

      </aside>


      {/* Main Content */}
      <main className="dashboard-main">

        {/* Header */}
        <header className="dashboard-header">

          <div>
            <h1>Welcome, Student 👋</h1>
            <p>
              Explore polar science, research and discoveries.
            </p>
          </div>

          <div className="profile-circle">
            S
          </div>

        </header>


        {/* Search */}
        <section className="search-section">

          <h2>Explore Polar Research</h2>

          <div className="dashboard-search">

            <Search size={22} />

            <input
              type="text"
              placeholder="Search Antarctic glaciers, expeditions, climate research..."
            />

            <button>
              Search
            </button>

          </div>

        </section>


        {/* Quick Access */}
        <section>

          <h2 className="section-title">
            Explore Resources
          </h2>

          <div className="resource-grid">

            <div className="resource-card">
              <FileText size={30} />
              <h3>Expedition Reports</h3>
              <p>
                Explore official polar expedition reports.
              </p>
            </div>

            <div className="resource-card">
              <BookOpen size={30} />
              <h3>Research Papers</h3>
              <p>
                Discover scientific research and publications.
              </p>
            </div>

            <div className="resource-card">
              <Database size={30} />
              <h3>Scientific Datasets</h3>
              <p>
                Access polar science datasets.
              </p>
            </div>

            <div className="resource-card">
              <Image size={30} />
              <h3>Media Gallery</h3>
              <p>
                View polar photographs and scientific visuals.
              </p>
            </div>

          </div>

        </section>


        {/* Recent Research This Week */}
        <section>

          <h2 className="section-title">
            Recent Research This Week
          </h2>

          <div className="research-grid">

            <div className="research-card">

              <div className="research-icon">
                ❄️
              </div>

              <div>
                <span className="tag">
                  Antarctica
                </span>

                <h3>
                  Antarctic Glacier Monitoring
                </h3>

                <p>
                  Study of glacier movement and ice mass
                  changes in Antarctica.
                </p>

                <button className="view-button">
                  View Research
                </button>
              </div>

            </div>


            <div className="research-card">

              <div className="research-icon">
                🌊
              </div>

              <div>
                <span className="tag">
                  Arctic
                </span>

                <h3>
                  Arctic Ocean Climate Study
                </h3>

                <p>
                  Analysis of ocean temperature and
                  changing Arctic conditions.
                </p>

                <button className="view-button">
                  View Research
                </button>
              </div>

            </div>


            <div className="research-card">

              <div className="research-icon">
                🧊
              </div>

              <div>
                <span className="tag">
                  Climate
                </span>

                <h3>
                  Polar Ice Sheet Research
                </h3>

                <p>
                  Research on polar ice sheets and
                  climate change.
                </p>

                <button className="view-button">
                  View Research
                </button>

              </div>

            </div>

          </div>

        </section>


        {/* AI Assistant */}
        <section className="ai-section">

          <div className="ai-icon">
            <Bot size={35} />
          </div>

          <div className="ai-content">

            <h2>Ask Polar AI</h2>

            <p>
              Ask questions about polar research and get
              summarized answers with source references.
            </p>

          </div>

          <button className="ai-button">
            Ask AI
          </button>

        </section>

      </main>

    </div>
  );
}

export default StudentDashboard;