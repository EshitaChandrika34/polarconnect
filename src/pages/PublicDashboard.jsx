import {
	BookOpen,
	FileText,
	Image,
	Info,
	LogOut,
	Search,
	User,
	Video,
} from "lucide-react";

import "./Dashboard.css";

function PublicDashboard() {
	return (
		<div className="dashboard">
			<aside className="sidebar">
				<div className="sidebar-logo">❄️ PolarConnect</div>
				<nav>
					<div className="nav-item active"><BookOpen size={20} />Public home</div>
					<div className="nav-item"><Search size={20} />Explore research</div>
					<div className="nav-item"><FileText size={20} />Research stories</div>
					<div className="nav-item"><Image size={20} />Photo stories</div>
					<div className="nav-item"><Video size={20} />Research videos</div>
					<div className="nav-item"><Info size={20} />About polar science</div>
				</nav>
				<div className="sidebar-bottom">
					<div className="nav-item"><User size={20} />Profile</div>
					<div className="nav-item"><LogOut size={20} />Logout</div>
				</div>
			</aside>

			<main className="dashboard-main">
				<header className="dashboard-header"><div><h1>Polar Science for Everyone</h1><p>Understand the research shaping our frozen planet.</p></div><div className="profile-circle">P</div></header>

				<section className="search-section"><h2>Discover polar research</h2><div className="dashboard-search"><Search size={22} /><input type="text" placeholder="Search glaciers, wildlife, climate research..." /><button>Search</button></div></section>

				<section><h2 className="section-title">Researcher stories</h2><div className="research-grid">
					<div className="research-card"><div className="research-icon">🧊</div><div><span className="tag">Climate</span><h3>Why are polar ice sheets changing?</h3><p>Researchers explain how ice loss is measured and what it means for communities worldwide.</p><button className="view-button">Read story</button></div></div>
					<div className="research-card"><div className="research-icon">🐧</div><div><span className="tag">Wildlife</span><h3>Following Antarctica's penguins</h3><p>Explore the fieldwork and technology scientists use to understand changing habitats.</p><button className="view-button">Read story</button></div></div>
					<div className="research-card"><div className="research-icon">🌊</div><div><span className="tag">Ocean</span><h3>The currents connecting our oceans</h3><p>See how polar oceans influence weather, sea levels, and life far beyond the ice.</p><button className="view-button">Read story</button></div></div>
				</div></section>

				<section className="resource-grid public-resources">
					<div className="resource-card"><Video size={30} /><h3>Watch the latest research</h3><p>Short videos from polar expeditions and laboratories.</p></div>
					<div className="resource-card"><Image size={30} /><h3>See the fieldwork</h3><p>Explore photographs captured by researchers in the polar regions.</p></div>
					<div className="resource-card"><BookOpen size={30} /><h3>Learn the basics</h3><p>Clear explainers for the science behind the headlines.</p></div>
				</section>
			</main>
		</div>
	);
}

export default PublicDashboard;
