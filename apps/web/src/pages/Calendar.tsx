import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";
import CareCalendar from "@/components/CareCalendar";

const CalendarPage = () => {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <Seo title="Calendar" description="See every upcoming watering, fertilizing, and health check for your garden." />
            <Navbar />
            <main className="flex-1">
                <CareCalendar />
            </main>
            <Footer />
        </div>
    );
};

export default CalendarPage;
