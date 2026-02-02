import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, Droplets, FlaskConical, ClipboardCheck } from 'lucide-react';
import { getCalendarEvents, getTodayTasks } from '@/integrations/api';
import { Skeleton } from '@/components/ui/skeleton';

const CareCalendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const { data: schedule, isLoading } = useQuery({
    queryKey: ['care-schedule'],
    queryFn: () => getTodayTasks(),
  });

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  const weekDays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const previousMonth = () =>
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const nextMonth = () =>
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));

  const renderCalendarDays = () => {
    const days = [];
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="h-24 hidden md:block" />);
    }
    for (let day = 1; day <= daysInMonth; day++) {
      const isToday = new Date().getDate() === day && new Date().getMonth() === currentDate.getMonth();

      days.push(
        <div
          key={day}
          className={`min-h-[100px] p-3 glass-card rounded-2xl transition-all hover:bg-white/60 ${isToday ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : ''
            }`}
        >
          <div className={`font-bold text-sm mb-2 ${isToday ? 'text-primary' : 'text-muted-foreground'}`}>
            {day}
          </div>
          {/* Calendar dots logic would go here */}
          <div className="flex gap-1 flex-wrap">
            {isToday && <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />}
          </div>
        </div>
      );
    }
    return days;
  };

  return (
    <div className="container mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-700">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-primary flex items-center gap-2">
            Care Calendar <CalendarIcon className="h-6 w-6" />
          </h1>
          <p className="text-muted-foreground">Keep track of your botanical duties.</p>
        </div>
        <div className="flex items-center gap-4 glass-card px-4 py-2 rounded-2xl">
          <Button variant="ghost" size="icon" onClick={previousMonth} className="hover:bg-primary/10">
            <ChevronLeft size={20} />
          </Button>
          <span className="font-bold text-lg min-w-[140px] text-center">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </span>
          <Button variant="ghost" size="icon" onClick={nextMonth} className="hover:bg-primary/10">
            <ChevronRight size={20} />
          </Button>
        </div>
      </header>

      <div className="grid grid-cols-7 gap-4">
        {weekDays.map((d) => (
          <div key={d} className="text-center font-bold text-xs uppercase tracking-wider text-muted-foreground mb-2">
            {d}
          </div>
        ))}
        {isLoading ? (
          Array(28).fill(0).map((_, i) => <Skeleton key={i} className="h-24 rounded-2xl" />)
        ) : renderCalendarDays()}
      </div>

      <section className="glass-card p-6 rounded-3xl space-y-4">
        <h2 className="text-xl font-bold flex items-center gap-2">
          Upcoming for Today <ClipboardCheck className="h-5 w-5 text-primary" />
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {schedule?.tasks?.map((task: any) => (
            <div key={task.id} className="p-4 rounded-2xl bg-white/40 border border-white/20 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                {task.task_type === 'watering' ? <Droplets className="text-blue-500" /> : <FlaskConical className="text-purple-500" />}
              </div>
              <div>
                <h4 className="font-bold text-sm">{task.title}</h4>
                <p className="text-xs text-muted-foreground">{task.plant_name}</p>
              </div>
            </div>
          ))}
          {(!schedule?.tasks || schedule.tasks.length === 0) && (
            <p className="col-span-full py-8 text-center italic text-muted-foreground">No tasks scheduled for today.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default CareCalendar;
