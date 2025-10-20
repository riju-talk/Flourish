import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Calendar, CheckCircle, Clock, Droplets, Sprout, Activity } from 'lucide-react';
import { getTodaySchedule, getWeekSchedule, completeCareTask } from '@/integrations/api';
import { useAuth } from '@/hooks/useAuth';

interface ScheduleItem {
  task: {
    plant_id: string;
    schedule_type: string;
    title: string;
    description: string;
    scheduled_date: string;
    priority: string;
    estimated_time: string;
    completed: boolean;
  };
  plant_name: string;
  plant_id: string;
}

export default function ScheduleCalendar() {
  const { user } = useAuth();
  const [todaySchedule, setTodaySchedule] = useState<any>(null);
  const [weekSchedule, setWeekSchedule] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    setLoading(true);
    try {
      const [todayData, weekData] = await Promise.all([
        getTodaySchedule(),
        getWeekSchedule()
      ]);
      setTodaySchedule(todayData);
      setWeekSchedule(weekData);
    } catch (error) {
      console.error('Error loading schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTask = async (plantId: string, scheduleId: string, taskType: string) => {
    try {
      await completeCareTask(plantId, scheduleId, `Completed ${taskType} task`);
      await loadSchedules(); // Refresh schedules
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  const getTaskIcon = (taskType: string) => {
    switch (taskType) {
      case 'watering':
        return <Droplets className="h-4 w-4" />;
      case 'fertilizing':
        return <Sprout className="h-4 w-4" />;
      case 'health_check':
        return <Activity className="h-4 w-4" />;
      default:
        return <CheckCircle className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-blue-100 text-blue-800';
      case 'low':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <Calendar className="h-8 w-8 mx-auto mb-2 animate-pulse" />
          <p>Loading your care schedule...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Today's Schedule */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Today's Care Tasks
          </CardTitle>
          <CardDescription>
            {todaySchedule?.total_tasks || 0} tasks scheduled for {new Date().toLocaleDateString()}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {todaySchedule?.tasks && todaySchedule.tasks.length > 0 ? (
            <div className="space-y-3">
              {todaySchedule.tasks.map((item: ScheduleItem, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="flex-shrink-0">
                      {getTaskIcon(item.task.schedule_type)}
                    </div>
                    <div>
                      <p className="font-medium">{item.task.title}</p>
                      <p className="text-sm text-muted-foreground">{item.task.description}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant="outline" className={getPriorityColor(item.task.priority)}>
                          {item.task.priority}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {item.task.estimated_time}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={() => handleCompleteTask(
                      item.plant_id,
                      item.task.scheduled_date,
                      item.task.schedule_type
                    )}
                    className="flex items-center gap-1"
                  >
                    <CheckCircle className="h-3 w-3" />
                    Complete
                  </Button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <CheckCircle className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No tasks scheduled for today!</p>
              <p className="text-sm">Great job keeping up with your plant care! 🌱</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Week Overview */}
      <Card>
        <CardHeader>
          <CardTitle>7-Day Schedule Overview</CardTitle>
          <CardDescription>
            {weekSchedule?.total_tasks || 0} tasks scheduled for the next week
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-64">
            {weekSchedule?.tasks_by_day && Object.keys(weekSchedule.tasks_by_day).length > 0 ? (
              <div className="space-y-4">
                {Object.entries(weekSchedule.tasks_by_day).map(([date, tasks]) => (
                  <div key={date}>
                    <div className="flex items-center gap-2 mb-2">
                      <h4 className="font-medium text-sm">
                        {new Date(date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </h4>
                      <Badge variant="outline">
                        {(tasks as ScheduleItem[]).length} tasks
                      </Badge>
                    </div>

                    <div className="space-y-2 pl-4 border-l-2 border-muted">
                      {(tasks as ScheduleItem[]).map((item: ScheduleItem, index: number) => (
                        <div key={index} className="flex items-center justify-between py-1">
                          <div className="flex items-center gap-2">
                            {getTaskIcon(item.task.schedule_type)}
                            <span className="text-sm">{item.plant_name}</span>
                          </div>
                          <Badge
                            variant="outline"
                            className={`text-xs ${getPriorityColor(item.task.priority)}`}
                          >
                            {item.task.schedule_type}
                          </Badge>
                        </div>
                      ))}
                    </div>

                    {date !== Object.keys(weekSchedule.tasks_by_day)[Object.keys(weekSchedule.tasks_by_day).length - 1] && (
                      <Separator className="my-4" />
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No tasks scheduled for the next week</p>
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <Droplets className="h-6 w-6" />
              <span className="text-sm">Water All</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <Activity className="h-6 w-6" />
              <span className="text-sm">Health Check</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <Sprout className="h-6 w-6" />
              <span className="text-sm">Fertilize</span>
            </Button>
            <Button variant="outline" className="h-auto p-4 flex flex-col items-center gap-2">
              <Clock className="h-6 w-6" />
              <span className="text-sm">View History</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
