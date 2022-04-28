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
	"strings"
	"time"

	"go.opentelemetry.io/otel/metric/instrument"
	"go.opentelemetry.io/otel/metric/instrument/syncfloat64"
	"go.opentelemetry.io/otel/metric/unit"

	"github.com/google/uuid"
	"github.com/gorilla/mux"
	"github.com/sirupsen/logrus"
	"go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
	"go.opentelemetry.io/otel/metric/global"
	"go.opentelemetry.io/otel/propagation"
	"go.opentelemetry.io/otel/sdk/resource"
	semconv "go.opentelemetry.io/otel/semconv/v1.7.0"
	"go.opentelemetry.io/otel/trace"
	"google.golang.org/grpc"
	"google.golang.org/grpc/peer"
)

const (
	instName = "github.com/GoogleCloudPlatform/microservices-demo/src/frontend"
	instVer  = "semver:0.0.1"
)

var (
	httpLatency syncfloat64.Histogram
	grpcLatency syncfloat64.Histogram

	res *resource.Resource
)

func init() {
	meter := global.MeterProvider().Meter(instName, metric.WithInstrumentationVersion(instVer))
	httpLatencyInstrument, err := meter.SyncFloat64().Histogram(
		"http.server.duration",
		instrument.WithDescription("duration of the inbound HTTP request"),
		instrument.WithUnit(unit.Milliseconds))
	if err != nil {
		logrus.WithError(err).Fatal("failed to create httpLatency instrument")
	}
	httpLatency = httpLatencyInstrument

	grpcLatencyInstrument, err := meter.SyncFloat64().Histogram(
		"grpc.client.duration",
		instrument.WithDescription("duration of the outbound gRPC request"),
		instrument.WithUnit(unit.Milliseconds))
	if err != nil {
		logrus.WithError(err).Fatal("failed to create grpcLatency instrument")
	}
	grpcLatency = grpcLatencyInstrument

	appResource, err := resource.New(
		context.Background(),
		resource.WithAttributes(semconv.ServiceNameKey.String("Frontend")),
		resource.WithFromEnv(),
	)
	if err != nil {
		logrus.WithError(err).Fatal("failed to create resource resource")
	}
	res, err = resource.Merge(resource.Default(), appResource)
	if err != nil {
		logrus.WithError(err).Fatal("failed to create resource resource")
	}
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
	ctx := otel.GetTextMapPropagator().Extract(r.Context(), propagation.HeaderCarrier(r.Header))
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
	labels := []attribute.KeyValue{
		attribute.String("span.name", spanName),
		attribute.String("span.kind", trace.SpanKindServer.String()),
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
				attributes(method, cc.Target())...,
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
				attributes(method, cc.Target())...,
			)
		}()

		return upstream(ctx, desc, cc, method, streamer, opts...)
	}
}

/*************************************************************************
* Copied from
* go.opentelemetry.io/otel/instrumentation/grpctrace/interceptor.go@v0.8.0
 */

func attributes(fullMethod, peerAddress string) []attribute.KeyValue {
	attrs := []attribute.KeyValue{semconv.RPCSystemKey.String("grpc")}
	name, mAttrs := parseFullMethod(fullMethod)
	attrs = append(attrs, mAttrs...)
	attrs = append(attrs, peerAttr(peerAddress)...)
	attrs = append(attrs, attribute.String("span.name", name))
	attrs = append(attrs, attribute.String("span.kind", trace.SpanKindServer.String()))
	return attrs
}

// peerAttr returns attributes about the peer address.
func peerAttr(addr string) []attribute.KeyValue {
	host, port, err := net.SplitHostPort(addr)
	if err != nil {
		return []attribute.KeyValue(nil)
	}

	if host == "" {
		host = "127.0.0.1"
	}

	return []attribute.KeyValue{
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
func parseFullMethod(fullMethod string) (string, []attribute.KeyValue) {
	name := strings.TrimLeft(fullMethod, "/")
	parts := strings.SplitN(name, "/", 2)
	if len(parts) != 2 {
		// Invalid format, does not follow `/package.service/method`.
		return name, []attribute.KeyValue(nil)
	}

	var attrs []attribute.KeyValue
	if service := parts[0]; service != "" {
		attrs = append(attrs, semconv.RPCServiceKey.String(service))
	}
	if method := parts[1]; method != "" {
		attrs = append(attrs, semconv.RPCMethodKey.String(method))
	}
	return name, attrs
}

/*************************************************************************/
