import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import CareCalendar from "@/components/CareCalendar";

const CalendarPage = () => {
    return (
        <div className="min-h-screen bg-background flex flex-col">
            <Navbar />
            <main className="flex-1">
                <CareCalendar />
            </main>
            <Footer />
        </div>
    );
};

export default CalendarPage;
