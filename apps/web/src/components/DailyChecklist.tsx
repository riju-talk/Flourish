import { Check, Clock, Droplets, FlaskConical, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

interface Task {
    id: string;
    plant_name: string;
    title: string;
    task_type: string;
    priority: string;
}

interface DailyChecklistProps {
    tasks: Task[];
    isLoading: boolean;
}

export const DailyChecklist = ({ tasks, isLoading }: DailyChecklistProps) => {
    if (isLoading) {
        return (
            <div className="space-y-3">
                {Array(3).fill(0).map((_, i) => (
                    <Skeleton key={i} className="h-16 rounded-2xl w-full" />
                ))}
            </div>
        );
    }

    if (!tasks || tasks.length === 0) {
        return (
            <div className="py-8 text-center bg-white/30 rounded-2xl border border-dashed border-primary/20 italic text-muted-foreground">
                All caught up! Your plants are happy.
            </div>
        );
    }

    const getTaskIcon = (type: string) => {
        switch (type.toLowerCase()) {
            case 'watering': return <Droplets className="text-blue-500" />;
            case 'fertilizing': return <FlaskConical className="text-purple-500" />;
            default: return <Search className="text-green-500" />;
        }
    };

    return (
        <div className="space-y-3">
            {tasks.map((task) => (
                <div
                    key={task.id}
                    className="flex items-center justify-between p-4 rounded-2xl bg-white/40 border border-white/20 hover:border-primary/30 transition-all hover:bg-white/60 group"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
                            {getTaskIcon(task.task_type)}
                        </div>
                        <div>
                            <h4 className="font-bold text-sm">{task.title}</h4>
                            <p className="text-xs text-muted-foreground">{task.plant_name}</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${task.priority === 'high' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                            }`}>
                            {task.priority}
                        </div>
                        <Button size="icon" className="h-8 w-8 rounded-full bg-primary text-white opacity-0 group-hover:opacity-100 transition-opacity">
                            <Check size={14} />
                        </Button>
                    </div>
                </div>
            ))}
        </div>
    );
};
