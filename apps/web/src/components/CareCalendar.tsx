import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Droplets, FlaskConical, ClipboardCheck } from 'lucide-react';
import { getAllUpcomingTasks, getPlants } from '@/integrations/api';
import { Skeleton } from '@/components/ui/skeleton';

const TASK_STYLE: Record<string, { dot: string; icon: React.ReactNode; label: string }> = {
  watering: { dot: 'bg-blue-500', icon: <Droplets size={14} className="text-blue-500" />, label: 'Watering' },
  fertilizing: { dot: 'bg-purple-500', icon: <FlaskConical size={14} className="text-purple-500" />, label: 'Fertilizing' },
};

const dateKey = (d: Date) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;

const taskDateKey = (task: any): string | null => {
  const raw = task.due_date;
  if (!raw) return null;
  const parsed = new Date(raw);
  if (isNaN(parsed.getTime())) return null;
  return dateKey(parsed);
};

const CareCalendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());

  const { data: tasks, isLoading: tasksLoading } = useQuery({
    queryKey: ['upcoming-tasks'],
    queryFn: getAllUpcomingTasks,
  });

  const { data: plants } = useQuery({
    queryKey: ['plants'],
    queryFn: getPlants,
  });

  const plantNameById = useMemo(() => {
    const map: Record<string, string> = {};
    (plants || []).forEach((p: any) => { map[p.id] = p.name; });
    return map;
  }, [plants]);

  const tasksByDate = useMemo(() => {
    const map: Record<string, any[]> = {};
    (tasks || []).forEach((task: any) => {
      const key = taskDateKey(task);
      if (!key) return;
      (map[key] ||= []).push(task);
    });
    return map;
  }, [tasks]);

  const todayKey = dateKey(new Date());
  const todayTasks = tasksByDate[todayKey] || [];

  const isLoading = tasksLoading;
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
      const cellDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const key = dateKey(cellDate);
      const isToday = key === todayKey;
      const dayTasks = tasksByDate[key] || [];
      const taskTypesPresent = Array.from(new Set(dayTasks.map((t) => t.task_type))).filter((t) => TASK_STYLE[t]);
      const tooltip = dayTasks.map((t) => `${TASK_STYLE[t.task_type]?.label || t.task_type}: ${plantNameById[t.plant_id] || t.title}`).join('\n');

      days.push(
        <div
          key={day}
          title={tooltip || undefined}
          className={`min-h-[100px] p-3 glass-card transition-all hover:bg-secondary/40 ${isToday ? 'border-primary bg-primary/5 ring-2 ring-primary/20' : ''
            } ${dayTasks.length > 0 && !isToday ? 'ring-1 ring-primary/10' : ''}`}
        >
          <div className={`font-bold text-sm mb-2 ${isToday ? 'text-primary' : 'text-muted-foreground'}`}>
            {day}
          </div>
          <div className="flex gap-1 flex-wrap">
            {isToday && <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />}
            {taskTypesPresent.map((type) => (
              <div key={type} className={`w-2 h-2 rounded-full ${TASK_STYLE[type].dot}`} />
            ))}
          </div>
        </div>
      );
    }
    return days;
  };

  return (
    <div className="container mx-auto p-4 md:p-8 space-y-8 animate-in fade-in duration-1000 ease-out">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-serif text-3xl md:text-4xl font-semibold text-foreground">
            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h1>
          <p className="text-muted-foreground">Cultivate your collection with precision and care.</p>
        </div>
        <div className="flex items-center gap-2 glass-card px-2 py-2">
          <Button variant="ghost" size="icon" onClick={previousMonth} className="hover:bg-primary/10">
            <ChevronLeft size={20} />
          </Button>
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

      <section className="glass-card p-6 space-y-4">
        <h2 className="font-serif text-xl font-semibold flex items-center gap-2">
          Upcoming for Today <ClipboardCheck className="h-5 w-5 text-primary" />
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {todayTasks.map((task: any) => (
            <div key={task.id} className="p-4 rounded-2xl bg-secondary/40 border border-border flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                {TASK_STYLE[task.task_type]?.icon || <Droplets className="text-blue-500" />}
              </div>
              <div>
                <h4 className="font-bold text-sm">{task.title}</h4>
                <p className="text-xs text-muted-foreground">{plantNameById[task.plant_id] || ''}</p>
              </div>
            </div>
          ))}
          {!isLoading && todayTasks.length === 0 && (
            <p className="col-span-full py-8 text-center italic text-muted-foreground">No tasks scheduled for today.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default CareCalendar;
