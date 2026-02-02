import { Link, useLocation } from "react-router-dom";
import { Leaf, LayoutDashboard, MessageSquare, Calendar, User, Search, FileText, Trophy } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import NotificationCenter from "./NotificationCenter";

export const Navbar = () => {
    const { user, signOut } = useAuth();
    const location = useLocation();

    const navItems = [
        { icon: <LayoutDashboard size={18} />, label: "Dashboard", path: "/" },
        { icon: <MessageSquare size={18} />, label: "AI Chat", path: "/chat" },
        { icon: <Search size={18} />, label: "Plant Lookup", path: "/lookup" },
        { icon: <Calendar size={18} />, label: "Calendar", path: "/calendar" },
        { icon: <FileText size={18} />, label: "Documents", path: "/documents" },
        { icon: <Trophy size={18} />, label: "Leaderboard", path: "/leaderboard" },
    ];

    return (
        <nav className="sticky top-4 z-50 w-[95%] mx-auto glass-card border-none rounded-full px-6 py-3 mt-4">
            <div className="flex items-center justify-between">
                <Link to="/" className="flex items-center gap-3 group">
                    <div className="w-10 h-10 rounded-full vibrant-gradient flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform">
                        <Leaf size={20} className="fill-current" />
                    </div>
                    <span className="text-xl font-bold text-gradient hidden sm:block">
                        Flourish
                    </span>
                </Link>

                {/* Desktop Nav */}
                <div className="hidden md:flex items-center gap-1 bg-secondary/30 rounded-full p-1 border border-white/10">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`
                                    flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300
                                    ${isActive
                                        ? 'bg-white shadow-sm text-primary'
                                        : 'text-muted-foreground hover:text-primary hover:bg-white/50'}
                                `}
                            >
                                {item.icon}
                                {item.label}
                            </Link>
                        );
                    })}
                </div>

                <div className="flex items-center gap-4">
                    <NotificationCenter />

                    <div className="flex items-center gap-3 pl-4 border-l border-border/50">
                        <div className="w-9 h-9 rounded-full ring-2 ring-white/50 ring-offset-2 ring-offset-transparent overflow-hidden shadow-sm">
                            {user?.photoURL ? (
                                <img src={user.photoURL} alt="User Avatar" className="w-full h-full object-cover" />
                            ) : (
                                <div className="w-full h-full bg-secondary flex items-center justify-center text-primary font-bold">
                                    {user?.displayName ? user.displayName[0] : <User size={18} />}
                                </div>
                            )}
                        </div>
                        <button
                            onClick={() => signOut()}
                            className="text-xs font-semibold text-muted-foreground hover:text-destructive transition-colors hidden sm:block"
                        >
                            Sign Out
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
};
