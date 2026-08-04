import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const mockInstance = vi.hoisted(() => {
  let reqHandler: ((config: any) => any) | null = null;
  let respErrHandler: ((error: any) => any) | null = null;

  return {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    interceptors: {
      request: {
        use: vi.fn((handler: any) => {
          reqHandler = handler;
        }),
      },
      response: {
        use: vi.fn((_success: any, error: any) => {
          respErrHandler = error;
        }),
      },
    },
    __getReqHandler: () => reqHandler,
    __getRespErrHandler: () => respErrHandler,
  };
});

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockInstance),
  },
}));

import * as api from './api';

describe('api client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('getPlants', () => {
    it('calls GET /plants and returns plants array', async () => {
      const mockPlants = [{ id: '1', name: 'Monstera' }];
      mockInstance.get.mockResolvedValue({ data: { plants: mockPlants } });

      const result = await api.getPlants();

      expect(mockInstance.get).toHaveBeenCalledWith('/plants');
      expect(result).toEqual(mockPlants);
    });
  });

  describe('createPlant', () => {
    it('sends POST /plants with plant data', async () => {
      const plantData = { name: 'Monstera', species: 'Monstera deliciosa' };
      mockInstance.post.mockResolvedValue({ data: plantData });

      const result = await api.createPlant(plantData);

      expect(mockInstance.post).toHaveBeenCalledWith('/plants', plantData);
      expect(result).toEqual(plantData);
    });
  });

  describe('getTodayTasks', () => {
    it('calls GET /tasks/today', async () => {
      mockInstance.get.mockResolvedValue({ data: { tasks: [{ id: 't1' }] } });
      const result = await api.getTodayTasks();
      expect(mockInstance.get).toHaveBeenCalledWith('/tasks/today');
      expect(result).toEqual([{ id: 't1' }]);
    });
  });

  describe('getDashboardData', () => {
    it('calls GET /dashboard', async () => {
      mockInstance.get.mockResolvedValue({ data: { stats: {} } });
      const result = await api.getDashboardData();
      expect(mockInstance.get).toHaveBeenCalledWith('/dashboard');
      expect(result).toEqual({ stats: {} });
    });
  });

  describe('chatWithAI', () => {
    it('sends POST /chat with messages', async () => {
      const messages = [{ role: 'user', content: 'hello' }];
      mockInstance.post.mockResolvedValue({
        data: { response: 'hi', suggestions: ['water'] },
      });
      const result = await api.chatWithAI(messages);
      expect(mockInstance.post).toHaveBeenCalledWith('/chat', messages);
      expect(result).toEqual({ response: 'hi', suggestions: ['water'] });
    });
  });

  describe('auth token interceptor', () => {
    it('attaches Bearer token from localStorage', async () => {
      localStorage.setItem('flourish_token', 'my-token');

      const reqHandler = mockInstance.__getReqHandler();
      expect(reqHandler).not.toBeNull();

      const config = { headers: {} };
      const result = await reqHandler!(config);

      expect(result.headers.Authorization).toBe('Bearer my-token');
    });

    it('does not attach token when localStorage is empty', async () => {
      const reqHandler = mockInstance.__getReqHandler();
      const config = { headers: {} };
      const result = await reqHandler!(config);
      expect(result.headers.Authorization).toBeUndefined();
    });
  });

  describe('401 response interceptor', () => {
    let originalLocation: Location;

    beforeEach(() => {
      originalLocation = window.location;
      Object.defineProperty(window, 'location', {
        configurable: true,
        value: { ...originalLocation, href: '' },
      });
    });

    afterEach(() => {
      Object.defineProperty(window, 'location', {
        configurable: true,
        value: originalLocation,
      });
    });

    it('redirects to /auth on 401 and clears storage', async () => {
      localStorage.setItem('flourish_token', 'expired-token');
      localStorage.setItem('flourish_user', JSON.stringify({ uid: 'u1' }));

      const errHandler = mockInstance.__getRespErrHandler();
      expect(errHandler).not.toBeNull();

      const error = { response: { status: 401 } };
      await expect(errHandler!(error)).rejects.toEqual(error);

      expect(localStorage.getItem('flourish_token')).toBeNull();
      expect(localStorage.getItem('flourish_user')).toBeNull();
      expect(window.location.href).toBe('/auth');
    });

    it('does not redirect on non-401 errors', async () => {
      const errHandler = mockInstance.__getRespErrHandler();
      const error = { response: { status: 500 } };

      await expect(errHandler!(error)).rejects.toEqual(error);
      expect(window.location.href).not.toBe('/auth');
    });
  });
});
