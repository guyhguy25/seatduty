export type Root = Root2[]

export interface Root2 {
  lastUpdateId: number
  requestedUpdateId: number
  ttl: number
  paging: Paging
  summary: Summary
  competitionFilters: CompetitionFilter[]
  sports: Sport[]
  countries: Country[]
  competitions: Competition[]
  competitors: Competitor[]
  games: Game[]
  bookmakers: Bookmaker2[]
}

export interface Paging {
  previousPage: string
  nextPage: string
}

export interface Summary {}

export interface CompetitionFilter {
  id: number
  countryId: number
  sportId: number
  name: string
  hasBrackets: boolean
  nameForURL: string
  popularityRank: number
  imageVersion: number
  currentStageType: number
  color: string
  competitorsType: number
  currentPhaseNum: number
  currentSeasonNum: number
  currentStageNum: number
  hideOnCatalog: boolean
  hideOnSearch: boolean
  isInternational: boolean
  currentPhaseName?: string
}

export interface Sport {
  id: number
  name: string
  nameForURL: string
  drawSupport: boolean
  imageVersion: number
}

export interface Country {
  id: number
  name: string
  totalGames?: number
  liveGames?: number
  nameForURL: string
  imageVersion: number
  isInternational?: boolean
}

export interface Competition {
  id: number
  countryId: number
  sportId: number
  name: string
  hasStandings?: boolean
  hasLiveStandings?: boolean
  hasStandingsGroups?: boolean
  hasBrackets: boolean
  nameForURL: string
  totalGames?: number
  liveGames?: number
  popularityRank: number
  hasActiveGames?: boolean
  imageVersion: number
  currentStageType: number
  color: string
  competitorsType: number
  currentPhaseNum: number
  currentSeasonNum: number
  currentStageNum: number
  hideOnCatalog: boolean
  hideOnSearch: boolean
  isInternational: boolean
  currentPhaseName?: string
}

export interface Competitor {
  id: number
  countryId: number
  sportId: number
  name: string
  symbolicName: string
  nameForURL: string
  type: number
  popularityRank: number
  imageVersion: number
  color: string
  awayColor?: string
  mainCompetitionId: number
  hasSquad: boolean
  hasTransfers: boolean
  competitorNum: number
  hideOnSearch: boolean
  hideOnCatalog: boolean
  shortName?: string
}

export interface Game {
  id: number
  sportId: number
  competitionId: number
  seasonNum: number
  stageNum: number
  roundNum: number
  roundName: string
  competitionDisplayName: string
  startTime: string
  statusGroup: number
  statusText: string
  shortStatusText: string
  gameTimeAndStatusDisplayType: number
  justEnded: boolean
  gameTime: number
  gameTimeDisplay: string
  hasLineups?: boolean
  hasMissingPlayers?: boolean
  hasFieldPositions?: boolean
  hasTVNetworks: boolean
  hasLiveStreaming?: boolean
  showCountdown?: boolean
  odds?: Odds
  homeCompetitor: HomeCompetitor
  awayCompetitor: AwayCompetitor
  isHomeAwayInverted: boolean
  hasStats: boolean
  hasStandings: boolean
  standingsName: string
  hasBrackets: boolean
  hasPreviousMeetings: boolean
  hasRecentMatches: boolean
  hasBets?: boolean
  hasPlayerBets?: boolean
  winner: number
  homeAwayTeamOrder: number
  hasNews?: boolean
  hasPointByPoint: boolean
  hasVideo: boolean
}

export interface Odds {
  lineId: number
  gameId: number
  bookmakerId: number
  lineTypeId: number
  lineType: LineType
  link: string
  bookmaker: Bookmaker
  options: Option[]
}

export interface LineType {
  id: number
  name: string
  title: string
  internalOptionType: number
}

export interface Bookmaker {
  id: number
  name: string
  link: string
  nameForURL: string
  actionButton: ActionButton
  color: string
  imageVersion: number
  promotionText: string
}

export interface ActionButton {
  link: string
  label: string
}

export interface Option {
  num: number
  name: string
  rate: Rate
  oldRate: OldRate
  link: string
  trend: number
}

export interface Rate {
  decimal: number
  fractional: string
  american: string
}

export interface OldRate {
  decimal: number
  fractional: string
  american: string
}

export interface HomeCompetitor {
  id: number
  countryId: number
  sportId: number
  name: string
  symbolicName: string
  score: number
  isQualified: boolean
  toQualify: boolean
  isWinner: boolean
  nameForURL: string
  type: number
  popularityRank: number
  imageVersion: number
  color: string
  awayColor?: string
  mainCompetitionId: number
  hasSquad: boolean
  hasTransfers: boolean
  competitorNum: number
  hideOnSearch: boolean
  hideOnCatalog: boolean
  shortName?: string
}

export interface AwayCompetitor {
  id: number
  countryId: number
  sportId: number
  name: string
  symbolicName: string
  score: number
  isQualified: boolean
  toQualify: boolean
  isWinner: boolean
  nameForURL: string
  type: number
  popularityRank: number
  imageVersion: number
  color: string
  awayColor?: string
  mainCompetitionId: number
  hasSquad: boolean
  hasTransfers: boolean
  competitorNum: number
  hideOnSearch: boolean
  hideOnCatalog: boolean
  shortName?: string
}

export interface Bookmaker2 {
  id: number
  name: string
  link: string
  nameForURL: string
  actionButton: ActionButton2
  color: string
  imageVersion: number
  promotionText: string
}

export interface ActionButton2 {
  link: string
  label: string
}
