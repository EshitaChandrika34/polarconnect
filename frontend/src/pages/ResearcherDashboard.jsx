import {
	BarChart3,
	BookOpen,
	FileText,
	Image,
	LayoutDashboard,
	LogOut,
	Plus,
	User,
	Video,
} from "lucide-react";

import "./Dashboard.css";

function ResearcherDashboard() {
	return (
		<div className="dashboard">
			<aside className="sidebar">
				<div className="sidebar-logo">❄️ PolarConnect</div>
				<nav>
					<div className="nav-item active"><LayoutDashboard size={20} />Dashboard</div>
					<div className="nav-item"><FileText size={20} />My Research</div>
					<div className="nav-item"><Image size={20} />Images</div>
					<div className="nav-item"><Video size={20} />Videos</div>
					<div className="nav-item"><BookOpen size={20} />Research Topics</div>
					<div className="nav-item"><BarChart3 size={20} />Analytics</div>
				</nav>
				<div className="sidebar-bottom">
					<div className="nav-item"><User size={20} />Profile</div>
					<div className="nav-item"><LogOut size={20} />Logout</div>
				</div>
			</aside>

			<main className="dashboard-main">
				<header className="dashboard-header">
					<div><h1>Researcher Workspace</h1><p>Manage your polar research and share discoveries with the public.</p></div>
					<div className="profile-circle">R</div>
				</header>

				<section className="stats-grid">
					<div className="stat-card"><FileText size={24} /><strong>24</strong><span>Research documents</span></div>
					<div className="stat-card"><Image size={24} /><strong>186</strong><span>Research images</span></div>
					<div className="stat-card"><Video size={24} /><strong>18</strong><span>Research videos</span></div>
					<div className="stat-card"><BookOpen size={24} /><strong>9</strong><span>Research topics</span></div>
				</section>

				<section className="dashboard-section-heading">
					<div><h2 className="section-title">Research collection</h2><p>Keep your latest work organized and ready to publish.</p></div>
					<button className="primary-action"><Plus size={18} />Add research</button>
				</section>

				<section className="research-grid">
					<div className="research-card"><div className="research-icon">🧊</div><div><span className="tag">In review</span><h3>Arctic Ice Sheet Monitoring</h3><p>Satellite observations and field measurements tracking seasonal ice loss.</p><button className="view-button">Open document</button></div></div>
					<div className="research-card"><div className="research-icon">🌊</div><div><span className="tag">Published</span><h3>Southern Ocean Currents</h3><p>New findings about ocean circulation and its climate impact.</p><button className="view-button">View publication</button></div></div>
					<div className="research-card"><div className="research-icon">🐋</div><div><span className="tag">Draft</span><h3>Polar Wildlife Census</h3><p>Visual records and population data from the latest expedition.</p><button className="view-button">Continue editing</button></div></div>
				</section>

				<section className="ai-section"><div className="ai-icon"><BarChart3 size={35} /></div><div className="ai-content"><h2>Research impact</h2><p>Your published work reached 4,280 public readers this month.</p></div><button className="ai-button">View analytics</button></section>
			</main>
		</div>
	);
}

export default ResearcherDashboard;
