// Copyright 2026 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package main

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"sort"
	"strconv"
	"time"
)

// Redis layout, per user (the user id is the anonymous session id the frontend
// keeps in a cookie):
//
//	wl:<user>:index        HASH  field = list id, value = JSON metadata
//	wl:<user>:<list id>    ZSET  member = product id, score = added_at (unix)
//
// The sorted set gives de-duplication and "newest first" ordering for free.
// Both keys carry a TTL so that abandoned sessions (and load generator
// traffic) cannot grow the dataset forever.

var (
	errNotFound     = errors.New("wishlist not found")
	errTooManyLists = errors.New("too many wishlists for this user")
	errTooManyItems = errors.New("too many items in this wishlist")
)

const (
	maxListsPerUser = 20
	maxItemsPerList = 100
)

// Wishlist is the wire representation returned by the API. Items is only
// populated by GetWishlist; the list endpoints return counts instead.
type Wishlist struct {
	ID        string         `json:"id"`
	Name      string         `json:"name"`
	CreatedAt int64          `json:"created_at"`
	ItemCount int            `json:"item_count"`
	Items     []WishlistItem `json:"items"`
}

type WishlistItem struct {
	ProductID string `json:"product_id"`
	AddedAt   int64  `json:"added_at"`
}

// listMeta is what actually lives in the index hash.
type listMeta struct {
	Name      string `json:"name"`
	CreatedAt int64  `json:"created_at"`
}

type store struct {
	redis *redisClient
	ttl   time.Duration
}

func newStore(r *redisClient, ttl time.Duration) *store {
	return &store{redis: r, ttl: ttl}
}

func indexKey(user string) string { return "wl:" + user + ":index" }

func listKey(user, id string) string { return "wl:" + user + ":" + id }

func newID() (string, error) {
	b := make([]byte, 6)
	if _, err := rand.Read(b); err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}

func (s *store) touch(keys ...string) {
	if s.ttl <= 0 {
		return
	}
	secs := strconv.Itoa(int(s.ttl.Seconds()))
	for _, k := range keys {
		// Best effort: a failed TTL refresh must not fail the request.
		_, _ = s.redis.do("EXPIRE", k, secs)
	}
}

func (s *store) ping() error {
	_, err := s.redis.do("PING")
	return err
}

func (s *store) meta(user, id string) (*listMeta, error) {
	res, err := s.redis.do("HGET", indexKey(user), id)
	if err != nil {
		return nil, err
	}
	if res.null {
		return nil, errNotFound
	}
	var m listMeta
	if err := json.Unmarshal([]byte(res.str), &m); err != nil {
		return nil, err
	}
	return &m, nil
}

func (s *store) count(user, id string) (int, error) {
	res, err := s.redis.do("ZCARD", listKey(user, id))
	if err != nil {
		return 0, err
	}
	return int(res.num), nil
}

func (s *store) Create(user, name string) (*Wishlist, error) {
	existing, err := s.redis.do("HLEN", indexKey(user))
	if err != nil {
		return nil, err
	}
	if int(existing.num) >= maxListsPerUser {
		return nil, errTooManyLists
	}

	id, err := newID()
	if err != nil {
		return nil, err
	}
	m := listMeta{Name: name, CreatedAt: time.Now().Unix()}
	raw, err := json.Marshal(m)
	if err != nil {
		return nil, err
	}
	if _, err := s.redis.do("HSET", indexKey(user), id, string(raw)); err != nil {
		return nil, err
	}
	s.touch(indexKey(user))
	return &Wishlist{ID: id, Name: m.Name, CreatedAt: m.CreatedAt, Items: []WishlistItem{}}, nil
}

func (s *store) List(user string) ([]Wishlist, error) {
	res, err := s.redis.do("HGETALL", indexKey(user))
	if err != nil {
		return nil, err
	}
	fields := res.strings()
	out := make([]Wishlist, 0, len(fields)/2)
	for i := 0; i+1 < len(fields); i += 2 {
		var m listMeta
		if err := json.Unmarshal([]byte(fields[i+1]), &m); err != nil {
			continue // skip entries written by an older schema
		}
		n, err := s.count(user, fields[i])
		if err != nil {
			return nil, err
		}
		out = append(out, Wishlist{
			ID:        fields[i],
			Name:      m.Name,
			CreatedAt: m.CreatedAt,
			ItemCount: n,
			Items:     []WishlistItem{},
		})
	}
	sort.Slice(out, func(i, j int) bool { return out[i].CreatedAt > out[j].CreatedAt })
	return out, nil
}

func (s *store) Get(user, id string) (*Wishlist, error) {
	m, err := s.meta(user, id)
	if err != nil {
		return nil, err
	}
	res, err := s.redis.do("ZREVRANGE", listKey(user, id), "0", "-1", "WITHSCORES")
	if err != nil {
		return nil, err
	}
	raw := res.strings()
	items := make([]WishlistItem, 0, len(raw)/2)
	for i := 0; i+1 < len(raw); i += 2 {
		score, _ := strconv.ParseFloat(raw[i+1], 64)
		items = append(items, WishlistItem{ProductID: raw[i], AddedAt: int64(score)})
	}
	return &Wishlist{
		ID:        id,
		Name:      m.Name,
		CreatedAt: m.CreatedAt,
		ItemCount: len(items),
		Items:     items,
	}, nil
}

func (s *store) Rename(user, id, name string) (*Wishlist, error) {
	m, err := s.meta(user, id)
	if err != nil {
		return nil, err
	}
	m.Name = name
	raw, err := json.Marshal(m)
	if err != nil {
		return nil, err
	}
	if _, err := s.redis.do("HSET", indexKey(user), id, string(raw)); err != nil {
		return nil, err
	}
	s.touch(indexKey(user), listKey(user, id))
	n, err := s.count(user, id)
	if err != nil {
		return nil, err
	}
	return &Wishlist{ID: id, Name: m.Name, CreatedAt: m.CreatedAt, ItemCount: n, Items: []WishlistItem{}}, nil
}

func (s *store) Delete(user, id string) error {
	res, err := s.redis.do("HDEL", indexKey(user), id)
	if err != nil {
		return err
	}
	if res.num == 0 {
		return errNotFound
	}
	_, err = s.redis.do("DEL", listKey(user, id))
	return err
}

func (s *store) AddItem(user, id, productID string) error {
	if _, err := s.meta(user, id); err != nil {
		return err
	}
	n, err := s.count(user, id)
	if err != nil {
		return err
	}
	if n >= maxItemsPerList {
		return errTooManyItems
	}
	// NX keeps the original timestamp when the product is already on the list.
	if _, err := s.redis.do("ZADD", listKey(user, id), "NX",
		strconv.FormatInt(time.Now().Unix(), 10), productID); err != nil {
		return err
	}
	s.touch(indexKey(user), listKey(user, id))
	return nil
}

func (s *store) RemoveItem(user, id, productID string) error {
	if _, err := s.meta(user, id); err != nil {
		return err
	}
	if _, err := s.redis.do("ZREM", listKey(user, id), productID); err != nil {
		return err
	}
	s.touch(indexKey(user), listKey(user, id))
	return nil
}

// Summary powers the counter in the store header.
func (s *store) Summary(user string) (lists int, items int, err error) {
	res, err := s.redis.do("HKEYS", indexKey(user))
	if err != nil {
		return 0, 0, err
	}
	ids := res.strings()
	for _, id := range ids {
		n, err := s.count(user, id)
		if err != nil {
			return 0, 0, err
		}
		items += n
	}
	return len(ids), items, nil
}
