import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddPlantDialog } from './AddPlantDialog';

describe('AddPlantDialog', () => {
  it('shows dialog content when open is true', () => {
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onAddPlant={vi.fn()} />);
    expect(screen.getByText('Add New Plant')).toBeInTheDocument();
    expect(screen.getByText('Add Plant')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('hides content when open is false', () => {
    render(<AddPlantDialog open={false} onOpenChange={vi.fn()} onAddPlant={vi.fn()} />);
    expect(screen.queryByText('Add New Plant')).not.toBeInTheDocument();
  });

  it('renders form labels and placeholders', () => {
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onAddPlant={vi.fn()} />);
    expect(screen.getByText('Plant Name')).toBeInTheDocument();
    expect(screen.getByText('Plant Type')).toBeInTheDocument();
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Sunlight Requirements')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., Monstera Deliciosa')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., Living Room, Balcony')).toBeInTheDocument();
  });

  it('calls onOpenChange(false) on cancel click', async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={onOpenChange} onAddPlant={vi.fn()} />);
    await user.click(screen.getByText('Cancel'));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('submits form with text fields and selects', async () => {
    const onAddPlant = vi.fn();
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onAddPlant={onAddPlant} />);

    await user.type(screen.getByPlaceholderText('e.g., Monstera Deliciosa'), 'Monstera');
    await user.type(screen.getByPlaceholderText('e.g., Living Room, Balcony'), 'Living Room');

    fireEvent.click(screen.getByText('Select plant type'));
    fireEvent.click(screen.getByRole('option', { name: 'Indoor Plant' }));

    fireEvent.click(screen.getByText('Select sunlight needs'));
    fireEvent.click(screen.getByRole('option', { name: 'Partial Sun' }));

    await user.click(screen.getByText('Add Plant'));

    expect(onAddPlant).toHaveBeenCalledTimes(1);
    expect(onAddPlant).toHaveBeenCalledWith(
      expect.objectContaining({
        name: 'Monstera',
        species: 'Indoor Plant',
        location: 'Living Room',
        sunlight_requirement: 'Partial Sun',
      })
    );
    expect(onAddPlant.mock.calls[0][0]).toHaveProperty('health_status', 'healthy');
    expect(onAddPlant.mock.calls[0][0]).toHaveProperty('watering_frequency_days', 7);
  });

  it('does not call onAddPlant when form is incomplete', async () => {
    const onAddPlant = vi.fn();
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onAddPlant={onAddPlant} />);

    await user.type(screen.getByPlaceholderText('e.g., Monstera Deliciosa'), 'Monstera');
    await user.click(screen.getByText('Add Plant'));

    expect(onAddPlant).not.toHaveBeenCalled();
  });
});
