// components/CareCalendar.tsx
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import { getCalendarEvents, getCareTasks } from '@/integrations/api';

interface CareTask {
  id: string;
  title: string;
  task_type: string;
  scheduled_date: string;
  status: string;
  plants?: { name: string };
}

const CareCalendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());

  // ── Fetch calendar events ──  
  const start = `${currentDate.getFullYear()}-${String(currentDate.getMonth()+1).padStart(2,'0')}-01`;
  const end =   `${currentDate.getFullYear()}-${String(currentDate.getMonth()+1).padStart(2,'0')}-${String(
                   new Date(currentDate.getFullYear(), currentDate.getMonth()+1, 0).getDate()
                 ).padStart(2,'0')}`;

  const { data: calendarEvents = [], isLoading: eventsLoading } = useQuery({
    queryKey: ['calendarEvents', start, end],
    queryFn: () => getCalendarEvents(start, end),
    enabled: true,
  });

  // ── Fetch today’s tasks ──
  const today = new Date().toISOString().split('T')[0];
  const { data: todaysTasks = [], isLoading: tasksLoading } = useQuery({
    queryKey: ['careTasks', today],
    queryFn: () => getCareTasks({ status: 'pending' })
      .then(tasks => tasks.filter(t => t.scheduled_date === today)),
    enabled: true,
  });

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();
  const monthNames = [ /* … */ ];
  const weekDays = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

  const previousMonth = () =>
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const nextMonth = () =>
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));

  const renderCalendarDays = () => {
    const days = [];
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(<div key={`empty-${i}`} className="h-24" />);
    }
    for (let day = 1; day <= daysInMonth; day++) {
      const isToday = today === `${currentDate.getFullYear()}-${String(currentDate.getMonth()+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
      const dayTasks = calendarEvents.filter(e => e.scheduled_date === `${currentDate.getFullYear()}-${String(currentDate.getMonth()+1).padStart(2,'0')}-${String(day).padStart(2,'0')}`);

      days.push(
        <div
          key={day}
          className={`h-24 p-2 border rounded-lg ${
            isToday ? 'bg-green-100 border-green-300' : 'bg-white/50'
          }`}
        >
          <div className={`font-semibold mb-1 ${isToday ? 'text-green-700' : 'text-gray-700'}`}>
            {day}
          </div>
          {dayTasks.map((t) => (
            <div key={t.id} className="space-y-1">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              <div className="text-xs text-gray-600 truncate">{t.title}</div>
            </div>
          ))}
        </div>
      );
    }
    return days;
  };

  return (
    <div className="space-y-6">
      <Card className="bg-white/60 backdrop-blur-sm border-green-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <CalendarIcon className="w-5 h-5 text-green-600" />
              <span>Smart Care Calendar</span>
            </CardTitle>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm" onClick={previousMonth}>
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <span className="font-semibold text-lg px-4">
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </span>
              <Button variant="outline" size="sm" onClick={nextMonth}>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {eventsLoading ? (
            <p>Loading calendar…</p>
          ) : (
            <>
              <div className="grid grid-cols-7 gap-2 mb-4">
                {weekDays.map((d) => (
                  <div key={d} className="text-center font-semibold text-gray-600 py-2">
                    {d}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-2">{renderCalendarDays()}</div>
            </>
          )}
        </CardContent>
      </Card>

      <Card className="bg-white/60 backdrop-blur-sm border-green-200">
        <CardHeader>
          <CardTitle>Today's Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          {tasksLoading ? (
            <p>Loading tasks…</p>
          ) : todaysTasks.length === 0 ? (
            <p className="text-gray-500 text-center py-4">No tasks scheduled for today!</p>
          ) : (
            todaysTasks.map((task) => (
              <div
                key={task.id}
                className="flex items-center justify-between p-3 bg-white/50 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      task.task_type === 'watering'
                        ? 'bg-blue-500'
                        : task.task_type === 'fertilizing'
                        ? 'bg-green-500'
                        : 'bg-yellow-500'
                    }`}
                  />
                  <span className="font-medium">{task.title}</span>
                  {task.plants && (
                    <span className="text-sm text-gray-500">({task.plants.name})</span>
                  )}
                </div>
                <Badge variant="outline">{task.task_type}</Badge>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default CareCalendar;
