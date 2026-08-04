import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PlantCard } from './PlantCard';

const mockPlant = {
  id: '1',
  name: 'Monstera',
  species: 'Monstera deliciosa',
  health_score: 85,
  watering_frequency_days: 7,
  sunlight_requirement: 'Bright, indirect',
  plant_type: 'Indoor',
};

describe('PlantCard', () => {
  it('renders plant name and species', () => {
    render(<PlantCard plant={mockPlant} />);
    expect(screen.getByText('Monstera')).toBeInTheDocument();
    expect(screen.getByText('Monstera deliciosa')).toBeInTheDocument();
  });

  it('shows health score', () => {
    render(<PlantCard plant={mockPlant} />);
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('shows sunlight requirement', () => {
    render(<PlantCard plant={mockPlant} />);
    expect(screen.getByText('Bright, indirect')).toBeInTheDocument();
  });

  it('shows watering frequency', () => {
    render(<PlantCard plant={mockPlant} />);
    expect(screen.getByText('7d')).toBeInTheDocument();
  });

  it('shows plant type badge', () => {
    render(<PlantCard plant={mockPlant} />);
    expect(screen.getByText('Indoor')).toBeInTheDocument();
  });

  it('health score color is green when above 80', () => {
    render(<PlantCard plant={mockPlant} />);
    const scoreEl = screen.getByText('85%');
    expect(scoreEl.className).toContain('text-green-500');
  });

  it('health score color is yellow when 80 or below', () => {
    render(<PlantCard plant={{ ...mockPlant, health_score: 70 }} />);
    const scoreEl = screen.getByText('70%');
    expect(scoreEl.className).toContain('text-yellow-500');
  });

  it('applies custom className', () => {
    const { container } = render(<PlantCard plant={mockPlant} className="custom-class" />);
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
