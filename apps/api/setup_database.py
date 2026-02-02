"""
Initialize Firebase Firestore Database for Flourish App
This script sets up the database structure and indexes
"""
import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin
service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "firebase-service-account.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

def setup_firestore_collections():
    """Set up Firestore collections with sample data and structure"""
    
    print("🔥 Setting up Firestore database for Flourish...")
    
    # Collections to create
    collections = {
        "profiles": {
            "description": "User profiles with gamification stats",
            "fields": [
                "email", "display_name", "photo_url",
                "total_score", "level", "tasks_completed",
                "streak_days", "last_activity", "achievements",
                "created_at", "updated_at"
            ]
        },
        "plants": {
            "description": "User plant inventory",
            "fields": [
                "user_id", "name", "species", "location",
                "image_url", "care_instructions", "health_status",
                "last_watered", "next_watering", "created_at", "updated_at"
            ]
        },
        "care_tasks": {
            "description": "Plant care tasks and reminders",
            "fields": [
                "user_id", "plant_id", "task_type", "title",
                "description", "due_date", "recurring", "recurring_days",
                "completed", "completed_at", "points", "priority", "created_at"
            ]
        },
        "notifications": {
            "description": "User notifications",
            "fields": [
                "user_id", "type", "title", "message",
                "read", "created_at"
            ]
        },
        "health_checks": {
            "description": "Plant health check history",
            "fields": [
                "plant_id", "user_id", "status", "notes",
                "symptoms", "recommendations", "checked_at"
            ]
        }
    }
    
    print("\n📊 Database Collections:")
    for collection_name, info in collections.items():
        print(f"\n✅ {collection_name}")
        print(f"   Description: {info['description']}")
        print(f"   Fields: {', '.join(info['fields'])}")
    
    print("\n✅ Firestore database structure ready!")
    print("\n📝 Collections created (will be visible once data is added):")
    for collection_name in collections.keys():
        print(f"   - {collection_name}")
    
    return collections

def create_sample_data():
    """Create sample data for testing (optional)"""
    
    print("\n\n🌱 Would you like to create sample data for testing?")
    print("This will create a test user with sample plants and tasks.")
    print("Note: In production, data will be created through the app.")
    
    # You can uncomment this to create test data
    # test_user_id = "test_user_123"
    # 
    # # Create test profile
    # db.collection("profiles").document(test_user_id).set({
    #     "email": "test@flourish.com",
    #     "display_name": "Test User",
    #     "photo_url": "",
    #     "total_score": 0,
    #     "level": 1,
    #     "tasks_completed": 0,
    #     "streak_days": 0,
    #     "last_activity": None,
    #     "achievements": [],
    #     "created_at": firestore.SERVER_TIMESTAMP,
    #     "updated_at": firestore.SERVER_TIMESTAMP
    # })
    # print(f"✅ Created test user profile: {test_user_id}")

def print_security_rules():
    """Print the Firestore security rules that should be applied"""
    
    print("\n\n🔒 IMPORTANT: Set up Firestore Security Rules")
    print("=" * 70)
    print("\nGo to: https://console.firebase.google.com/project/flourish-de908/firestore/rules")
    print("\nReplace the rules with this:\n")
    
    rules = """rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Helper function to check if user is authenticated
    function isAuthenticated() {
      return request.auth != null;
    }
    
    // Helper function to check if user owns the resource
    function isOwner(userId) {
      return isAuthenticated() && request.auth.uid == userId;
    }
    
    // Profiles - users can read/write their own profile
    // All authenticated users can read profiles (for leaderboard)
    match /profiles/{userId} {
      allow read: if isAuthenticated();
      allow write: if isOwner(userId);
    }
    
    // Plants - users can only access their own plants
    match /plants/{plantId} {
      allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated() && request.resource.data.user_id == request.auth.uid;
      allow update, delete: if isAuthenticated() && resource.data.user_id == request.auth.uid;
    }
    
    // Care Tasks - users can only access their own tasks
    match /care_tasks/{taskId} {
      allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated() && request.resource.data.user_id == request.auth.uid;
      allow update, delete: if isAuthenticated() && resource.data.user_id == request.auth.uid;
    }
    
    // Notifications - users can only access their own notifications
    match /notifications/{notificationId} {
      allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated() && request.resource.data.user_id == request.auth.uid;
      allow update, delete: if isAuthenticated() && resource.data.user_id == request.auth.uid;
    }
    
    // Health Checks - users can only access their own health checks
    match /health_checks/{checkId} {
      allow read: if isAuthenticated() && resource.data.user_id == request.auth.uid;
      allow create: if isAuthenticated() && request.resource.data.user_id == request.auth.uid;
      allow update, delete: if isAuthenticated() && resource.data.user_id == request.auth.uid;
    }
  }
}"""
    
    print(rules)
    print("\n" + "=" * 70)

def print_indexes():
    """Print recommended Firestore indexes"""
    
    print("\n\n📑 Recommended Firestore Indexes")
    print("=" * 70)
    print("\nThese will be automatically created as you use the app.")
    print("If you see 'index required' errors, Firebase will provide a link to create them.")
    print("\nRecommended indexes:")
    print("\n1. Collection: profiles")
    print("   - total_score (Descending)")
    print("   - Used for: Leaderboard queries")
    
    print("\n2. Collection: care_tasks")
    print("   - user_id (Ascending), due_date (Ascending)")
    print("   - Used for: User's tasks sorted by due date")
    
    print("\n3. Collection: notifications")
    print("   - user_id (Ascending), created_at (Descending)")
    print("   - Used for: User's notifications sorted by date")
    
    print("\n" + "=" * 70)

def verify_connection():
    """Verify Firebase connection"""
    
    print("\n\n🔍 Verifying Firebase connection...")
    
    try:
        # Try to access Firestore
        collections = db.collections()
        collection_names = [col.id for col in collections]
        
        if collection_names:
            print(f"✅ Connected! Found {len(collection_names)} existing collections:")
            for name in collection_names:
                print(f"   - {name}")
        else:
            print("✅ Connected! Database is empty (collections will appear when data is added)")
        
        return True
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    
    print("\n" + "=" * 70)
    print("🌱 FLOURISH DATABASE SETUP")
    print("=" * 70)
    
    # Verify connection
    if not verify_connection():
        print("\n❌ Setup failed! Check your Firebase credentials.")
        return
    
    # Set up collections
    setup_firestore_collections()
    
    # Print security rules
    print_security_rules()
    
    # Print indexes info
    print_indexes()
    
    # Final instructions
    print("\n\n✨ NEXT STEPS:")
    print("=" * 70)
    print("\n1. ✅ Database structure is ready!")
    print("2. 🔒 Copy the security rules above to Firebase Console")
    print("3. 🔐 Enable Google Sign-In in Authentication")
    print("   https://console.firebase.google.com/project/flourish-de908/authentication/providers")
    print("4. 🚀 Start your backend: python main.py")
    print("5. 🌐 Start your frontend: npm run dev")
    print("6. 🎉 Sign in and start using Flourish!")
    
    print("\n" + "=" * 70)
    print("✅ DATABASE SETUP COMPLETE!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
