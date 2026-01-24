import { Navbar } from "@/components/Navbar";
import CareCalendar from "@/components/CareCalendar";

const CalendarPage = () => {
    return (
        <div className="min-h-screen bg-background">
            <Navbar />
            <main>
                <CareCalendar />
            </main>
        </div>
    );
};

export default CalendarPage;
