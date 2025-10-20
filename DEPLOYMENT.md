# 🚀 Flourish Deployment Guide

## Overview

Flourish is deployed as a full-stack application with:
- **Frontend**: React + TypeScript (Vercel)
- **Backend**: FastAPI + Python (Railway/Render)
- **Database**: Ready for PostgreSQL integration

## Prerequisites

1. **API Keys** (get these from respective services):
   - Groq API key
   - Plant.ID API key
   - OpenWeatherMap API key
   - Firebase project with service account

2. **Domain names** for production URLs

## Deployment Options

### Option 1: Vercel (Frontend) + Railway (Backend) ⭐ **Recommended**

#### Frontend Deployment (Vercel)

1. **Connect Repository**
   ```bash
   # Fork or connect your repository to Vercel
   # Vercel will auto-detect Next.js/React apps
   ```

2. **Environment Variables** (Set in Vercel dashboard)
   ```env
   VITE_FIREBASE_API_KEY=your_firebase_api_key
   VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your-project-id
   VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   VITE_API_BASE_URL=https://your-backend-domain.com/api
   ```

3. **Deploy**
   ```bash
   # Vercel will handle the build automatically
   npm run build
   ```

#### Backend Deployment (Railway)

1. **Connect Repository**
   ```bash
   # Connect your repository to Railway
   # Railway will detect the Python app
   ```

2. **Environment Variables** (Set in Railway dashboard)
   ```env
   GROQ_API_KEY=your_groq_api_key
   PLANT_ID_API_KEY=your_plant_id_api_key
   OPENWEATHER_API_KEY=your_openweathermap_api_key
   FIREBASE_SERVICE_ACCOUNT_KEY=path_to_service_account_json
   NODE_ENV=production
   ```

3. **Deploy**
   ```bash
   # Railway will handle the build automatically
   # The Dockerfile is already configured
   ```

### Option 2: Vercel (Frontend) + Render (Backend)

#### Backend Deployment (Render)

1. **Create Web Service**
   - Go to Render Dashboard
   - Create new Web Service
   - Connect your repository

2. **Configure Build**
   ```yaml
   # Use the render.yaml file already created
   # Build Command: pip install -r requirements.txt
   # Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables** (Same as Railway above)

### Option 3: Manual Deployment (Docker)

#### Backend (Docker)

```bash
# Build the image
docker build -t flourish-api -f apps/api/Dockerfile .

# Run the container
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e PLANT_ID_API_KEY=your_key \
  -e OPENWEATHER_API_KEY=your_key \
  flourish-api
```

## Production Checklist

### Before Deployment

- [ ] Set up Firebase project and get service account key
- [ ] Get all required API keys
- [ ] Configure domain names
- [ ] Set up environment variables in deployment platform
- [ ] Test locally with production environment variables
- [ ] Update CORS settings for production domains

### After Deployment

- [ ] Verify API endpoints are working
- [ ] Test Firebase authentication
- [ ] Check plant identification API integration
- [ ] Verify weather API integration
- [ ] Test chat functionality
- [ ] Set up monitoring and logging

### Security Considerations

- [ ] Use HTTPS in production
- [ ] Restrict CORS origins to your domains only
- [ ] Set up proper Firebase security rules
- [ ] Enable rate limiting on API endpoints
- [ ] Set up proper logging and monitoring

## Environment Variables Reference

### Frontend (.env)
```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
VITE_API_BASE_URL=https://your-backend-domain.com/api
```

### Backend (.env)
```env
GROQ_API_KEY=your_groq_api_key
PLANT_ID_API_KEY=your_plant_id_api_key
OPENWEATHER_API_KEY=your_openweathermap_api_key
FIREBASE_SERVICE_ACCOUNT_KEY=path_to_service_account_json
ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## Monitoring & Maintenance

### Health Checks
- Frontend: Check if the React app loads
- Backend: `GET /health` endpoint
- Database: Connection status

### Logs
- Check deployment platform logs
- Monitor API error rates
- Track user engagement metrics

### Updates
1. Test changes in development
2. Deploy backend first (if API changes)
3. Deploy frontend
4. Monitor for issues

## Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check ALLOWED_ORIGINS in backend config
   - Ensure frontend URL is whitelisted

2. **API Key Issues**
   - Verify all API keys are set in environment variables
   - Check API key validity with respective services

3. **Firebase Auth Issues**
   - Verify Firebase configuration
   - Check auth domain settings
   - Ensure service account key is valid

4. **Build Failures**
   - Check Node.js/Python versions
   - Verify all dependencies are installed
   - Check for syntax errors

## Support

For issues or questions:
1. Check the logs in your deployment platform
2. Verify all environment variables are set correctly
3. Test API endpoints individually
4. Check service status of external APIs (Groq, Plant.ID, etc.)

---

**🚀 Happy Deploying!**
