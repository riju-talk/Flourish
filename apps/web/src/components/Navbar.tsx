import { Link, useLocation } from "react-router-dom";
import { Leaf, LayoutDashboard, MessageSquare, Calendar, User, Bell } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

export const Navbar = () => {
    const { user, signOut } = useAuth();
    const location = useLocation();

    const navItems = [
        { icon: <LayoutDashboard size={20} />, label: "Dashboard", path: "/" },
        { icon: <MessageSquare size={20} />, label: "PlantMind AI", path: "/chat" },
        { icon: <Calendar size={20} />, label: "Calendar", path: "/calendar" },
    ];

    return (
        <nav className="sticky top-0 z-50 w-full border-b border-white/20 bg-white/40 backdrop-blur-md px-4 py-3">
            <div className="container mx-auto flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2 group">
                    <div className="w-10 h-10 rounded-2xl vibrant-gradient flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-transform">
                        <Leaf size={24} />
                    </div>
                    <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">
                        Flourish
                    </span>
                </Link>

                {/* Desktop Nav */}
                <div className="hidden md:flex items-center gap-8 font-medium">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`flex items-center gap-2 hover:text-primary transition-colors ${location.pathname === item.path ? 'text-primary' : 'text-muted-foreground'
                                }`}
                        >
                            {item.icon}
                            {item.label}
                        </Link>
                    ))}
                </div>

                <div className="flex items-center gap-4">
                    <button className="relative p-2 rounded-full hover:bg-white/40 transition-colors hidden sm:block">
                        <Bell size={20} className="text-muted-foreground" />
                        <span className="absolute top-2 right-2 w-2 h-2 bg-primary rounded-full border-2 border-white"></span>
                    </button>

                    <div className="flex items-center gap-3 pl-4 border-l border-white/20">
                        <div className="hidden sm:block text-right">
                            <p className="text-sm font-bold truncate max-w-[120px]">{user?.displayName || "Guest"}</p>
                            <button
                                onClick={() => signOut()}
                                className="text-xs text-muted-foreground hover:text-red-500 transition-colors"
                                id="logout_btn"
                            >
                                Sign Out
                            </button>
                        </div>
                        <div className="w-10 h-10 rounded-2xl bg-secondary border-2 border-white overflow-hidden shadow-inner">
                            {user?.photoURL ? (
                                <img src={user.photoURL} alt="User Avatar" />
                            ) : (
                                <div className="w-full h-full flex items-center justify-center text-primary font-bold">
                                    {user?.displayName ? user.displayName[0] : <User size={20} />}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};
