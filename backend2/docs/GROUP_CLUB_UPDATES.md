# 🏟️ Group-Club Association Updates

## ✅ What Was Added

### 1. Club Data in Group Responses ✅

**Before**: Groups only returned `club_id`
```json
{
  "id": 1,
  "name": "My Group",
  "club_id": 5
}
```

**After**: Groups now include full club details
```json
{
  "id": 1,
  "name": "My Group",
  "club_id": 5,
  "club": {
    "id": 5,
    "name": "Manchester United",
    "logo": "https://imagecache.365scores.com/.../1234",
    "country": "England",
    "country_id": "6",
    "competition_name": "Premier League",
    "symbolic_name": "MUN",
    "color": "#DA291C",
    "away_color": "#FFFFFF"
  }
}
```

---

### 2. New Admin Endpoint to Update Club Association ✅

**Endpoint**: `PATCH /groups/{group_id}/club`

**Purpose**: Allow group admins to change the club associated with a group

**Who Can Use**: Only group admins

**Request Body**:
```json
{
  "club_id": 5
}
```

Or to remove club association:
```json
{
  "club_id": null
}
```

**Response**: Returns updated group with club details

---

## 📝 API Changes

### Updated Endpoints

#### 1. `GET /groups/{group_id}`
**Enhanced**: Now includes full club object in response

**Example**:
```bash
GET /groups/1
Authorization: Bearer {token}

Response:
{
  "id": 1,
  "name": "Arsenal Fans",
  "description": "Group for Arsenal supporters",
  "creator_id": 2,
  "club_id": 3,
  "club": {
    "id": 3,
    "name": "Arsenal",
    "external_id": "1234",
    "logo": "https://imagecache.365scores.com/.../1234",
    "country": "England",
    "color": "#EF0107"
  }
}
```

---

#### 2. `GET /groups`
**Enhanced**: Now includes full club object for all groups in the list

**Example**:
```bash
GET /groups
Authorization: Bearer {token}

Response:
[
  {
    "id": 1,
    "name": "Arsenal Fans",
    "club_id": 3,
    "club": { ... }
  },
  {
    "id": 2,
    "name": "My Other Group",
    "club_id": null,
    "club": null
  }
]
```

---

#### 3. `PATCH /groups/{group_id}/club` (NEW)
**Purpose**: Update the club associated with a group

**Authorization**: Only group admins

**Request**:
```bash
PATCH /groups/1/club
Authorization: Bearer {token}
Content-Type: application/json

{
  "club_id": 5
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Arsenal Fans",
  "club_id": 5,
  "club": {
    "id": 5,
    "name": "Manchester United",
    ...
  }
}
```

**To Remove Club Association**:
```bash
PATCH /groups/1/club
Authorization: Bearer {token}
Content-Type: application/json

{
  "club_id": null
}
```

---

## 🔧 Schema Updates

### GroupOut Schema
```python
class GroupOut(GroupBase):
    id: int
    creator_id: int
    club_id: Optional[int] = None
    club: Optional['ClubOut'] = None  # ✅ NEW - Full club object
```

### UpdateGroupClub Schema (NEW)
```python
class UpdateGroupClub(BaseModel):
    club_id: Optional[int] = None
```

---

## 💻 Frontend Usage

### Display Club in Group Details

```typescript
interface Group {
  id: number;
  name: string;
  description: string;
  creator_id: number;
  club_id: number | null;
  club: Club | null;  // ✅ Now available!
}

// Usage
const GroupDetail = ({ group }: { group: Group }) => {
  return (
    <div>
      <h1>{group.name}</h1>
      {group.club && (
        <div className="club-info">
          <img src={group.club.logo} alt={group.club.name} />
          <h2>{group.club.name}</h2>
          <p>{group.club.competition_name}</p>
        </div>
      )}
    </div>
  );
};
```

---

### Update Group's Club (Admin Only)

```typescript
const updateGroupClub = async (groupId: number, clubId: number | null) => {
  const response = await fetch(`/groups/${groupId}/club`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ club_id: clubId })
  });
  
  return response.json();
};

// Usage
await updateGroupClub(1, 5); // Change to club ID 5
await updateGroupClub(1, null); // Remove club association
```

---

### Show Club in Group List

```typescript
const GroupList = ({ groups }: { groups: Group[] }) => {
  return (
    <div className="groups-grid">
      {groups.map(group => (
        <div key={group.id} className="group-card">
          <h3>{group.name}</h3>
          {group.club && (
            <div className="club-badge">
              <img src={group.club.logo} alt={group.club.name} />
              <span>{group.club.name}</span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
```

---

## 🧪 Testing

### Test Get Group with Club
```bash
curl -X GET "http://localhost:8000/groups/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: Group response includes `club` object with full club details.

---

### Test List Groups with Clubs
```bash
curl -X GET "http://localhost:8000/groups" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: All groups include `club` object if they have a club association.

---

### Test Update Group Club (Admin)
```bash
curl -X PATCH "http://localhost:8000/groups/1/club" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"club_id": 5}'
```

**Expected**: Returns updated group with new club details.

---

### Test Update Group Club - Remove Association
```bash
curl -X PATCH "http://localhost:8000/groups/1/club" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"club_id": null}'
```

**Expected**: Returns group with `club_id: null` and `club: null`.

---

### Test Update Club - Non-Admin (Should Fail)
```bash
curl -X PATCH "http://localhost:8000/groups/1/club" \
  -H "Authorization: Bearer NON_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"club_id": 5}'
```

**Expected**: `403 Forbidden - Admin access required`

---

## 🎨 UI/UX Improvements

With club data now included in group responses, you can:

1. **Display Club Logos** in group cards
2. **Show Team Colors** for branding
3. **Display Competition Info** (e.g., "Premier League")
4. **Filter Groups by Club** in the UI
5. **Show Club Stats** in group details

---

## 📋 Summary

| Feature | Status |
|---------|--------|
| Club data in GET /groups/{id} | ✅ Complete |
| Club data in GET /groups | ✅ Complete |
| Admin endpoint to update club | ✅ Complete |
| Schema updates | ✅ Complete |
| Validation (admin-only) | ✅ Complete |
| Support for removing club | ✅ Complete |

---

## 🔒 Security

- ✅ Only **group admins** can update club associations
- ✅ Club ID validation (club must exist)
- ✅ Group membership verification before showing club data
- ✅ Proper error messages for unauthorized access

---

## 📚 Files Modified

1. **`app/groups/schemas.py`**
   - Added `club` field to `GroupOut`
   - Added `UpdateGroupClub` schema

2. **`app/groups/routers.py`**
   - Updated `get_group` to load club relationship
   - Updated `list_my_groups` to load club relationships
   - Added `update_group_club` endpoint (PATCH)

3. **`GROUP_CLUB_UPDATES.md`** (NEW)
   - This documentation file

---

**Status**: ✅ Complete and Ready to Use

**Date**: October 9, 2025

