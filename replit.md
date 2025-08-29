# Overview

EcoMind is an AI-powered plant care system that provides proactive monitoring, analysis, and optimization of plant health through intelligent automation. Unlike traditional plant care apps, EcoMind uses an AI agent approach to continuously monitor plant health metrics, predict issues before they become problems, and generate dynamic care schedules that adapt to plant responses.

The system features a conversational AI assistant with multi-modal capabilities (text and image analysis), automated health tracking with daily checklists, personalized care plans that evolve based on plant responses, and a modern dashboard that visualizes overall garden health with actionable insights.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Monorepo Structure
The project uses a Turborepo monorepo architecture with separate apps for the web frontend and API backend, plus shared packages for common utilities. This provides excellent code organization, shared dependency management, and optimized build pipelines across the entire system.

## Frontend Architecture
The web application is built with React 18, TypeScript, and Vite for fast development and optimized builds. It uses shadcn/ui components built on Radix UI primitives for accessibility and consistent design, with Tailwind CSS for styling and responsive design. React Query handles server state management and caching, while React Router provides client-side navigation.

The frontend follows a component-based architecture with reusable UI components, custom hooks for business logic, and a clean separation between presentation and data fetching layers.

## Backend Architecture
The API is built with FastAPI (Python) following a clean architecture pattern with separate layers for routes, services, and models. Pydantic handles data validation and serialization, while the service layer contains business logic for plant analysis, care scheduling, and AI interactions.

The backend uses an in-memory data store for rapid prototyping but is designed to easily integrate with external databases. Background tasks handle continuous monitoring and automated scheduling.

## AI Integration
The system integrates with Groq's language models for advanced plant care intelligence. The AI service provides multi-modal chat capabilities, plant health analysis from images, proactive issue detection, and personalized care recommendations. The AI system is designed with extensible prompts and context management for consistent plant care expertise.

## Authentication System
Currently implements a mock authentication system for development, designed to integrate with Firebase Auth for production. The authentication context provides user management, session handling, and route protection throughout the application.

## Data Models
The system uses well-defined TypeScript interfaces and Pydantic models for type safety across the full stack. Core entities include Plants (with health metrics and care requirements), Tasks (AI-generated care schedules), Health Checks (systematic monitoring data), and Chat Messages (AI conversation history).

## External Dependencies

- **Groq AI**: Advanced language model integration for plant care intelligence and conversational AI capabilities
- **Unsplash API**: Plant image fetching for visual plant identification and gallery features
- **Firebase**: Planned integration for user authentication and real-time data synchronization
- **React Query**: Client-side data fetching, caching, and state management
- **Radix UI**: Accessible component primitives for consistent user interface design
- **Tailwind CSS**: Utility-first CSS framework for responsive design and theming