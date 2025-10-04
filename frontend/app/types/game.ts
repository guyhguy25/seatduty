export interface Root {
  assignedUserId: number[]
  assigned_user_names: string[]
  awayCompetitor: AwayCompetitor
  competitionDisplayName: string
  competitionId: number
  gameTime: number
  gameTimeAndStatusDisplayType: number
  gameTimeDisplay: string
  hasBets: boolean
  hasBrackets: boolean
  hasFieldPositions: boolean
  hasLineups: boolean
  hasLiveStreaming: boolean
  hasMissingPlayers: boolean
  hasNews: boolean
  hasPlayerBets: boolean
  hasPointByPoint: boolean
  hasPreviousMeetings: boolean
  hasRecentMatches: boolean
  hasStandings: boolean
  hasStats: boolean
  hasTVNetworks: boolean
  hasVideo: boolean
  homeAwayTeamOrder: number
  homeCompetitor: HomeCompetitor
  id: number
  isHomeAwayInverted: boolean
  justEnded: boolean
  odds: Odds
  roundName: string
  roundNum: number
  seasonNum: number
  shortStatusText: string
  showCountdown: boolean
  sportId: number
  stageNum: number
  standingsName: string
  startTime: string
  statusGroup: number
  statusText: string
  winner: number
}

export interface AwayCompetitor {
  awayColor: string
  color: string
  competitorNum: number
  countryId: number
  hasSquad: boolean
  hasTransfers: boolean
  hideOnCatalog: boolean
  hideOnSearch: boolean
  id: number
  imageVersion: number
  isQualified: boolean
  isWinner: boolean
  mainCompetitionId: number
  name: string
  nameForURL: string
  popularityRank: number
  score: number
  sportId: number
  symbolicName: string
  toQualify: boolean
  type: number
}

export interface HomeCompetitor {
  awayColor: string
  color: string
  competitorNum: number
  countryId: number
  hasSquad: boolean
  hasTransfers: boolean
  hideOnCatalog: boolean
  hideOnSearch: boolean
  id: number
  imageVersion: number
  isQualified: boolean
  isWinner: boolean
  mainCompetitionId: number
  name: string
  nameForURL: string
  popularityRank: number
  score: number
  sportId: number
  symbolicName: string
  toQualify: boolean
  type: number
}

export interface Odds {
  bookmaker: Bookmaker
  bookmakerId: number
  gameId: number
  lineId: number
  lineType: LineType
  lineTypeId: number
  link: string
  options: Option[]
}

export interface Bookmaker {
  actionButton: ActionButton
  color: string
  id: number
  imageVersion: number
  link: string
  name: string
  nameForURL: string
  promotionText: string
}

export interface ActionButton {
  label: string
  link: string
}

export interface LineType {
  id: number
  internalOptionType: number
  name: string
  title: string
}

export interface Option {
  link: string
  name: string
  num: number
  oldRate: OldRate
  rate: Rate
  trend: number
}

export interface OldRate {
  american: string
  decimal: number
  fractional: string
}

export interface Rate {
  american: string
  decimal: number
  fractional: string
}

// Legacy Game interface for backward compatibility
export interface Game {
  id: number;
  game_id: string;
  start_time: string;
  home_team: string;
  away_team: string;
  homeId: string;
  awayId: string;
  assigned_group: string;
  created_at: string;
}

// User interface
export interface User {
  id: number;
  email: string;
  name: string;
  is_active: boolean;
  last_assigned_at: string;
  total_games_assigned: number;
  total_games_completed: number;
}

// Assignment interface
export interface Assignment {
  id: number;
  user_id: number;
  user_name: string;
  game_id: number;
  home_competitor_name: string;
  away_competitor_name: string;
  start_time: string;
  assigned_at: string;
  status: string;
}
