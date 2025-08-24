// Sports Web API (Go + net/http)
// Theme: Football (Soccer) teams and players
// Endpoints:
//   GET /health
//   GET /api/teams
//   GET /api/teams/{id}
//   GET /api/players
//   GET /api/players/{id}
//   GET /api/stats/summary
// Query features: filter, search (q), sort, pagination (page, per_page)
// CORS: enabled for GET from any origin (for local docs)
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"net/url"
	"os"
	"sort"
	"strconv"
	"strings"
	"time"
)

// ---- Models ----

type Team struct {
	ID       int     `json:"id"`
	Name     string  `json:"name"`
	Country  string  `json:"country"`
	League   string  `json:"league"`
	Rating   float64 `json:"rating"`   // 0-100
	Founded  int     `json:"founded"`  // year
	Stadium  string  `json:"stadium"`
}

type Player struct {
	ID          int     `json:"id"`
	TeamID      int     `json:"team_id"`
	Name        string  `json:"name"`
	Position    string  `json:"position"` // GK, DF, MF, FW
	Age         int     `json:"age"`
	Nationality string  `json:"nationality"`
	Rating      float64 `json:"rating"`   // 0-100
	ValueUSD    int     `json:"value"`    // in USD
	JerseyNo    int     `json:"jersey_no"`
}

type APIError struct {
	Error string `json:"error"`
	Field string `json:"field,omitempty"`
}

type ListMeta struct {
	Page    int    `json:"page"`
	PerPage int    `json:"per_page"`
	Total   int    `json:"total"`
	Sort    string `json:"sort,omitempty"`
}

type Links struct {
	Self string `json:"self,omitempty"`
	Next string `json:"next,omitempty"`
	Prev string `json:"prev,omitempty"`
}

type ListResponse[T any] struct {
	Meta  ListMeta `json:"meta"`
	Data  []T      `json:"data"`
	Links Links    `json:"links"`
}

// ---- In-memory dataset ----

var teams []Team
var players []Player

var leagues = []string{
	"Premier League", "La Liga", "Serie A", "Bundesliga", "Ligue 1", "Eredivisie", "J1 League",
}
var countries = []string{
	"England", "Spain", "Italy", "Germany", "France", "Netherlands", "Japan", "Brazil", "Argentina",
}
var positions = []string{"GK", "DF", "MF", "FW"}

func seedData() {
	// Deterministic for repeatability (change to time.Now().UnixNano() for random each run)
	r := rand.New(rand.NewSource(42))

	stadiums := []string{
		"National Stadium", "City Arena", "River Park", "Sky Dome", "Liberty Field",
		"Metropolitan Ground", "Sunshine Park", "Harbor Stadium",
	}
	teamNames := []string{
		"Lions", "Tigers", "Eagles", "Sharks", "Wolves", "Falcons", "Bulls", "Dragons",
		"Kings", "United", "Athletic", "Rangers", "City", "County",
	}

	teams = teams[:0]
	players = players[:0]

	// ~70 teams
	id := 1
	for _, lg := range leagues {
		for i := 0; i < 10; i++ {
			name := fmt.Sprintf("%s %s", pick(r, []string{"FC", "SC", "AC", "Sporting", "Real", "CD"}), pick(r, teamNames))
			teams = append(teams, Team{
				ID:      id,
				Name:    name,
				Country: pick(r, countries),
				League:  lg,
				Rating:  round2(r.Float64()*30 + 60), // 60-90
				Founded: 1890 + r.Intn(130),          // 1890-2020
				Stadium: pick(r, stadiums),
			})
			id++
		}
	}

	// players (~1,400)
	playerID := 1
	for _, t := range teams {
		n := 15 + r.Intn(11) // 15-25
		for j := 0; j < n; j++ {
			pos := pick(r, positions)
			age := 17 + r.Intn(23) // 17-39
			value := 500_000 + r.Intn(100_000_000) // 0.5M - 100.5M
			players = append(players, Player{
				ID:          playerID,
				TeamID:      t.ID,
				Name:        fakeName(r),
				Position:    pos,
				Age:         age,
				Nationality: pick(r, countries),
				Rating:      round2(r.Float64()*35 + 55), // 55-90
				ValueUSD:    value,
				JerseyNo:    1 + r.Intn(30),
			})
			playerID++
		}
	}
}

func pick[T any](r *rand.Rand, arr []T) T { return arr[r.Intn(len(arr))] }

func round2(f float64) float64 { return float64(int(f*100+0.5)) / 100.0 }

func fakeName(r *rand.Rand) string {
	firsts := []string{"Alex", "Leo", "Kai", "Riku", "Noah", "Mia", "Yuna", "Sora", "Ren", "Emma", "Oliver", "Lucas", "Ava", "Sophia", "Mason"}
	lasts := []string{"Tanaka", "Suzuki", "Sato", "Kobayashi", "Watanabe", "Smith", "Garcia", "Lopez", "Miller", "Johnson", "Schneider", "Rossi", "Dubois"}
	return fmt.Sprintf("%s %s", pick(r, firsts), pick(r, lasts))
}

// ---- Utilities ----

func writeJSON(w http.ResponseWriter, status int, v any) {
	// CORS (demo): allow all origins for GET and OPTIONS
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
	w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Cache-Control", "public, max-age=60")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(v)
}

func errorJSON(w http.ResponseWriter, status int, msg, field string) {
	writeJSON(w, status, APIError{Error: msg, Field: field})
}

func parseInt(q url.Values, key string, def int) int {
	s := strings.TrimSpace(q.Get(key))
	if s == "" {
		return def
	}
	n, err := strconv.Atoi(s)
	if err != nil {
		return def
	}
	return n
}

func parseFloat(q url.Values, key string, def float64) float64 {
	s := strings.TrimSpace(q.Get(key))
	if s == "" {
		return def
	}
	n, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return def
	}
	return n
}

func clamp(v, lo, hi int) int {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}

func parseTrailingID(path, prefix string) (int, bool) {
	if !strings.HasPrefix(path, prefix) {
		return 0, false
	}
	s := strings.TrimPrefix(path, prefix)
	if s == "" || strings.Contains(s, "/") {
		return 0, false
	}
	id, err := strconv.Atoi(s)
	if err != nil {
		return 0, false
	}
	return id, true
}

// Build clean next/prev links using url.Values (no trailing &)
func buildLink(basePath string, q url.Values, page, perPage int) string {
	v := url.Values{}
	for k, vals := range q {
		for _, val := range vals {
			if k == "page" || k == "per_page" {
				continue
			}
			v.Add(k, val)
		}
	}
	v.Set("page", strconv.Itoa(page))
	v.Set("per_page", strconv.Itoa(perPage))
	qs := v.Encode()
	if qs != "" {
		return fmt.Sprintf("%s?%s", basePath, qs)
	}
	return basePath
}

// ---- Handlers ----

func healthHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodOptions {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		w.WriteHeader(http.StatusNoContent)
		return
	}
	writeJSON(w, http.StatusOK, map[string]string{"status": "ok", "time": time.Now().UTC().Format(time.RFC3339)})
}

// GET /api/teams
// Filters: league, country, min_rating
// Search: q (name contains, case-insensitive)
// Sort: sort=name|-name|rating|-rating|founded|-founded (default: -rating)
// Pagination: page, per_page (<= 100)
func teamsListHandler(w http.ResponseWriter, r *http.Request) {
	q := r.URL.Query()
	qs := q.Encode()

	qParam := strings.TrimSpace(q.Get("q"))
	league := strings.TrimSpace(q.Get("league"))
	country := strings.TrimSpace(q.Get("country"))
	minRating := parseFloat(q, "min_rating", -1)
	sortKey := strings.TrimSpace(q.Get("sort"))
	if sortKey == "" {
		sortKey = "-rating"
	}
	page := clamp(parseInt(q, "page", 1), 1, 100000)
	perPage := clamp(parseInt(q, "per_page", 20), 1, 100)

	// Validate sort
	base := strings.TrimPrefix(sortKey, "-")
	allowed := map[string]bool{"name": true, "rating": true, "founded": true}
	if !allowed[base] {
		errorJSON(w, http.StatusBadRequest, "invalid sort key", "sort")
		return
	}

	filtered := make([]Team, 0, len(teams))
	for _, t := range teams {
		if qParam != "" && !strings.Contains(strings.ToLower(t.Name), strings.ToLower(qParam)) {
			continue
		}
		if league != "" && !strings.EqualFold(league, t.League) {
			continue
		}
		if country != "" && !strings.EqualFold(country, t.Country) {
			continue
		}
		if minRating >= 0 && t.Rating < minRating {
			continue
		}
		filtered = append(filtered, t)
	}

	sort.SliceStable(filtered, func(i, j int) bool {
		a, b := filtered[i], filtered[j]
		switch base {
		case "name":
			if strings.HasPrefix(sortKey, "-") {
				return strings.ToLower(a.Name) > strings.ToLower(b.Name)
			}
			return strings.ToLower(a.Name) < strings.ToLower(b.Name)
		case "rating":
			if strings.HasPrefix(sortKey, "-") {
				return a.Rating > b.Rating
			}
			return a.Rating < b.Rating
		case "founded":
			if strings.HasPrefix(sortKey, "-") {
				return a.Founded > b.Founded
			}
			return a.Founded < b.Founded
		default:
			return a.Rating > b.Rating
		}
	})

	total := len(filtered)
	start := (page - 1) * perPage
	if start > total {
		start = total
	}
	end := start + perPage
	if end > total {
		end = total
	}
	pageItems := filtered[start:end]

	resp := ListResponse[Team]{
		Meta: ListMeta{Page: page, PerPage: perPage, Total: total, Sort: sortKey},
		Data: pageItems,
		Links: Links{
			Self: buildLink("/api/teams", q, page, perPage),
		},
	}
	if end < total {
		resp.Links.Next = buildLink("/api/teams", q, page+1, perPage)
	}
	if page > 1 {
		resp.Links.Prev = buildLink("/api/teams", q, page-1, perPage)
	}
	_ = qs // for clarity; we now use buildLink
	writeJSON(w, http.StatusOK, resp)
}

// GET /api/teams/{id}
func teamDetailHandler(w http.ResponseWriter, r *http.Request) {
	id, ok := parseTrailingID(r.URL.Path, "/api/teams/")
	if !ok {
		errorJSON(w, http.StatusNotFound, "not found", "")
		return
	}
	for _, t := range teams {
		if t.ID == id {
			writeJSON(w, http.StatusOK, t)
			return
		}
	}
	errorJSON(w, http.StatusNotFound, "team not found", "id")
}

// GET /api/players
// Filters: team_id, position, nationality, min_rating, max_age
// Search: q (name contains)
// Sort: sort=name|-name|rating|-rating|age|-age|value|-value (default: -rating)
// Pagination: page, per_page
func playersListHandler(w http.ResponseWriter, r *http.Request) {
	q := r.URL.Query()

	qParam := strings.TrimSpace(q.Get("q"))
	teamID := parseInt(q, "team_id", -1)
	position := strings.ToUpper(strings.TrimSpace(q.Get("position")))
	nationality := strings.TrimSpace(q.Get("nationality"))
	minRating := parseFloat(q, "min_rating", -1)
	maxAge := parseInt(q, "max_age", -1)

	sortKey := strings.TrimSpace(q.Get("sort"))
	if sortKey == "" {
		sortKey = "-rating"
	}
	page := clamp(parseInt(q, "page", 1), 1, 100000)
	perPage := clamp(parseInt(q, "per_page", 20), 1, 100)

	// Validate sort
	base := strings.TrimPrefix(sortKey, "-")
	allowed := map[string]bool{"name": true, "rating": true, "age": true, "value": true}
	if !allowed[base] {
		errorJSON(w, http.StatusBadRequest, "invalid sort key", "sort")
		return
	}

	filtered := make([]Player, 0, len(players))
	for _, p := range players {
		if qParam != "" && !strings.Contains(strings.ToLower(p.Name), strings.ToLower(qParam)) {
			continue
		}
		if teamID >= 0 && p.TeamID != teamID {
			continue
		}
		if position != "" && strings.ToUpper(p.Position) != position {
			continue
		}
		if nationality != "" && !strings.EqualFold(p.Nationality, nationality) {
			continue
		}
		if minRating >= 0 && p.Rating < minRating {
			continue
		}
		if maxAge >= 0 && p.Age > maxAge {
			continue
		}
		filtered = append(filtered, p)
	}

	sort.SliceStable(filtered, func(i, j int) bool {
		a, b := filtered[i], filtered[j]
		switch base {
		case "name":
			if strings.HasPrefix(sortKey, "-") {
				return strings.ToLower(a.Name) > strings.ToLower(b.Name)
			}
			return strings.ToLower(a.Name) < strings.ToLower(b.Name)
		case "rating":
			if strings.HasPrefix(sortKey, "-") {
				return a.Rating > b.Rating
			}
			return a.Rating < b.Rating
		case "age":
			if strings.HasPrefix(sortKey, "-") {
				return a.Age > b.Age
			}
			return a.Age < b.Age
		case "value":
			if strings.HasPrefix(sortKey, "-") {
				return a.ValueUSD > b.ValueUSD
			}
			return a.ValueUSD < b.ValueUSD
		default:
			return a.Rating > b.Rating
		}
	})

	total := len(filtered)
	start := (page - 1) * perPage
	if start > total {
		start = total
	}
	end := start + perPage
	if end > total {
		end = total
	}
	pageItems := filtered[start:end]

	resp := ListResponse[Player]{
		Meta:  ListMeta{Page: page, PerPage: perPage, Total: total, Sort: sortKey},
		Data:  pageItems,
		Links: Links{Self: buildLink("/api/players", q, page, perPage)},
	}
	if end < total {
		resp.Links.Next = buildLink("/api/players", q, page+1, perPage)
	}
	if page > 1 {
		resp.Links.Prev = buildLink("/api/players", q, page-1, perPage)
	}
	writeJSON(w, http.StatusOK, resp)
}

// GET /api/players/{id}
func playerDetailHandler(w http.ResponseWriter, r *http.Request) {
	id, ok := parseTrailingID(r.URL.Path, "/api/players/")
	if !ok {
		errorJSON(w, http.StatusNotFound, "not found", "")
		return
	}
	for _, p := range players {
		if p.ID == id {
			writeJSON(w, http.StatusOK, p)
			return
		}
	}
	errorJSON(w, http.StatusNotFound, "player not found", "id")
}

// GET /api/stats/summary
type Summary struct {
	TotalTeams        int            `json:"total_teams"`
	TotalPlayers      int            `json:"total_players"`
	AvgTeamRating     float64        `json:"avg_team_rating"`
	AvgPlayerRating   float64        `json:"avg_player_rating"`
	TeamsPerLeague    map[string]int `json:"teams_per_league"`
	TopTeamsByRating  []Team         `json:"top_teams_by_rating"`
	TopPlayersByValue []Player       `json:"top_players_by_value"`
}

func statsSummaryHandler(w http.ResponseWriter, r *http.Request) {
	sum := Summary{
		TotalTeams:     len(teams),
		TotalPlayers:   len(players),
		TeamsPerLeague: map[string]int{},
	}
	var sumTeam, sumPlayer float64
	for _, t := range teams {
		sumTeam += t.Rating
		sum.TeamsPerLeague[t.League]++
	}
	for _, p := range players {
		sumPlayer += p.Rating
	}
	if len(teams) > 0 {
		sum.AvgTeamRating = round2(sumTeam / float64(len(teams)))
	}
	if len(players) > 0 {
		sum.AvgPlayerRating = round2(sumPlayer / float64(len(players)))
	}

	// Top 5 teams by rating
	topTeams := make([]Team, len(teams))
	copy(topTeams, teams)
	sort.Slice(topTeams, func(i, j int) bool { return topTeams[i].Rating > topTeams[j].Rating })
	if len(topTeams) > 5 {
		topTeams = topTeams[:5]
	}
	sum.TopTeamsByRating = topTeams

	// Top 5 players by value
	topPlayers := make([]Player, len(players))
	copy(topPlayers, players)
	sort.Slice(topPlayers, func(i, j int) bool { return topPlayers[i].ValueUSD > topPlayers[j].ValueUSD })
	if len(topPlayers) > 5 {
		topPlayers = topPlayers[:5]
	}
	sum.TopPlayersByValue = topPlayers

	writeJSON(w, http.StatusOK, sum)
}

// ---- Router / Server ----

func router(w http.ResponseWriter, r *http.Request) {
	// Simple CORS preflight for docs
	if r.Method == http.MethodOptions {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type")
		w.WriteHeader(http.StatusNoContent)
		return
	}

	path := r.URL.Path
	switch {
	case r.Method == http.MethodGet && path == "/health":
		healthHandler(w, r)
		return
	case r.Method == http.MethodGet && path == "/api/teams":
		teamsListHandler(w, r)
		return
	case r.Method == http.MethodGet && strings.HasPrefix(path, "/api/teams/"):
		teamDetailHandler(w, r)
		return
	case r.Method == http.MethodGet && path == "/api/players":
		playersListHandler(w, r)
		return
	case r.Method == http.MethodGet && strings.HasPrefix(path, "/api/players/"):
		playerDetailHandler(w, r)
		return
	case r.Method == http.MethodGet && path == "/api/stats/summary":
		statsSummaryHandler(w, r)
		return
	default:
		writeJSON(w, http.StatusNotFound, APIError{Error: "endpoint not found"})
	}
}

type statusWriter struct {
	http.ResponseWriter
	status int
}

func (w *statusWriter) WriteHeader(code int) {
	w.status = code
	w.ResponseWriter.WriteHeader(code)
}

func logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		sw := &statusWriter{ResponseWriter: w, status: 200}
		start := time.Now()
		next.ServeHTTP(sw, r)
		log.Printf("%s %s %d %v", r.Method, r.URL.String(), sw.status, time.Since(start))
	})
}

func main() {
	seedData()

	port := os.Getenv("PORT")
	if port == "" {
		port = "8000"
	}
	addr := ":" + port

	// Serve docs under /docs (so you can open http://localhost:8000/docs/)
	fs := http.FileServer(http.Dir("./docs"))

	mux := http.NewServeMux()
	mux.HandleFunc("/", router)
	mux.Handle("/docs/", http.StripPrefix("/docs/", fs))
	mux.HandleFunc("/api/docs", func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/docs/", http.StatusFound)
	})

	log.Printf("Sports API server listening on %s", addr)
	log.Printf("Docs:   http://localhost:%s/docs/", port)
	log.Printf("Try:    http://localhost:%s/api/players?per_page=5", port)
	log.Printf("Health: http://localhost:%s/health", port)

	srv := &http.Server{
		Addr:              addr,
		Handler:           logging(mux),
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Fatal(srv.ListenAndServe())
}
