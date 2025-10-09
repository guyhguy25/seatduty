# Seat Duty Backend - TODO List

## Overview
Complete redesign of the backend system for seat duty management, including user registration, group management, club associations, and seat duty coordination.

## 🏗️ Database Design & Schema

### Core Tables
- [ ] **Users Table**
  - User registration (name, email, phone, password)
  - User settings and preferences
  - Authentication tokens/sessions
  - User roles and permissions

- [ ] **Groups Table**
  - Group creation and management
  - Group settings and preferences
  - Group admin assignment
  - Group membership tracking
  - Season number (for 365scores API)
  - Competition ID (for 365scores API)
  - Team/Club ID (competitor ID for home games)

- [ ] **Clubs Table**
  - Club information and details
  - Home venue information
  - Season schedules and game data
  - 365scores competitor ID
  - Competition ID mappings
  - Season information

- [ ] **Group-Club Association Table**
  - Link groups to clubs (admin-only)
  - Track association status and permissions

- [ ] **Games Table**
  - Home game schedules for the season
  - Game details (opponent, date, time, venue)
  - Game status and updates
  - 365scores game ID
  - Competition ID and season number
  - Home/away competitor information
  - API sync timestamps

- [ ] **Seat Duty Table**
  - Seat duty assignments per game
  - Maximum 2 duties per group per game
  - Duty status and completion tracking

- [ ] **Invitations Table**
  - Group invitation system
  - Invitation status tracking
  - Invitation expiration and management

## 🔐 User Management System

### User Registration & Authentication
- [x] **User Registration**
  - Email/password registration
  - Email verification system
  - Profile setup (name, phone, preferences)
  - Password reset functionality

- [ ] **Change to Phone Number**
  - Remove Email

- [x] **Authentication System**
  - JWT token implementation
  - Session management
  - Password hashing and security
  - Login/logout endpoints

- [x] **User Profile Management**
  - Profile CRUD operations
  - User settings and preferences
  - Notification preferences
  - Account deactivation/deletion

## 👥 Group Management System

### Group Operations
- [x] **Group Registration**
  - Create new groups
  - Set group name and description
  - Assign group admin during creation
  - Group settings configuration

- [x] **Group Administration**
  - Admin permissions and controls
  - Member management (add/remove)
  - Group settings updates
  - Group deletion and archival

- [x] **Group Membership**
  - Join/leave group functionality
  - Member role assignment
  - Membership status tracking
  - Group member list and details

## 📧 Invitation System

### Invitation Management
- [x] **Send Invitations**
  - Token-based invitations (no email)
  - Invitation message customization
  - Bulk invitation sending
  - Invitation tracking and status

- [x] **Accept/Decline Invitations**
  - Invitation response handling
  - Automatic group joining on acceptance
  - Invitation expiration management
  - Invitation history tracking

## 🏟️ Club Association System

### Club Integration
- [x] **Club Management** ✅ COMPLETED
  - ✅ Club information database (external_id, name, logo, country, competition)
  - ✅ 365scores API integration (countries, competitions, teams)
  - ✅ Caching system (24-hour cache for API responses)
  - ✅ Club creation from team selection
  - 📝 See: CLUB_README.md, CLUB_MANAGEMENT.md, FRONTEND_INTEGRATION.md

- [x] **Group-Club Association** ✅ COMPLETED
  - ✅ Group-Club linking (club_id foreign key)
  - ✅ Optional club association (nullable club_id)
  - ✅ Club validation during group creation
  - ✅ Complete API endpoints and schemas
  - 📝 Frontend implementation pending (see EXAMPLE_FRONTEND_COMPONENT.tsx)

## ⚽ Game Management System

### 365scores API Integration
- [ ] **API Configuration Management**
  - Group-specific API settings (season, competition ID, team ID)
  - Dynamic parameter building for API calls
  - API rate limiting and caching strategies
  - Error handling and retry mechanisms

- [ ] **Game Data Fetching**
  - `fetch_games_for_group(group_id)` - Fetch games for specific group
  - `filter_home_games(games, team_id)` - Filter home games by team
  - `sync_group_games(group_id)` - Sync and store games for group
  - `update_game_status(game_id)` - Update individual game status

- [ ] **API Response Processing**
  - Parse 365scores game data structure
  - Handle different game statuses and formats
  - Store competitor information (home/away teams)
  - Process game timing and venue data

### Season Games
- [ ] **Game Data Management**
  - Game details CRUD operations
  - Game status tracking and updates
  - Venue and timing information
  - Game cancellation/postponement handling
  - API response caching and optimization
  - Multi-group game data aggregation

## 🪑 Seat Duty System

### Duty Management
- [ ] **Seat Duty Creation**
  - Create duties for each home game
  - Duty type and description
  - Required number of volunteers
  - Duty timing and requirements

- [ ] **Duty Assignment**
  - Maximum 2 duties per group per game
  - Volunteer sign-up system
  - Assignment confirmation
  - Duty completion tracking

- [ ] **Duty Coordination**
  - Duty schedule management
  - Reminder notifications
  - Duty status updates
  - Performance tracking

## 🔧 CRUD Operations

### Core CRUD Implementation
- [x] **Users CRUD**
  - Create, read, update, delete users
  - User search and filtering
  - Bulk user operations
  - User data validation

- [ ] **Groups CRUD**
  - Complete group management
  - Group search and discovery
  - Group statistics and analytics
  - Group archival system

- [ ] **Games CRUD**
  - Game data management
  - Game search and filtering
  - Game statistics tracking
  - Game history management

- [ ] **Seat Duties CRUD**
  - Duty creation and management
  - Duty assignment tracking
  - Duty completion monitoring
  - Duty reporting and analytics

## ⚙️ Settings Management

### User Settings
- [ ] **Profile Settings**
  - Personal information updates
  - Contact preferences
  - Notification settings
  - Privacy controls

- [ ] **Account Settings**
  - Password management
  - Email preferences
  - Account security
  - Data export/deletion

### Group Settings
- [ ] **Group Configuration**
  - Group name and description
  - Group rules and guidelines
  - Notification preferences
  - Member management settings

- [ ] **Club Association Settings**
  - Club preferences
  - Game notification settings
  - Duty assignment preferences
  - Season configuration

## 🔧 365scores API Implementation

### API Configuration
```python
# Base API URL and parameters
SCORES_API_URL = "https://webws.365scores.com/web/games/fixtures/"
DEFAULT_PARAMS = {
    "appTypeId": 5,
    "langId": 2,
    "timezoneName": "Asia/Jerusalem",
    "userCountryId": 6,
    "showOdds": "true",
    "includeTopBettingOpportunity": 1,
    "topBookmaker": 1
}

# Group-specific parameters
def build_group_params(group):
    return {
        **DEFAULT_PARAMS,
        "competitors": group.team_id,  # Team/Club ID for home games
        "competitionId": group.competition_id,
        "seasonNum": group.season_num
    }
```

### Core Functions
- [ ] `fetch_games_for_group(group_id)` - Fetch games using group's API settings
- [ ] `get_home_games(api_data, team_id)` - Filter home games from API response
- [ ] `store_games_in_db(games_data, group_id)` - Store games for specific group
- [ ] `sync_group_games(group_id)` - Complete sync process for a group
- [ ] `update_game_status(game_id)` - Update individual game from API

### Database Schema for API Data
```sql
-- Groups table additions
ALTER TABLE groups ADD COLUMN season_num INTEGER;
ALTER TABLE groups ADD COLUMN competition_id INTEGER;
ALTER TABLE groups ADD COLUMN team_id INTEGER;

-- Games table enhancements
ALTER TABLE games ADD COLUMN group_id INTEGER REFERENCES groups(id);
ALTER TABLE games ADD COLUMN api_sync_timestamp TIMESTAMP;
ALTER TABLE games ADD COLUMN last_updated TIMESTAMP;
```

## 🔄 API Endpoints

### Authentication Endpoints
- [x] `POST /auth/register` - User registration
- [x] `POST /auth/login` - User login
- [x] `POST /auth/logout` - User logout
- [x] `POST /auth/refresh` - Token refresh
- [x] `POST /auth/forgot-password` - Password reset request
- [x] `POST /auth/reset-password` - Password reset

### User Management Endpoints
- [x] `GET /users/profile` - Get user profile
- [x] `PUT /users/profile` - Update user profile
- [x] `GET /users` - List users (admin only)
- [x] `GET /users/{id}` - Get user by ID (admin only)
- [x] `PUT /users/{id}` - Update user by ID (admin only)
- [x] `DELETE /users/{id}` - Delete user by ID (admin only)
- [x] `POST /users` - Create user (admin only)
- [x] `POST /users/bulk-delete` - Bulk delete users (admin only)
- [x] `PUT /users/bulk-update` - Bulk update users (admin only)
- [x] `PATCH /users/{id}/toggle-active` - Toggle user status (admin only)
- [x] `GET /users/stats/active` - Get user statistics (admin only)
- [ ] `GET /users/settings` - Get user settings
- [ ] `PUT /users/settings` - Update user settings
- [x] `DELETE /users/account` - Delete user account

### Group Management Endpoints
- [x] `POST /groups` - Create new group
- [x] `GET /groups` - List user's groups
- [x] `GET /groups/{id}` - Get group details
- [x] `DELETE /groups/{id}` - Delete group
- [x] `GET /groups/{id}/members` - List group members
- [x] `POST /groups/{id}/admins/{user_id}` - Add admin
- [x] `DELETE /groups/{id}/members/{user_id}` - Remove member
- [x] `DELETE /groups/{id}/leave` - Leave group

### Invitation Endpoints
- [x] `POST /groups/{id}/invites` - Create invite token
- [x] `POST /groups/join/{token}` - Join with token
- [x] `POST /groups/invites/{token}/revoke` - Revoke invite

### Club Association Endpoints
- [x] `GET /groups/clubs` - List available clubs (from 365scores)
- [ ] `GET /clubs/{id}` - Get club details
- [ ] `POST /groups/{id}/club` - Associate group with club
- [ ] `DELETE /groups/{id}/club` - Remove club association

### Game Management Endpoints
- [ ] `GET /games` - List games (with filters)
- [ ] `GET /games/{id}` - Get game details
- [ ] `GET /groups/{id}/games` - Get group's home games from 365scores
- [ ] `POST /games/sync` - Sync season games for a group
- [ ] `GET /groups/{id}/games/sync` - Sync games for specific group
- [ ] `POST /groups/{id}/games/configure` - Configure group's API settings (season, competition, team)

### Seat Duty Endpoints
- [ ] `GET /games/{id}/duties` - List game duties
- [ ] `POST /games/{id}/duties` - Create seat duty
- [ ] `PUT /duties/{id}` - Update duty
- [ ] `DELETE /duties/{id}` - Delete duty
- [ ] `POST /duties/{id}/join` - Join duty
- [ ] `DELETE /duties/{id}/leave` - Leave duty
- [ ] `GET /users/{id}/duties` - User's duties

## 🧪 Testing & Quality Assurance

### Testing Strategy
- [x] **Unit Tests**
  - Database operations testing
  - Business logic validation
  - API endpoint testing
  - Error handling verification

- [x] **Integration Tests**
  - End-to-end workflow testing
  - Database integration testing
  - External API integration
  - Authentication flow testing

- [ ] **Performance Testing**
  - Load testing for concurrent users
  - Database performance optimization
  - API response time optimization
  - Memory usage optimization

## 🚀 Deployment & Infrastructure

### Deployment Setup
- [ ] **Docker Configuration**
  - Containerized application
  - Database container setup
  - Environment configuration
  - Docker Compose orchestration

- [ ] **Database Setup**
  - PostgreSQL configuration
  - Database migration scripts
  - Initial data seeding
  - Backup and recovery procedures

- [ ] **API Documentation**
  - OpenAPI/Swagger documentation
  - Endpoint documentation
  - Authentication guide
  - Usage examples

## 📊 Monitoring & Analytics

### System Monitoring
- [ ] **Logging System**
  - Application logging
  - Error tracking
  - Performance monitoring
  - User activity tracking

- [ ] **Analytics**
  - User engagement metrics
  - Group activity statistics
  - Duty completion rates
  - System usage patterns

## 🔒 Security & Compliance

### Security Measures
- [ ] **Data Protection**
  - Password encryption
  - Data encryption at rest
  - Secure API communication
  - Input validation and sanitization

- [ ] **Access Control**
  - Role-based permissions
  - API rate limiting
  - CORS configuration
  - Security headers implementation

---

## ✅ Recently Completed Features

### Group Management System (COMPLETED)
- ✅ Group creation with 2-group limit per user
- ✅ Group deletion (creator/admin only)
- ✅ Member management (add/remove/leave)
- ✅ Admin promotion system
- ✅ Token-based invitations (no email)
- ✅ WhatsApp-like group behavior
- ✅ Club integration with 365scores API
- ✅ Comprehensive test coverage

### User Management (COMPLETED)
- ✅ User registration and authentication
- ✅ Profile management
- ✅ Admin user management
- ✅ Superuser promotion system
- ✅ Account deletion

### API Endpoints (COMPLETED)
- ✅ All authentication endpoints
- ✅ All user management endpoints
- ✅ All group management endpoints
- ✅ All invitation endpoints
- ✅ Club fetching endpoints

## Priority Levels
- 🔴 **High Priority**: Core functionality (Users, Groups, Authentication) ✅
- 🟡 **Medium Priority**: Advanced features (Invitations, Club Association) ✅
- 🟢 **Low Priority**: Nice-to-have features (Analytics, Advanced Settings)

## Estimated Timeline
- **Phase 1** (Core System): 2-3 weeks
- **Phase 2** (Group Management): 1-2 weeks  
- **Phase 3** (Seat Duty System): 1-2 weeks
- **Phase 4** (Advanced Features): 1-2 weeks
- **Phase 5** (Testing & Polish): 1 week

**Total Estimated Time**: 6-10 weeks
