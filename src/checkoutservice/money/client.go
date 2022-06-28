// Package zendesk provides a client for using the Zendesk Core API.

package zendesk

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"time"
)

// Client describes a client for the Zendesk Core API.
type Client interface {
	WithHeader(name, value string) Client

	AddUserTags(int64, []string) ([]string, error)
	AutocompleteOrganizations(string) ([]Organization, error)
	BatchUpdateManyTickets([]Ticket) error
	BulkUpdateManyTickets([]int64, *Ticket) error
	CreateIdentity(int64, *UserIdentity) (*UserIdentity, error)
	CreateOrganization(*Organization) (*Organization, error)
	CreateOrganizationMembership(*OrganizationMembership) (*OrganizationMembership, error)
	CreateOrUpdateOrganization(*Organization) (*Organization, error)
	CreateOrUpdateUser(*User) (*User, error)
	CreateTicket(*Ticket) (*Ticket, error)
	CreateUser(*User) (*User, error)
	CreateGroup(*Group) (*Group, error)
	DeleteIdentity(int64, int64) error
	DeleteOrganization(int64) error
	DeleteTicket(int64) error
	DeleteUser(int64) (*User, error)
	DeleteOrganizationMembershipByID(int64) error
	DeleteGroup(int64) error
	ListIdentities(int64) ([]UserIdentity, error)
	ListLocales() ([]Locale, error)
	ListOrganizationMembershipsByUserID(id int64) ([]OrganizationMembership, error)
	ListOrganizations(*ListOptions) ([]Organization, error)
	ListOrganizationUsers(int64, *ListUsersOptions) ([]User, error)
	ListOrganizationTickets(int64, *ListOptions, ...SideLoad) (*ListResponse, error)
	ListExternalIDTickets(string, *ListOptions, ...SideLoad) (*ListResponse, error)
	ListRequestedTickets(int64) ([]Ticket, error)
	ListTickets(*ListOptions, ...SideLoad) (*ListResponse, error)
	ListTicketAudits(int64, *ListOptions) (*ListResponse, error)
	ListTicketComments(int64) ([]TicketComment, error)
	ListTicketCommentsFull(int64, *ListOptions, ...SideLoad) (*ListResponse, error)
	ListTicketCollaborators(int64) ([]User, error)
	ListTicketFollowers(int64) ([]User, error)
	ListTicketEmailCCs(int64) ([]User, error)
	ListTicketFields() ([]TicketField, error)
	ListTicketIncidents(int64) ([]Ticket, error)
	ListUsers(*ListUsersOptions) ([]User, error)
	ListGroups() ([]Group, error)
	MakeIdentityPrimary(int64, int64) ([]UserIdentity, error)
	PermanentlyDeleteTicket(int64) (*JobStatus, error)
	PermanentlyDeleteUser(int64) (*User, error)
	RedactCommentString(int64, int64, string) (*TicketComment, error)
	SearchOrganizationsByExternalID(string) ([]Organization, error)
	SearchTickets(string, *ListOptions, ...Filters) (*TicketSearchResults, error)
	SearchUsers(string) ([]User, error)
	SearchUsersEx(string, *ListOptions, ...Filters) (*UserSearchResults, error)
	SearchUserByExternalID(string) (*User, error)
	ShowComplianceDeletionStatuses(int64) ([]ComplianceDeletionStatus, error)
	ShowIdentity(int64, int64) (*UserIdentity, error)
	ShowJobStatus(string) (*JobStatus, error)
	ShowLocale(int64) (*Locale, error)
	ShowLocaleByCode(string) (*Locale, error)
	ShowManyOrganizations([]int64) ([]Organization, error)
	ShowManyUsers([]int64) ([]User, error)
	ShowManyUsersByExternalIDs([]string) ([]User, error)
	ShowOrganization(int64) (*Organization, error)
	ShowTicket(int64) (*Ticket, error)
	ShowUser(int64) (*User, error)
	UpdateIdentity(int64, int64, *UserIdentity) (*UserIdentity, error)
	UpdateOrganization(int64, *Organization) (*Organization, error)
	UpdateTicket(int64, *Ticket) (*Ticket, error)
	UpdateUser(int64, *User) (*User, error)
	UploadFile(string, *string, io.Reader) (*Upload, error)
	UpdateGroup(int64, *Group) (*Group, error)
}

type client struct {
	username string
	password string

	client    *http.Client
	baseURL   *url.URL
	userAgent string
	headers   map[string]string
}

type ClientOption func(*client)

func WithHTTPClient(httpClient *http.Client) ClientOption {
	return func(c *client) {
		c.client = httpClient
	}
}

// NewEnvClient creates a new Client configured via environment variables.
//
// Three environment variables are required: ZENDESK_DOMAIN, ZENDESK_USERNAME and ZENDESK_PASSWORD
// they will provide parameters to the NewClient function
func NewEnvClient(opts ...ClientOption) (Client, error) {
	domain := os.Getenv("ZENDESK_DOMAIN")
	if domain == "" {
		return nil, errors.New("ZENDESK_DOMAIN not found")
	}

	username := os.Getenv("ZENDESK_USERNAME")
	if username == "" {
		return nil, errors.New("ZENDESK_USERNAME not found")
	}

	password := os.Getenv("ZENDESK_PASSWORD")
	if password == "" {
		return nil, errors.New("ZENDESK_PASSWORD not found")
	}

	return NewClient(domain, username, password, opts...)
}

// NewClient creates a new Client.
//
// You can use either a user email/password combination or an API token.
// For the latter, append /token to the email and use the API token as a password
func NewClient(domain, username, password string, opts ...ClientOption) (Client, error) {
	return NewURLClient(fmt.Sprintf("https://%s.zendesk.com", domain), username, password, opts...)
}

// NewURLClient is like NewClient but accepts an explicit end point instead of a Zendesk domain.
func NewURLClient(endpoint, username, password string, opts ...ClientOption) (Client, error) {
	baseURL, err := url.Parse(endpoint)
	if err != nil {
		return nil, err
	}

	c := &client{
		baseURL:   baseURL,
		userAgent: "Go-Zendesk",
		username:  username,
		password:  password,
		client:    http.DefaultClient,
		headers:   make(map[string]string),
	}

	for _, opt := range opts {
		opt(c)
	}

	return c, nil
}

// WithHeader returns an updated client that sends the provided header
// with each subsequent request.
func (c *client) WithHeader(name, value string) Client {
	newClient := *c
	newClient.headers = make(map[string]string)

	for k, v := range c.headers {
		newClient.headers[k] = v
	}

	newClient.headers[name] = value

	return &newClient
}

func (c *client) request(method, endpoint string, headers map[string]string, body io.Reader) (*http.Response, error) {
	rel, err := url.Parse(endpoint)
	if err != nil {
		return nil, err
	}

	url := c.baseURL.ResolveReference(rel)
	req, err := http.NewRequest(method, url.String(), body)
	if err != nil {
		return nil, err
	}

	req.SetBasicAuth(c.username, c.password)
	req.Header.Set("User-Agent", c.userAgent)

	for key, value := range c.headers {
		req.Header.Set(key, value)
	}

	for key, value := range headers {
		req.Header.Set(key, value)
	}

	return c.client.Do(req)
}

func (c *client) do(method, endpoint string, in, out interface{}) error {
	payload, err := marshall(in)
	if err != nil {
		return err
	}

	headers := map[string]string{}
	if in != nil {
		headers["Content-Type"] = "application/json"
	}

	res, err := c.request(method, endpoint, headers, bytes.NewReader(payload))
	if err != nil {
		return err
	}

	defer res.Body.Close()

	// Retry the request if the retry after header is present. This can happen when we are
	// being rate limited or we failed with a retriable error.
	if res.Header.Get("Retry-After") != "" {
		after, err := strconv.ParseInt(res.Header.Get("Retry-After"), 10, 64)
		if err != nil || after == 0 {
			return unmarshall(res, out)
		}

		time.Sleep(time.Duration(after) * time.Second)

		res, err = c.request(method, endpoint, headers, bytes.NewReader(payload))
		if err != nil {
			return err
		}
		defer res.Body.Close()
	}

	return unmarshall(res, out)
}

func (c *client) get(endpoint string, out interface{}) error {
	return c.do("GET", endpoint, nil, out)
}

func (c *client) post(endpoint string, in, out interface{}) error {
	return c.do("POST", endpoint, in, out)
}

func (c *client) put(endpoint string, in, out interface{}) error {
	return c.do("PUT", endpoint, in, out)
}

func (c *client) delete(endpoint string, out interface{}) error {
	return c.do("DELETE", endpoint, nil, out)
}

func marshall(in interface{}) ([]byte, error) {
	if in == nil {
		return nil, nil
	}

	return json.Marshal(in)
}

func unmarshall(res *http.Response, out interface{}) error {
	if res.StatusCode < 200 || res.StatusCode >= 300 {
		apierr := new(APIError)
		apierr.Response = res
		if err := json.NewDecoder(res.Body).Decode(apierr); err != nil {
			apierr.Type = String("Unknown")
			apierr.Description = String("Oops! Something went wrong when parsing the error response.")
		}
		return apierr
	}

	if out != nil {
		return json.NewDecoder(res.Body).Decode(out)
	}

	return nil
}

// APIPayload represents the payload of an API call.
type APIPayload struct {
	Attachment                 *Attachment                `json:"attachment"`
	Attachments                []Attachment               `json:"attachments"`
	Audits                     []TicketAudit              `json:"audits,omitempty"`
	Comment                    *TicketComment             `json:"comment,omitempty"`
	Comments                   []TicketComment            `json:"comments,omitempty"`
	ComplianceDeletionStatuses []ComplianceDeletionStatus `json:"compliance_deletion_statuses,omitempty"`
	Identity                   *UserIdentity              `json:"identity,omitempty"`
	Identities                 []UserIdentity             `json:"identities,omitempty"`
	JobStatus                  *JobStatus                 `json:"job_status,omitempty"`
	Locale                     *Locale                    `json:"locale,omitempty"`
	Locales                    []Locale                   `json:"locales,omitempty"`
	Organization               *Organization              `json:"organization,omitempty"`
	OrganizationMembership     *OrganizationMembership    `json:"organization_membership,omitempty"`
	OrganizationMemberships    []OrganizationMembership   `json:"organization_memberships,omitempty"`
	Organizations              []Organization             `json:"organizations,omitempty"`
	Tags                       []string                   `json:"tags,omitempty"`
	Ticket                     *Ticket                    `json:"ticket,omitempty"`
	TicketField                *TicketField               `json:"ticket_field,omitempty"`
	TicketFields               []TicketField              `json:"ticket_fields,omitempty"`
	Tickets                    []Ticket                   `json:"tickets,omitempty"`
	Upload                     *Upload                    `json:"upload,omitempty"`
	User                       *User                      `json:"user,omitempty"`
	Users                      []User                     `json:"users,omitempty"`
	Group                      *Group                     `json:"group,omitempty"`
	Groups                     []Group                    `json:"groups,omitempty"`
	NextPage                   *string                    `json:"next_page,omitempty"`
	PreviousPage               *string                    `json:"previous_page,omitempty"`
	Count                      *int64                     `json:"count,omitempty"`
}

// TicketSearchResults represents returned results from the unified search api for type:ticket
type TicketSearchResults struct {
	Results      []Ticket `json:"results"`
	NextPage     *string  `json:"next_page"`
	PreviousPage *string  `json:"previous_page"`
	Count        *int64   `json:"count"`
}

// UserSearchResults represents returned results from the unified search api for type:user
type UserSearchResults struct {
	Results      []User  `json:"results"`
	NextPage     *string `json:"next_page"`
	PreviousPage *string `json:"previous_page"`
	Count        *int64  `json:"count"`
}

// APIError represents an error response returnted by the API.
type APIError struct {
	Response *http.Response

	Type        *string                       `json:"error,omitempty"`
	Description *string                       `json:"description,omitempty"`
	Details     *map[string][]*APIErrorDetail `json:"details,omitempty"`
}

func (e *APIError) Error() string {
	msg := fmt.Sprintf("%v %v: %d", e.Response.Request.Method, e.Response.Request.URL, e.Response.StatusCode)

	if e.Type != nil {
		msg = fmt.Sprintf("%s %v", msg, *e.Type)
	}

	if e.Description != nil {
		msg = fmt.Sprintf("%s: %v", msg, *e.Description)
	}

	if e.Details != nil {
		msg = fmt.Sprintf("%s: %+v", msg, *e.Details)
	}

	return msg
}

// APIErrorDetail represents a detail about an APIError.
type APIErrorDetail struct {
	Type        *string `json:"error,omitempty"`
	Description *string `json:"description,omitempty"`
}

func (e *APIErrorDetail) Error() string {
	msg := ""

	if e.Type != nil {
		msg = *e.Type + ": "
	}

	if e.Description != nil {
		msg += *e.Description
	}

	return msg
}

// Bool is a helper function that returns a pointer to the bool value b.
func Bool(b bool) *bool {
	p := b
	return &p
}

// Int is a helper function that returns a pointer to the int value i.
func Int(i int64) *int64 {
	p := i
	return &p
}

// String is a helper function that returns a pointer to the string value s.
func String(s string) *string {
	p := s
	return &p
}

// ListResponse is a holder for the various returns from the list apis
type ListResponse struct {
	Comments     []TicketComment
	Tickets      []Ticket
	Users        []User
	Groups       []Group
	Audits       []TicketAudit
	NextPage     *string
	PreviousPage *string
	Count        *int64
}

// ListOptions specifies the optional parameters for the list methods that support pagination.
//
// Zendesk Core API doscs: https://developer.zendesk.com/rest_api/docs/core/introduction#pagination
type ListOptions struct {
	// Sets the page of results to retrieve.
	Page int `url:"page,omitempty"`
	// Sets the number of results to include per page.
	PerPage int `url:"per_page,omitempty"`
	// Sets the field to sort the retrieved results by.
	SortBy string `url:"sort_by,omitempty"`
	// Sets the sort order of the results. One of asc or desc.
	SortOrder string `url:"sort_order,omitempty"`
}

// Side-Loading
//
// Zendesk Core API doscs: https://developer.zendesk.com/rest_api/docs/core/side_loading#side-loading
type SideLoadOptions struct {
	Include []string
}

// Allows for side loads to be specified on api requests that support it
type SideLoad func(*SideLoadOptions)

// IncludeUsers will include a top level array of users
func IncludeUsers() SideLoad {
	return func(c *SideLoadOptions) {
		c.Include = append(c.Include, "users")
	}
}

// IncludeGroups will include a top level array of groups
func IncludeGroups() SideLoad {
	return func(c *SideLoadOptions) {
		c.Include = append(c.Include, "groups")
	}
}

// IncludeCommentCount will include a top level array of groups
func IncludeCommentCount() SideLoad {
	return func(c *SideLoadOptions) {
		c.Include = append(c.Include, "comment_count")
	}
}
