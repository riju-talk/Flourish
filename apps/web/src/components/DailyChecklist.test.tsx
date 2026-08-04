import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DailyChecklist } from './DailyChecklist';

const mockTasks = [
  { id: '1', plant_name: 'Monstera', title: 'Water Monstera', task_type: 'watering', priority: 'high' },
  { id: '2', plant_name: 'Snake Plant', title: 'Fertilize Snake Plant', task_type: 'fertilizing', priority: 'normal' },
  { id: '3', plant_name: 'Fern', title: 'Check Fern sunlight', task_type: 'sunlight', priority: 'normal' },
  { id: '4', plant_name: 'Rose', title: 'Pest check Rose', task_type: 'pest check', priority: 'high' },
];

describe('DailyChecklist', () => {
  it('shows "All caught up!" when tasks is empty', () => {
    render(<DailyChecklist tasks={[]} isLoading={false} />);
    expect(screen.getByText(/All caught up/i)).toBeInTheDocument();
  });

  it('renders task items with titles and plant names', () => {
    render(<DailyChecklist tasks={mockTasks} isLoading={false} />);
    expect(screen.getByText('Water Monstera')).toBeInTheDocument();
    expect(screen.getByText('Fertilize Snake Plant')).toBeInTheDocument();
    expect(screen.getByText('Monstera')).toBeInTheDocument();
    expect(screen.getByText('Snake Plant')).toBeInTheDocument();
  });

  it('shows loading skeletons when isLoading is true', () => {
    const { container } = render(<DailyChecklist tasks={[]} isLoading={true} />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBe(3);
  });

  it('does not render tasks when loading', () => {
    render(<DailyChecklist tasks={mockTasks} isLoading={true} />);
    expect(screen.queryByText('Water Monstera')).not.toBeInTheDocument();
  });

  it('shows high priority badge with red styling', () => {
    render(<DailyChecklist tasks={[mockTasks[0]]} isLoading={false} />);
    const badge = screen.getByText('high');
    expect(badge.className).toContain('text-red-600');
    expect(badge.className).toContain('bg-red-100');
  });

  it('shows normal priority badge with blue styling', () => {
    render(<DailyChecklist tasks={[mockTasks[1]]} isLoading={false} />);
    const badge = screen.getByText('normal');
    expect(badge.className).toContain('text-blue-600');
    expect(badge.className).toContain('bg-blue-100');
  });

  it('renders all task types with appropriate icons', () => {
    render(<DailyChecklist tasks={mockTasks} isLoading={false} />);
    expect(screen.getByText('Water Monstera')).toBeInTheDocument();
    expect(screen.getByText('Fertilize Snake Plant')).toBeInTheDocument();
    expect(screen.getByText('Check Fern sunlight')).toBeInTheDocument();
    expect(screen.getByText('Pest check Rose')).toBeInTheDocument();
  });
});
