package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"database/sql"
	"fmt"
	"net"
	"os"
	"strings"
	"sync"
	"time"

	"github.com/go-sql-driver/mysql"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/productcatalogservice/genproto"
)

var (
	log *logrus.Logger
	db  *sql.DB
)

var (
	catalogMutex *sync.Mutex
	extraLatency time.Duration
	reloadCatalog bool
)

func init() {
	log = logrus.New()
	log.Formatter = &logrus.JSONFormatter{
		FieldMap: logrus.FieldMap{
			logrus.FieldKeyTime:  "timestamp",
			logrus.FieldKeyLevel: "severity",
			logrus.FieldKeyMsg:   "message",
		},
		TimestampFormat: time.RFC3339Nano,
	}
	log.Out = os.Stdout
	catalogMutex = &sync.Mutex{}
	extraLatency = 0
	reloadCatalog = false
}

type productCatalogService struct {
	pb.UnimplementedProductCatalogServiceServer
}

func main() {
	// Get database connection details from environment variables
	dbUser := os.Getenv("MYSQL_USER")
	dbPassword := os.Getenv("MYSQL_PASSWORD")
	dbHost := os.Getenv("MYSQL_HOST")
	dbPort := os.Getenv("MYSQL_PORT")
	dbName := os.Getenv("MYSQL_DATABASE")
	dbParams := os.Getenv("MYSQL_PARAMS")
	sslCertPath := os.Getenv("SSL_CERT_PATH")

	// Register TLS config if SSL_CERT_PATH is provided
	if sslCertPath != "" {
		err := mysql.RegisterTLSConfig("custom", &tls.Config{
			RootCAs: loadCACertPool(sslCertPath),
		})
		if err != nil {
			log.Fatalf("failed to register TLS config: %v", err)
		}
		if dbParams != "" {
			dbParams += "&tls=custom"
		} else {
			dbParams = "tls=custom"
		}
	}

	// Create database connection string
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s?parseTime=true&%s", dbUser, dbPassword, dbHost, dbPort, dbName, dbParams)

	var err error
	db, err = sql.Open("mysql", dsn)
	if err != nil {
		log.Fatalf("failed to open database connection: %v", err)
	}
	// See "Important settings" section.
	db.SetConnMaxLifetime(time.Minute * 3)
	db.SetMaxOpenConns(10)
	db.SetMaxIdleConns(10)

	// Check the connection
	err = db.Ping()
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}

	defer db.Close()
	log.Info("Successfully connected to MySQL database")

	port := os.Getenv("PORT")
	if port == "" {
		port = "3550"
	}

	lis, err := net.Listen("tcp", fmt.Sprintf(":%s", port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	srv := grpc.NewServer()
	pb.RegisterProductCatalogServiceServer(srv, &productCatalogService{})
	log.Infof("starting gRPC server on port %s", port)
	if err := srv.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

// loadCACertPool loads the CA certificate from the given path
func loadCACertPool(certPath string) *x509.CertPool {
	certPool := x509.NewCertPool()
	caCert, err := os.ReadFile(certPath)
	if err != nil {
		log.Fatalf("failed to read CA cert file: %v", err)
	}
	if ok := certPool.AppendCertsFromPEM(caCert); !ok {
		log.Fatalf("failed to append CA cert")
	}
	return certPool
}

func (s *productCatalogService) ListProducts(ctx context.Context, _ *pb.Empty) (*pb.ListProductsResponse, error) {
	rows, err := db.QueryContext(ctx, "SELECT id, name, description, picture, price_usd_currency_code, price_usd_units, price_usd_nanos, categories FROM products")
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to query products: %v", err)
	}
	defer rows.Close()

	var products []*pb.Product
	for rows.Next() {
		p := &pb.Product{PriceUsd: &pb.Money{}}
		var categories string
		if err := rows.Scan(&p.Id, &p.Name, &p.Description, &p.Picture, &p.PriceUsd.CurrencyCode, &p.PriceUsd.Units, &p.PriceUsd.Nanos, &categories); err != nil {
			return nil, status.Errorf(codes.Internal, "failed to scan product: %v", err)
		}
		p.Categories = strings.Split(categories, ",")
		products = append(products, p)
	}

	return &pb.ListProductsResponse{Products: products}, nil
}

func (s *productCatalogService) GetProduct(ctx context.Context, req *pb.GetProductRequest) (*pb.Product, error) {
	var p pb.Product
	p.PriceUsd = &pb.Money{}
	var categories string
	row := db.QueryRowContext(ctx, "SELECT id, name, description, picture, price_usd_currency_code, price_usd_units, price_usd_nanos, categories FROM products WHERE id = ?", req.Id)
	err := row.Scan(&p.Id, &p.Name, &p.Description, &p.Picture, &p.PriceUsd.CurrencyCode, &p.PriceUsd.Units, &p.PriceUsd.Nanos, &categories)
	if err == sql.ErrNoRows {
		return nil, status.Errorf(codes.NotFound, "product with ID %s not found", req.Id)
	} else if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to get product: %v", err)
	}
	p.Categories = strings.Split(categories, ",")
	return &p, nil
}

func (s *productCatalogService) SearchProducts(ctx context.Context, req *pb.SearchProductsRequest) (*pb.SearchProductsResponse, error) {
	query := "%" + req.Query + "%"
	rows, err := db.QueryContext(ctx, "SELECT id, name, description, picture, price_usd_currency_code, price_usd_units, price_usd_nanos, categories FROM products WHERE name LIKE ? OR description LIKE ?", query, query)
	if err != nil {
		return nil, status.Errorf(codes.Internal, "failed to search products: %v", err)
	}
	defer rows.Close()

	var products []*pb.Product
	for rows.Next() {
		p := &pb.Product{PriceUsd: &pb.Money{}}
		var categories string
		if err := rows.Scan(&p.Id, &p.Name, &p.Description, &p.Picture, &p.PriceUsd.CurrencyCode, &p.PriceUsd.Units, &p.PriceUsd.Nanos, &categories); err != nil {
			return nil, status.Errorf(codes.Internal, "failed to scan product: %v", err)
		}
		p.Categories = strings.Split(categories, ",")
		products = append(products, p)
	}
	if len(products) == 0 {
		return &pb.SearchProductsResponse{}, nil
	}
	return &pb.SearchProductsResponse{Results: products}, nil
}