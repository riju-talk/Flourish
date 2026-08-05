import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddPlantDialog } from './AddPlantDialog';
import { createAutonomousPlant } from '@/integrations/api';

vi.mock('@/integrations/api', () => ({
  createAutonomousPlant: vi.fn(),
}));

const mockedCreateAutonomousPlant = vi.mocked(createAutonomousPlant);

describe('AddPlantDialog', () => {
  beforeEach(() => {
    mockedCreateAutonomousPlant.mockReset();
  });

  it('shows dialog content when open is true', () => {
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onSuccess={vi.fn()} />);
    expect(screen.getByText('Add a Plant')).toBeInTheDocument();
    expect(screen.getByText('Add to My Garden')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('hides content when open is false', () => {
    render(<AddPlantDialog open={false} onOpenChange={vi.fn()} onSuccess={vi.fn()} />);
    expect(screen.queryByText('Add a Plant')).not.toBeInTheDocument();
  });

  it('renders form labels and placeholders', () => {
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onSuccess={vi.fn()} />);
    expect(screen.getByText('Plant name')).toBeInTheDocument();
    expect(screen.getByText('Where will it live? (optional)')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., Monstera Deliciosa, Snake Plant, Basil')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('e.g., Living Room, Balcony')).toBeInTheDocument();
  });

  it('calls onOpenChange(false) on cancel click', async () => {
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={onOpenChange} onSuccess={vi.fn()} />);
    await user.click(screen.getByText('Cancel'));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('submits the plant name (and optional location) via the agentic autonomous-create endpoint', async () => {
    mockedCreateAutonomousPlant.mockResolvedValue({ success: true, plant: {}, tasks: [] });
    const onSuccess = vi.fn();
    const onOpenChange = vi.fn();
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={onOpenChange} onSuccess={onSuccess} />);

    await user.type(screen.getByPlaceholderText('e.g., Monstera Deliciosa, Snake Plant, Basil'), 'Monstera');
    await user.type(screen.getByPlaceholderText('e.g., Living Room, Balcony'), 'Living Room');
    await user.click(screen.getByText('Add to My Garden'));

    await waitFor(() => expect(mockedCreateAutonomousPlant).toHaveBeenCalledWith('Monstera', 'Living Room'));
    await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it('does not submit when the plant name is empty', async () => {
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onSuccess={vi.fn()} />);

    expect(screen.getByText('Add to My Garden').closest('button')).toBeDisabled();
    expect(mockedCreateAutonomousPlant).not.toHaveBeenCalled();
  });

  it('shows an error and keeps the dialog open when the request fails', async () => {
    mockedCreateAutonomousPlant.mockRejectedValue(new Error('network error'));
    const onSuccess = vi.fn();
    const user = userEvent.setup();
    render(<AddPlantDialog open={true} onOpenChange={vi.fn()} onSuccess={onSuccess} />);

    await user.type(screen.getByPlaceholderText('e.g., Monstera Deliciosa, Snake Plant, Basil'), 'Monstera');
    await user.click(screen.getByText('Add to My Garden'));

    await waitFor(() => expect(screen.getByText(/couldn't add that plant/i)).toBeInTheDocument());
    expect(onSuccess).not.toHaveBeenCalled();
  });
});
