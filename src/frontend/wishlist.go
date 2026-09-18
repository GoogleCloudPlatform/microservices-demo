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
	"context"
	"net/http"
	"strings"
	"time"

	"github.com/gorilla/mux"
	"github.com/pkg/errors"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"

	pb "github.com/GoogleCloudPlatform/microservices-demo/src/frontend/genproto"
)

const (
	wishlistTimeout = 3 * time.Second
	// El contador del encabezado se pinta en todas las páginas, así que tiene
	// un presupuesto mucho más corto: si el servicio se pone lento, la tienda
	// no se lo puede permitir.
	wishlistBadgeTimeout = 500 * time.Millisecond
)

// wishlistSvc se arma en main(). Es global porque injectCommonTemplateData(),
// que alimenta a todas las plantillas, lo necesita.
var wishlistSvc *wlClient

// wlProductView es lo que la plantilla de una lista pinta por renglón.
type wlProductView struct {
	Item    *pb.Product
	Price   *pb.Money
	AddedAt time.Time
}

type wlClient struct {
	c pb.WishlistServiceClient
}

func newWishlistClient(conn *grpc.ClientConn) *wlClient {
	return &wlClient{c: pb.NewWishlistServiceClient(conn)}
}

func (c *wlClient) lists(ctx context.Context, userID string) ([]*pb.Wishlist, error) {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	res, err := c.c.ListWishlists(ctx, &pb.ListWishlistsRequest{UserId: userID})
	return res.GetWishlists(), err
}

func (c *wlClient) get(ctx context.Context, userID, id string) (*pb.Wishlist, error) {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	return c.c.GetWishlist(ctx, &pb.GetWishlistRequest{UserId: userID, Id: id})
}

func (c *wlClient) create(ctx context.Context, userID, name string) (*pb.Wishlist, error) {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	return c.c.CreateWishlist(ctx, &pb.CreateWishlistRequest{UserId: userID, Name: name})
}

func (c *wlClient) rename(ctx context.Context, userID, id, name string) error {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	_, err := c.c.RenameWishlist(ctx, &pb.RenameWishlistRequest{UserId: userID, Id: id, Name: name})
	return err
}

func (c *wlClient) remove(ctx context.Context, userID, id string) error {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	_, err := c.c.DeleteWishlist(ctx, &pb.DeleteWishlistRequest{UserId: userID, Id: id})
	return err
}

func (c *wlClient) addItem(ctx context.Context, userID, id, productID string) error {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	_, err := c.c.AddWishlistItem(ctx, &pb.AddWishlistItemRequest{
		UserId: userID, Id: id, ProductId: productID})
	return err
}

func (c *wlClient) removeItem(ctx context.Context, userID, id, productID string) error {
	ctx, cancel := context.WithTimeout(ctx, wishlistTimeout)
	defer cancel()
	_, err := c.c.RemoveWishlistItem(ctx, &pb.RemoveWishlistItemRequest{
		UserId: userID, Id: id, ProductId: productID})
	return err
}

// wishlistContext se llama al pintar cualquier página: alimenta el contador del
// encabezado y el desplegable de la página de producto. Los errores se tragan a
// propósito, una caída del servicio no puede tumbar la tienda.
func wishlistContext(r *http.Request) ([]*pb.Wishlist, int) {
	if wishlistSvc == nil {
		return nil, 0
	}
	userID := sessionID(r)
	if userID == "" {
		return nil, 0
	}
	ctx, cancel := context.WithTimeout(r.Context(), wishlistBadgeTimeout)
	defer cancel()

	lists, err := wishlistSvc.lists(ctx, userID)
	if err != nil {
		return nil, 0
	}
	total := 0
	for _, l := range lists {
		total += int(l.GetItemCount())
	}
	return lists, total
}

// wishlistHTTPStatus traduce el código de gRPC al código HTTP que le toca a la
// página de error. Esto es lo que se gana con errores tipados: el frontend no
// tiene que interpretar mensajes de texto.
func wishlistHTTPStatus(err error) int {
	switch status.Code(err) {
	case codes.NotFound:
		return http.StatusNotFound
	case codes.InvalidArgument:
		return http.StatusUnprocessableEntity
	case codes.ResourceExhausted:
		return http.StatusConflict
	default:
		return http.StatusInternalServerError
	}
}

// ------------------------------------------------------------------ handlers

func (fe *frontendServer) viewWishlistsHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	log.Debug("viewing wishlists")

	lists, err := wishlistSvc.lists(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve wishlists"), wishlistHTTPStatus(err))
		return
	}
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve cart"), http.StatusInternalServerError)
		return
	}

	if err := templates.ExecuteTemplate(w, "wishlists", injectCommonTemplateData(r, map[string]interface{}{
		"show_currency": true,
		"currencies":    currencies,
		"cart_size":     cartSize(cart),
		"lists":         lists,
	})); err != nil {
		log.Error(err)
	}
}

func (fe *frontendServer) viewWishlistHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	id := mux.Vars(r)["id"]

	list, err := wishlistSvc.get(r.Context(), sessionID(r), id)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve wishlist"), wishlistHTTPStatus(err))
		return
	}
	currencies, err := fe.getCurrencies(r.Context())
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve currencies"), http.StatusInternalServerError)
		return
	}
	cart, err := fe.getCart(r.Context(), sessionID(r))
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve cart"), http.StatusInternalServerError)
		return
	}

	// La lista sólo guarda identificadores: el catálogo es el dueño del resto.
	items := make([]wlProductView, 0, len(list.GetItems()))
	for _, it := range list.GetItems() {
		p, err := fe.getProduct(r.Context(), it.GetProductId())
		if err != nil {
			log.WithField("product", it.GetProductId()).Warn("skipping product missing from the catalog")
			continue
		}
		price, err := fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
		if err != nil {
			renderHTTPError(log, r, w, errors.Wrap(err, "failed to convert currency"), http.StatusInternalServerError)
			return
		}
		items = append(items, wlProductView{Item: p, Price: price, AddedAt: time.Unix(it.GetAddedAt(), 0)})
	}

	if err := templates.ExecuteTemplate(w, "wishlist", injectCommonTemplateData(r, map[string]interface{}{
		"show_currency": true,
		"currencies":    currencies,
		"cart_size":     cartSize(cart),
		"list":          list,
		"items":         items,
	})); err != nil {
		log.Error(err)
	}
}

func (fe *frontendServer) createWishlistHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	name := strings.TrimSpace(r.FormValue("name"))
	if name == "" {
		name = "My Wishlist"
	}
	list, err := wishlistSvc.create(r.Context(), sessionID(r), name)
	if err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to create wishlist"), wishlistHTTPStatus(err))
		return
	}
	log.WithField("wishlist", list.GetId()).Debug("created wishlist")
	redirect(w, baseUrl+"/wishlist/"+list.GetId())
}

func (fe *frontendServer) renameWishlistHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	id := mux.Vars(r)["id"]
	name := strings.TrimSpace(r.FormValue("name"))
	if name == "" {
		renderHTTPError(log, r, w, errors.New("wishlist name is required"), http.StatusUnprocessableEntity)
		return
	}
	if err := wishlistSvc.rename(r.Context(), sessionID(r), id, name); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to rename wishlist"), wishlistHTTPStatus(err))
		return
	}
	redirect(w, baseUrl+"/wishlist/"+id)
}

func (fe *frontendServer) deleteWishlistHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	id := mux.Vars(r)["id"]
	if err := wishlistSvc.remove(r.Context(), sessionID(r), id); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to delete wishlist"), wishlistHTTPStatus(err))
		return
	}
	redirect(w, baseUrl+"/wishlists")
}

// addToWishlistHandler es la entrada desde la página de producto: puede crear
// la lista al vuelo cuando el comprador elige "nueva lista".
func (fe *frontendServer) addToWishlistHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	productID := strings.TrimSpace(r.FormValue("product_id"))
	if productID == "" {
		renderHTTPError(log, r, w, errors.New("product id not specified"), http.StatusBadRequest)
		return
	}
	// Comprobar que el producto existe antes de guardar su identificador.
	if _, err := fe.getProduct(r.Context(), productID); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "could not retrieve product"), http.StatusInternalServerError)
		return
	}

	listID := strings.TrimSpace(r.FormValue("list_id"))
	if listID == "" || listID == "__new__" {
		name := strings.TrimSpace(r.FormValue("new_list_name"))
		if name == "" {
			name = "My Wishlist"
		}
		list, err := wishlistSvc.create(r.Context(), sessionID(r), name)
		if err != nil {
			renderHTTPError(log, r, w, errors.Wrap(err, "failed to create wishlist"), wishlistHTTPStatus(err))
			return
		}
		listID = list.GetId()
	}

	if err := wishlistSvc.addItem(r.Context(), sessionID(r), listID, productID); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to add product to wishlist"), wishlistHTTPStatus(err))
		return
	}
	log.WithField("product", productID).WithField("wishlist", listID).Debug("added to wishlist")
	redirect(w, baseUrl+"/wishlist/"+listID)
}

func (fe *frontendServer) removeFromWishlistHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	id := mux.Vars(r)["id"]
	productID := strings.TrimSpace(r.FormValue("product_id"))
	if err := wishlistSvc.removeItem(r.Context(), sessionID(r), id, productID); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to remove product from wishlist"), wishlistHTTPStatus(err))
		return
	}
	redirect(w, baseUrl+"/wishlist/"+id)
}

// moveToCartHandler es el único lugar donde se combinan dos backends: el
// frontend agrega al carrito y después quita el producto de la lista. Los
// servicios nunca se llaman entre ellos.
// moveBetweenListsHandler cambia un producto de una lista a otra.
//
// No hace falta ninguna operacion nueva en el contrato: mover es agregar en la
// lista destino y quitar de la de origen. El servicio no se entera de que esto
// existe, y por eso wishlist.proto no cambia.
func (fe *frontendServer) moveBetweenListsHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	origen := mux.Vars(r)["id"]
	productID := strings.TrimSpace(r.FormValue("product_id"))
	destino := strings.TrimSpace(r.FormValue("target_list_id"))

	if productID == "" {
		renderHTTPError(log, r, w, errors.New("product id not specified"), http.StatusBadRequest)
		return
	}
	if destino == "" {
		renderHTTPError(log, r, w, errors.New("target wishlist not specified"), http.StatusBadRequest)
		return
	}
	// Mover a la misma lista no es un error: es exactamente el estado que se
	// pedia, asi que se contesta como si se hubiera hecho.
	if destino == origen {
		redirect(w, baseUrl+"/wishlist/"+origen)
		return
	}

	// Primero agregar, despues quitar. Es el mismo orden que en «mover al
	// carrito» y por la misma razon: si algo falla en medio, el producto queda
	// en las dos listas —molesto— y nunca se pierde.
	if err := wishlistSvc.addItem(r.Context(), sessionID(r), destino, productID); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to add product to the target wishlist"), wishlistHTTPStatus(err))
		return
	}
	if err := wishlistSvc.removeItem(r.Context(), sessionID(r), origen, productID); err != nil {
		// Ya esta en la lista destino, asi que esto no es fatal.
		log.WithField("error", err).Warn("failed to remove product from the source wishlist after moving it")
	}

	log.WithField("product", productID).WithField("from", origen).WithField("to", destino).Debug("moved between wishlists")
	redirect(w, baseUrl+"/wishlist/"+destino)
}

func (fe *frontendServer) moveToCartHandler(w http.ResponseWriter, r *http.Request) {
	log := r.Context().Value(ctxKeyLog{}).(logrus.FieldLogger)
	id := mux.Vars(r)["id"]
	productID := strings.TrimSpace(r.FormValue("product_id"))
	if productID == "" {
		renderHTTPError(log, r, w, errors.New("product id not specified"), http.StatusBadRequest)
		return
	}
	if err := fe.insertCart(r.Context(), sessionID(r), productID, 1); err != nil {
		renderHTTPError(log, r, w, errors.Wrap(err, "failed to add to cart"), http.StatusInternalServerError)
		return
	}
	if err := wishlistSvc.removeItem(r.Context(), sessionID(r), id, productID); err != nil {
		// El producto ya está en el carrito, así que esto no es fatal.
		log.WithField("error", err).Warn("failed to remove product from wishlist after moving it to the cart")
	}
	redirect(w, baseUrl+"/cart")
}

func redirect(w http.ResponseWriter, location string) {
	w.Header().Set("Location", location)
	w.WriteHeader(http.StatusFound)
}
