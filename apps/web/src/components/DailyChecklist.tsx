import { Check, Clock, Droplets, FlaskConical, Search, Sun, Bug } from "lucide-react";
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
                    <Skeleton key={i} className="h-20 rounded-2xl w-full bg-white/20" />
                ))}
            </div>
        );
    }

    if (!tasks || tasks.length === 0) {
        return (
            <div className="py-12 text-center bg-white/40 rounded-[2rem] border border-dashed border-white/40 italic text-muted-foreground">
                <p className="text-lg font-medium text-emerald-700/60 mb-1">All caught up! 🎉</p>
                <p className="text-sm">Your plants are thriving.</p>
            </div>
        );
    }

    const getTaskIcon = (type: string) => {
        switch (type.toLowerCase()) {
            case 'watering': return <Droplets className="text-blue-500" size={20} />;
            case 'fertilizing': return <FlaskConical className="text-purple-500" size={20} />;
            case 'sunlight': return <Sun className="text-amber-500" size={20} />;
            case 'pest check': return <Bug className="text-red-500" size={20} />;
            default: return <Search className="text-green-500" size={20} />;
        }
    };

    return (
        <div className="space-y-3">
            {tasks.map((task) => (
                <div
                    key={task.id}
                    className="flex items-center justify-between p-4 rounded-2xl bg-white/60 border border-white/40 shadow-sm hover:shadow-md hover:bg-white/80 transition-all group hover:-translate-x-1 duration-300"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-white to-white/50 flex items-center justify-center shadow-inner">
                            {getTaskIcon(task.task_type)}
                        </div>
                        <div>
                            <h4 className="font-bold text-sm text-foreground">{task.title}</h4>
                            <p className="text-xs text-muted-foreground font-medium">{task.plant_name}</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider shadow-sm ${task.priority === 'high'
                                ? 'bg-red-100 text-red-600'
                                : 'bg-blue-100 text-blue-600'
                            }`}>
                            {task.priority}
                        </div>
                        <Button
                            size="icon"
                            className="h-10 w-10 rounded-full bg-secondary text-primary hover:bg-primary hover:text-white transition-all shadow-sm"
                        >
                            <Check size={18} />
                        </Button>
                    </div>
                </div>
            ))}
        </div>
    );
};
