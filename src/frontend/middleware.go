// Copyright 2018 Google LLC
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
	"context"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/contrib/detectors/gcp"
	"go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"go.opentelemetry.io/otel/api/global"
	"go.opentelemetry.io/otel/api/metric"
	"go.opentelemetry.io/otel/api/trace"
	"go.opentelemetry.io/otel/label"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/semconv"
	"go.opentelemetry.io/otel/unit"
	"google.golang.org/grpc"
	"google.golang.org/grpc/peer"
)

const (
	instName = "github.com/GoogleCloudPlatform/microservices-demo/src/frontend"
	instVer  = "semver:0.0.1"
)

var (
	httpLatency metric.Float64ValueRecorder
	grpcLatency metric.Float64ValueRecorder

	res *resource.Resource
)

func init() {
	meter := global.MeterProvider().Meter(instName, metric.WithInstrumentationVersion(instVer))
	httpLatency = metric.Must(meter).NewFloat64ValueRecorder(
		"http.server.duration",
		metric.WithDescription("duration of the inbound HTTP request"),
		metric.WithUnit(unit.Milliseconds),
	)
	grpcLatency = metric.Must(meter).NewFloat64ValueRecorder(
		"grpc.client.duration",
		metric.WithDescription("duration of the inbound gRPC request"),
		metric.WithUnit(unit.Milliseconds),
	)

	detectedR, err := new(gcp.GKE).Detect(context.Background())
	if err != nil {
		logrus.WithError(err).Fatal("could not detect GKE environment")
	}

	var instID label.KeyValue
	if host, ok := os.LookupEnv("HOSTNAME"); ok && host != "" {
		instID = semconv.ServiceInstanceIDKey.String(host)
	} else {
		instID = semconv.ServiceInstanceIDKey.String(uuid.New().String())
	}
	res = resource.Merge(detectedR, resource.New(instID))
}

type ctxKeyLog struct{}
type ctxKeyRequestID struct{}

type logHandler struct {
	log  *logrus.Logger
	next http.Handler
}

type responseRecorder struct {
	b      int
	status int
	w      http.ResponseWriter
}

func (r *responseRecorder) Header() http.Header { return r.w.Header() }

func (r *responseRecorder) Write(p []byte) (int, error) {
	if r.status == 0 {
		r.status = http.StatusOK
	}
	n, err := r.w.Write(p)
	r.b += n
	return n, err
}

func (r *responseRecorder) WriteHeader(statusCode int) {
	r.status = statusCode
	r.w.WriteHeader(statusCode)
}

func (lh *logHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	rr := &responseRecorder{w: w}
	ctx := r.Context()
	requestID, _ := uuid.NewRandom()
	ctx = context.WithValue(ctx, ctxKeyRequestID{}, requestID.String())

	start := time.Now()
	log := lh.log.WithFields(logrus.Fields{
		"http.req.path":   r.URL.Path,
		"http.req.method": r.Method,
		"http.req.id":     requestID.String(),
	})
	if v, ok := r.Context().Value(ctxKeySessionID{}).(string); ok {
		log = log.WithField("session", v)
	}
	log.Debug("request started")
	defer func() {
		log.WithFields(logrus.Fields{
			"http.resp.took_ms": int64(time.Since(start) / time.Millisecond),
			"http.resp.status":  rr.status,
			"http.resp.bytes":   rr.b}).Debugf("request complete")
	}()

	ctx = context.WithValue(ctx, ctxKeyLog{}, log)
	r = r.WithContext(ctx)
	lh.next.ServeHTTP(rr, r)
}

func ensureSessionID(next http.Handler) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var sessionID string
		c, err := r.Cookie(cookieSessionID)
		if err == http.ErrNoCookie {
			u, _ := uuid.NewRandom()
			sessionID = u.String()
			http.SetCookie(w, &http.Cookie{
				Name:   cookieSessionID,
				Value:  sessionID,
				MaxAge: cookieMaxAge,
			})
		} else if err != nil {
			return
		} else {
			sessionID = c.Value
		}
		ctx := context.WithValue(r.Context(), ctxKeySessionID{}, sessionID)
		r = r.WithContext(ctx)
		next.ServeHTTP(w, r)
	}
}

type traceware struct {
	handler http.Handler
}

// ServeHTTP implements the http.Handler interface. It does the actual
// tracing of the request.
func (tw traceware) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	ctx := global.TextMapPropagator().Extract(r.Context(), r.Header)
	spanName := ""
	route := mux.CurrentRoute(r)
	if route != nil {
		var err error
		spanName, err = route.GetPathTemplate()
		if err != nil {
			spanName, err = route.GetPathRegexp()
			if err != nil {
				spanName = ""
			}
		}
	}
	if spanName == "" {
		spanName = fmt.Sprintf("HTTP %s route not found", r.Method)
	}
	labels := []label.KeyValue{
		label.String("span.name", spanName),
		label.String("span.kind", trace.SpanKindServer.String()),
	}
	labels = append(labels, semconv.HTTPServerMetricAttributesFromHTTPRequest(serviceName, r)...)

	start := time.Now()
	defer func() {
		httpLatency.Record(ctx, float64(time.Now().Sub(start).Milliseconds()), labels...)
	}()
	tw.handler.ServeHTTP(w, r)
}

func MuxMiddleware() mux.MiddlewareFunc {
	return func(handler http.Handler) http.Handler {
		return traceware{handler: handler}
	}
}

// UnaryClientInterceptor returns a grpc.UnaryClientInterceptor suitable
// for use in a grpc.Dial call.
func UnaryClientInterceptor() grpc.UnaryClientInterceptor {
	upstream := otelgrpc.UnaryClientInterceptor()
	return func(
		ctx context.Context,
		method string,
		req, reply interface{},
		cc *grpc.ClientConn,
		invoker grpc.UnaryInvoker,
		opts ...grpc.CallOption,
	) error {
		start := time.Now()
		defer func() {
			grpcLatency.Record(
				ctx,
				float64(time.Now().Sub(start).Milliseconds()),
				labels(method, cc.Target())...,
			)
		}()

		return upstream(ctx, method, req, reply, cc, invoker, opts...)
	}
}

// StreamClientInterceptor returns a grpc.StreamClientInterceptor suitable
// for use in a grpc.Dial call.
func StreamClientInterceptor() grpc.StreamClientInterceptor {
	upstream := otelgrpc.StreamClientInterceptor()
	return func(
		ctx context.Context,
		desc *grpc.StreamDesc,
		cc *grpc.ClientConn,
		method string,
		streamer grpc.Streamer,
		opts ...grpc.CallOption,
	) (grpc.ClientStream, error) {
		start := time.Now()
		defer func() {
			grpcLatency.Record(
				ctx,
				float64(time.Now().Sub(start).Milliseconds()),
				labels(method, cc.Target())...,
			)
		}()

		return upstream(ctx, desc, cc, method, streamer, opts...)
	}
}

/*************************************************************************
* Copied from
* go.opentelemetry.io/otel/instrumentation/grpctrace/interceptor.go@v0.8.0
 */

func labels(fullMethod, peerAddress string) []label.KeyValue {
	attrs := []label.KeyValue{semconv.RPCSystemGRPC}
	name, mAttrs := parseFullMethod(fullMethod)
	attrs = append(attrs, mAttrs...)
	attrs = append(attrs, peerAttr(peerAddress)...)
	attrs = append(attrs, label.String("span.name", name))
	attrs = append(attrs, label.String("span.kind", trace.SpanKindServer.String()))
	return attrs
}

// peerAttr returns attributes about the peer address.
func peerAttr(addr string) []label.KeyValue {
	host, port, err := net.SplitHostPort(addr)
	if err != nil {
		return []label.KeyValue(nil)
	}

	if host == "" {
		host = "127.0.0.1"
	}

	return []label.KeyValue{
		semconv.NetPeerIPKey.String(host),
		semconv.NetPeerPortKey.String(port),
	}
}

// peerFromCtx returns a peer address from a context, if one exists.
func peerFromCtx(ctx context.Context) string {
	p, ok := peer.FromContext(ctx)
	if !ok {
		return ""
	}
	return p.Addr.String()
}

// parseFullMethod returns a span name following the OpenTelemetry semantic
// conventions as well as all applicable span label.KeyValue attributes based
// on a gRPC's FullMethod.
func parseFullMethod(fullMethod string) (string, []label.KeyValue) {
	name := strings.TrimLeft(fullMethod, "/")
	parts := strings.SplitN(name, "/", 2)
	if len(parts) != 2 {
		// Invalid format, does not follow `/package.service/method`.
		return name, []label.KeyValue(nil)
	}

	var attrs []label.KeyValue
	if service := parts[0]; service != "" {
		attrs = append(attrs, semconv.RPCServiceKey.String(service))
	}
	if method := parts[1]; method != "" {
		attrs = append(attrs, semconv.RPCMethodKey.String(method))
	}
	return name, attrs
}

/*************************************************************************/
