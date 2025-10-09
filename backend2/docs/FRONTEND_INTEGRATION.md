# Frontend Integration Guide - Club Management

## 🎯 Quick Start

The club management system is now ready! Here's where you need to integrate it in your frontend.

---

## 📍 Integration Points

### 1. Group Creation Flow (BEFORE creating the group)

**Location**: When user clicks "Create Group" button, show a multi-step wizard:

#### Step 1: Select Country
```typescript
// API Call
const response = await fetch(`${API_BASE}/clubs/countries`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const countries = await response.json();

// countries: Array<{ id: number, name: string, has_league: boolean }>
```

**UI Component Needed**: Dropdown or searchable list of countries

---

#### Step 2: Select Competition/League
```typescript
// API Call (triggered when user selects a country)
const response = await fetch(
  `${API_BASE}/clubs/competitions?country_id=${selectedCountryId}`,
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);
const competitions = await response.json();

// competitions: Array<{
//   id: number,
//   name: string,
//   image_path: string,
//   country_id: number,
//   current_season_num: number,
//   current_stage_num: number
// }>
```

**UI Component Needed**: Grid or list of competitions with logos

---

#### Step 3: Select Team
```typescript
// API Call (triggered when user selects a competition)
const response = await fetch(
  `${API_BASE}/clubs/teams?competition_id=${selectedCompetitionId}`,
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);
const teams = await response.json();

// teams: Array<{
//   id: number,
//   name: string,
//   image_url: string,
//   country_name: string
// }>
```

**UI Component Needed**: Searchable list/grid of teams with logos

---

#### Step 4: Create Club & Group
```typescript
// First, create/register the club
const clubParams = new URLSearchParams({
  team_id: selectedTeam.id.toString(),
  team_name: selectedTeam.name,
  team_image_url: selectedTeam.image_url || '',
  country_name: selectedCountry.name,
  country_id: selectedCountry.id.toString(),
  competition_id: selectedCompetition.id.toString(),
  competition_name: selectedCompetition.name
});

const clubResponse = await fetch(
  `${API_BASE}/clubs/create-from-team?${clubParams}`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

if (!clubResponse.ok) {
  throw new Error('Failed to create club');
}

const club = await clubResponse.json();

// Now create the group with the club
const groupResponse = await fetch(`${API_BASE}/groups`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    name: groupName,
    description: groupDescription,
    club_id: club.id  // <-- This links the group to the club
  })
});

const group = await groupResponse.json();
```

---

## 🎨 UI Flow Example

```
┌─────────────────────────────────────┐
│  Create New Group                   │
├─────────────────────────────────────┤
│                                     │
│  Step 1: Choose Your Country       │
│  ┌─────────────────────────────┐  │
│  │ 🇬🇧 England                  │  │
│  │ 🇪🇸 Spain                    │  │
│  │ 🇩🇪 Germany                  │  │
│  └─────────────────────────────┘  │
│                                     │
│         [Next] [Cancel]             │
└─────────────────────────────────────┘

            ↓ (User selects England)

┌─────────────────────────────────────┐
│  Create New Group                   │
├─────────────────────────────────────┤
│                                     │
│  Step 2: Choose Competition         │
│  ┌─────────────────────────────┐  │
│  │ [⚽] Premier League          │  │
│  │ [⚽] Championship            │  │
│  │ [⚽] League One              │  │
│  └─────────────────────────────┘  │
│                                     │
│      [Back] [Next] [Cancel]         │
└─────────────────────────────────────┘

            ↓ (User selects Premier League)

┌─────────────────────────────────────┐
│  Create New Group                   │
├─────────────────────────────────────┤
│                                     │
│  Step 3: Choose Your Team           │
│  Search: [____________]             │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ [🔴] Manchester United       │  │
│  │ [⚪] Manchester City         │  │
│  │ [⚪] Arsenal                  │  │
│  │ [⚪] Chelsea                  │  │
│  └─────────────────────────────┘  │
│                                     │
│      [Back] [Next] [Cancel]         │
└─────────────────────────────────────┘

            ↓ (User selects Manchester United)

┌─────────────────────────────────────┐
│  Create New Group                   │
├─────────────────────────────────────┤
│                                     │
│  Step 4: Group Details              │
│                                     │
│  Team: [🔴] Manchester United       │
│                                     │
│  Group Name:                        │
│  [_________________________]        │
│                                     │
│  Description:                       │
│  [_________________________]        │
│  [_________________________]        │
│                                     │
│    [Back] [Create Group] [Cancel]   │
└─────────────────────────────────────┘
```

---

## 📦 TypeScript Types

```typescript
// Add these to your types file

export interface Country {
  id: number;
  name: string;
  has_league: boolean;
}

export interface Competition {
  id: number;
  name: string;
  image_path: string | null;
  country_id: number | null;
  current_season_num: number | null;
  current_stage_num: number | null;
}

export interface Team {
  id: number;
  name: string;
  image_url: string | null;
  country_name: string | null;
}

export interface Club {
  id: number;
  name: string;
  external_id: string;
  logo: string | null;
  country: string | null;
  country_id: string | null;
  competition_id: string | null;
  competition_name: string | null;
}

export interface Group {
  id: number;
  name: string;
  description: string | null;
  creator_id: number;
  club_id: number | null;
}
```

---

## 🔧 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/clubs/countries` | GET | Get list of countries |
| `/clubs/competitions?country_id={id}` | GET | Get competitions for a country |
| `/clubs/teams?competition_id={id}` | GET | Get teams in a competition |
| `/clubs/create-from-team?team_id={id}&team_name={name}&...` | POST | Register a club |
| `/groups` | POST | Create group with `club_id` |

---

## ✅ What's Already Done (Backend)

✅ All API endpoints are implemented  
✅ Caching system (24 hours) to avoid excessive API calls  
✅ Database models and migrations  
✅ Group-Club association  
✅ Error handling and validation  

---

## 🚀 What You Need to Do (Frontend)

1. **Create UI Components**:
   - Country selector
   - Competition selector  
   - Team selector (with search)
   - Group creation form

2. **Update Group Creation Flow**:
   - Make it a multi-step wizard
   - Add club selection before final group creation
   - Store selected club data in state

3. **Update Group Display**:
   - Show club logo/name in group cards
   - Display club info in group details page

4. **Optional Enhancements**:
   - Add "Skip" option to create group without club
   - Show club in group listings
   - Filter groups by club

---

## 🎯 Files to Modify

### Frontend Files to Create/Update:

1. **`app/components/ClubSelectionWizard.tsx`** (NEW)
   - Multi-step form for country → competition → team selection

2. **`app/types/club.ts`** (NEW)
   - TypeScript interfaces for Club, Country, Competition, Team

3. **`app/components/GroupCreationModal.tsx`** (UPDATE)
   - Integrate ClubSelectionWizard before group name/description

4. **`app/components/GroupCard.tsx`** (UPDATE)
   - Display club logo/name if group has a club

---

## 💡 Tips

1. **Caching**: The backend caches API responses for 24 hours. No need to implement frontend caching.

2. **Loading States**: Show loading spinners while fetching countries/competitions/teams.

3. **Error Handling**: The backend returns cached data if 365scores API fails. Handle 503 errors gracefully.

4. **Search**: For teams list, implement client-side search since all teams are loaded at once.

5. **Images**: Team logos come from the `image_url` field. Competition logos from `image_path`.

---

## 📞 Need Help?

All the backend work is complete. The data is ready to be consumed. Just follow the flow above and you'll have a working club management system!

