import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { User, LogOut, Settings, HelpCircle, ChevronDown, Menu } from "lucide-react";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { useAuth } from "@/hooks/useAuth";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import NotificationCenter from "./NotificationCenter";

export const Navbar = () => {
    const { user, profile, signOut } = useAuth();
    const location = useLocation();
    const navigate = useNavigate();
    const [menuOpen, setMenuOpen] = useState(false);

    const navItems = [
        { label: "Dashboard", path: "/" },
        { label: "AI Assistant", path: "/chat" },
        { label: "Calendar", path: "/calendar" },
        { label: "Explore", path: "/lookup" },
        { label: "For You", path: "/recommendations" },
        { label: "Leaderboard", path: "/leaderboard" },
    ];

    const handleSignOut = async () => {
        await signOut();
        navigate("/auth");
    };

    return (
        <nav className="sticky top-0 z-50 w-full bg-card/95 backdrop-blur-sm border-b border-border">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16 gap-2">
                    <button
                        type="button"
                        onClick={() => setMenuOpen(true)}
                        aria-label="Open menu"
                        className="md:hidden -ml-2 p-2 rounded-lg text-foreground hover:bg-secondary/60 transition-colors"
                    >
                        <Menu size={22} />
                    </button>

                    <Link to="/" className="flex items-center gap-2.5 group shrink-0 max-md:mr-auto">
                        <img
                            src="/logo.png"
                            alt="Flourish"
                            className="w-9 h-9 rounded-full object-cover shadow-sm transition-transform duration-500 ease-out group-hover:scale-105"
                        />
                        <span className="text-xl sm:text-2xl font-serif font-semibold text-primary tracking-tight">
                            Flourish
                        </span>
                    </Link>

                    <div className="hidden md:flex items-center gap-8">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path || (item.path === "/chat" && location.pathname.startsWith("/chat/"));
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    className={`
                                        relative text-sm font-medium tracking-wide py-1 transition-colors duration-200
                                        ${isActive
                                            ? 'text-primary'
                                            : 'text-muted-foreground hover:text-primary'}
                                    `}
                                >
                                    {item.label}
                                    {isActive && (
                                        <span className="absolute -bottom-[21px] left-0 right-0 h-0.5 bg-primary rounded-full" />
                                    )}
                                </Link>
                            );
                        })}
                    </div>

                    <div className="flex items-center gap-3">
                        <NotificationCenter />

                        <DropdownMenu>
                            <DropdownMenuTrigger className="flex items-center gap-2 pl-2 pr-1 py-1 rounded-full border border-border hover:bg-secondary/50 transition-colors outline-none">
                                <div className="w-8 h-8 rounded-full overflow-hidden bg-secondary flex items-center justify-center shrink-0">
                                    {user?.photoURL ? (
                                        <img src={user.photoURL} alt="User Avatar" className="w-full h-full object-cover" />
                                    ) : (
                                        <User size={16} className="text-primary" />
                                    )}
                                </div>
                                <ChevronDown size={14} className="text-muted-foreground hidden sm:block" />
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end" className="w-56">
                                <DropdownMenuLabel>
                                    <p className="font-semibold truncate">{profile?.full_name || user?.displayName || "Botanist"}</p>
                                    <p className="text-xs font-normal text-muted-foreground truncate">{user?.email}</p>
                                </DropdownMenuLabel>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem disabled className="gap-2">
                                    <Settings size={16} /> Settings
                                </DropdownMenuItem>
                                <DropdownMenuItem disabled className="gap-2">
                                    <HelpCircle size={16} /> Help
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem onClick={handleSignOut} className="gap-2 text-destructive focus:text-destructive">
                                    <LogOut size={16} /> Sign Out
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </div>
            </div>

            <Sheet open={menuOpen} onOpenChange={setMenuOpen}>
                <SheetContent side="left" className="w-72 p-0 flex flex-col">
                    <SheetTitle className="sr-only">Navigation menu</SheetTitle>
                    <div className="flex items-center gap-2.5 px-5 h-16 border-b border-border">
                        <img src="/logo.png" alt="" className="w-8 h-8 rounded-full object-cover" />
                        <span className="text-xl font-serif font-semibold text-primary">Flourish</span>
                    </div>
                    <nav aria-label="Mobile" className="flex-1 overflow-y-auto p-3">
                        {navItems.map((item) => {
                            const isActive = location.pathname === item.path || (item.path === "/chat" && location.pathname.startsWith("/chat/"));
                            return (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMenuOpen(false)}
                                    aria-current={isActive ? "page" : undefined}
                                    className={`flex items-center rounded-lg px-4 py-3 text-base font-medium transition-colors ${
                                        isActive ? "bg-primary/10 text-primary" : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
                                    }`}
                                >
                                    {item.label}
                                </Link>
                            );
                        })}
                    </nav>
                    <div className="border-t border-border p-3">
                        <button
                            onClick={() => { setMenuOpen(false); handleSignOut(); }}
                            className="flex w-full items-center gap-2 rounded-lg px-4 py-3 text-base font-medium text-destructive hover:bg-destructive/10 transition-colors"
                        >
                            <LogOut size={18} /> Sign Out
                        </button>
                    </div>
                </SheetContent>
            </Sheet>
        </nav>
    );
};
