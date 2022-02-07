package cse.project.grpc;

import static io.grpc.MethodDescriptor.generateFullMethodName;
import static io.grpc.stub.ClientCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ClientCalls.asyncClientStreamingCall;
import static io.grpc.stub.ClientCalls.asyncServerStreamingCall;
import static io.grpc.stub.ClientCalls.asyncUnaryCall;
import static io.grpc.stub.ClientCalls.blockingServerStreamingCall;
import static io.grpc.stub.ClientCalls.blockingUnaryCall;
import static io.grpc.stub.ClientCalls.futureUnaryCall;
import static io.grpc.stub.ServerCalls.asyncBidiStreamingCall;
import static io.grpc.stub.ServerCalls.asyncClientStreamingCall;
import static io.grpc.stub.ServerCalls.asyncServerStreamingCall;
import static io.grpc.stub.ServerCalls.asyncUnaryCall;
import static io.grpc.stub.ServerCalls.asyncUnimplementedStreamingCall;
import static io.grpc.stub.ServerCalls.asyncUnimplementedUnaryCall;

/**
 */
@javax.annotation.Generated(
    value = "by gRPC proto compiler (version 1.15.0)",
    comments = "Source: ratingService.proto")
public final class RatingServiceGrpc {

  private RatingServiceGrpc() {}

  public static final String SERVICE_NAME = "RatingService";

  // Static method descriptors that strictly reflect the proto.
  private static volatile io.grpc.MethodDescriptor<cse.project.grpc.ProductRequest,
      cse.project.grpc.ApiResponse> getRateProductMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "RateProduct",
      requestType = cse.project.grpc.ProductRequest.class,
      responseType = cse.project.grpc.ApiResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<cse.project.grpc.ProductRequest,
      cse.project.grpc.ApiResponse> getRateProductMethod() {
    io.grpc.MethodDescriptor<cse.project.grpc.ProductRequest, cse.project.grpc.ApiResponse> getRateProductMethod;
    if ((getRateProductMethod = RatingServiceGrpc.getRateProductMethod) == null) {
      synchronized (RatingServiceGrpc.class) {
        if ((getRateProductMethod = RatingServiceGrpc.getRateProductMethod) == null) {
          RatingServiceGrpc.getRateProductMethod = getRateProductMethod = 
              io.grpc.MethodDescriptor.<cse.project.grpc.ProductRequest, cse.project.grpc.ApiResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(
                  "RatingService", "RateProduct"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ProductRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ApiResponse.getDefaultInstance()))
                  .setSchemaDescriptor(new RatingServiceMethodDescriptorSupplier("RateProduct"))
                  .build();
          }
        }
     }
     return getRateProductMethod;
  }

  private static volatile io.grpc.MethodDescriptor<cse.project.grpc.ProductRatingRequest,
      cse.project.grpc.ProductRatingResponse> getGetProductRatingMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetProductRating",
      requestType = cse.project.grpc.ProductRatingRequest.class,
      responseType = cse.project.grpc.ProductRatingResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<cse.project.grpc.ProductRatingRequest,
      cse.project.grpc.ProductRatingResponse> getGetProductRatingMethod() {
    io.grpc.MethodDescriptor<cse.project.grpc.ProductRatingRequest, cse.project.grpc.ProductRatingResponse> getGetProductRatingMethod;
    if ((getGetProductRatingMethod = RatingServiceGrpc.getGetProductRatingMethod) == null) {
      synchronized (RatingServiceGrpc.class) {
        if ((getGetProductRatingMethod = RatingServiceGrpc.getGetProductRatingMethod) == null) {
          RatingServiceGrpc.getGetProductRatingMethod = getGetProductRatingMethod = 
              io.grpc.MethodDescriptor.<cse.project.grpc.ProductRatingRequest, cse.project.grpc.ProductRatingResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(
                  "RatingService", "GetProductRating"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ProductRatingRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ProductRatingResponse.getDefaultInstance()))
                  .setSchemaDescriptor(new RatingServiceMethodDescriptorSupplier("GetProductRating"))
                  .build();
          }
        }
     }
     return getGetProductRatingMethod;
  }

  private static volatile io.grpc.MethodDescriptor<cse.project.grpc.ShopRequest,
      cse.project.grpc.ApiResponse> getRateShopMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "RateShop",
      requestType = cse.project.grpc.ShopRequest.class,
      responseType = cse.project.grpc.ApiResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<cse.project.grpc.ShopRequest,
      cse.project.grpc.ApiResponse> getRateShopMethod() {
    io.grpc.MethodDescriptor<cse.project.grpc.ShopRequest, cse.project.grpc.ApiResponse> getRateShopMethod;
    if ((getRateShopMethod = RatingServiceGrpc.getRateShopMethod) == null) {
      synchronized (RatingServiceGrpc.class) {
        if ((getRateShopMethod = RatingServiceGrpc.getRateShopMethod) == null) {
          RatingServiceGrpc.getRateShopMethod = getRateShopMethod = 
              io.grpc.MethodDescriptor.<cse.project.grpc.ShopRequest, cse.project.grpc.ApiResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(
                  "RatingService", "RateShop"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ShopRequest.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ApiResponse.getDefaultInstance()))
                  .setSchemaDescriptor(new RatingServiceMethodDescriptorSupplier("RateShop"))
                  .build();
          }
        }
     }
     return getRateShopMethod;
  }

  private static volatile io.grpc.MethodDescriptor<cse.project.grpc.Empty,
      cse.project.grpc.ShopRatingResponse> getGetShopRatingMethod;

  @io.grpc.stub.annotations.RpcMethod(
      fullMethodName = SERVICE_NAME + '/' + "GetShopRating",
      requestType = cse.project.grpc.Empty.class,
      responseType = cse.project.grpc.ShopRatingResponse.class,
      methodType = io.grpc.MethodDescriptor.MethodType.UNARY)
  public static io.grpc.MethodDescriptor<cse.project.grpc.Empty,
      cse.project.grpc.ShopRatingResponse> getGetShopRatingMethod() {
    io.grpc.MethodDescriptor<cse.project.grpc.Empty, cse.project.grpc.ShopRatingResponse> getGetShopRatingMethod;
    if ((getGetShopRatingMethod = RatingServiceGrpc.getGetShopRatingMethod) == null) {
      synchronized (RatingServiceGrpc.class) {
        if ((getGetShopRatingMethod = RatingServiceGrpc.getGetShopRatingMethod) == null) {
          RatingServiceGrpc.getGetShopRatingMethod = getGetShopRatingMethod = 
              io.grpc.MethodDescriptor.<cse.project.grpc.Empty, cse.project.grpc.ShopRatingResponse>newBuilder()
              .setType(io.grpc.MethodDescriptor.MethodType.UNARY)
              .setFullMethodName(generateFullMethodName(
                  "RatingService", "GetShopRating"))
              .setSampledToLocalTracing(true)
              .setRequestMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.Empty.getDefaultInstance()))
              .setResponseMarshaller(io.grpc.protobuf.ProtoUtils.marshaller(
                  cse.project.grpc.ShopRatingResponse.getDefaultInstance()))
                  .setSchemaDescriptor(new RatingServiceMethodDescriptorSupplier("GetShopRating"))
                  .build();
          }
        }
     }
     return getGetShopRatingMethod;
  }

  /**
   * Creates a new async stub that supports all call types for the service
   */
  public static RatingServiceStub newStub(io.grpc.Channel channel) {
    return new RatingServiceStub(channel);
  }

  /**
   * Creates a new blocking-style stub that supports unary and streaming output calls on the service
   */
  public static RatingServiceBlockingStub newBlockingStub(
      io.grpc.Channel channel) {
    return new RatingServiceBlockingStub(channel);
  }

  /**
   * Creates a new ListenableFuture-style stub that supports unary calls on the service
   */
  public static RatingServiceFutureStub newFutureStub(
      io.grpc.Channel channel) {
    return new RatingServiceFutureStub(channel);
  }

  /**
   */
  public static abstract class RatingServiceImplBase implements io.grpc.BindableService {

    /**
     */
    public void rateProduct(cse.project.grpc.ProductRequest request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ApiResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getRateProductMethod(), responseObserver);
    }

    /**
     */
    public void getProductRating(cse.project.grpc.ProductRatingRequest request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ProductRatingResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getGetProductRatingMethod(), responseObserver);
    }

    /**
     */
    public void rateShop(cse.project.grpc.ShopRequest request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ApiResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getRateShopMethod(), responseObserver);
    }

    /**
     */
    public void getShopRating(cse.project.grpc.Empty request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ShopRatingResponse> responseObserver) {
      asyncUnimplementedUnaryCall(getGetShopRatingMethod(), responseObserver);
    }

    @java.lang.Override public final io.grpc.ServerServiceDefinition bindService() {
      return io.grpc.ServerServiceDefinition.builder(getServiceDescriptor())
          .addMethod(
            getRateProductMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                cse.project.grpc.ProductRequest,
                cse.project.grpc.ApiResponse>(
                  this, METHODID_RATE_PRODUCT)))
          .addMethod(
            getGetProductRatingMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                cse.project.grpc.ProductRatingRequest,
                cse.project.grpc.ProductRatingResponse>(
                  this, METHODID_GET_PRODUCT_RATING)))
          .addMethod(
            getRateShopMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                cse.project.grpc.ShopRequest,
                cse.project.grpc.ApiResponse>(
                  this, METHODID_RATE_SHOP)))
          .addMethod(
            getGetShopRatingMethod(),
            asyncUnaryCall(
              new MethodHandlers<
                cse.project.grpc.Empty,
                cse.project.grpc.ShopRatingResponse>(
                  this, METHODID_GET_SHOP_RATING)))
          .build();
    }
  }

  /**
   */
  public static final class RatingServiceStub extends io.grpc.stub.AbstractStub<RatingServiceStub> {
    private RatingServiceStub(io.grpc.Channel channel) {
      super(channel);
    }

    private RatingServiceStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected RatingServiceStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new RatingServiceStub(channel, callOptions);
    }

    /**
     */
    public void rateProduct(cse.project.grpc.ProductRequest request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ApiResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRateProductMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getProductRating(cse.project.grpc.ProductRatingRequest request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ProductRatingResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetProductRatingMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void rateShop(cse.project.grpc.ShopRequest request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ApiResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getRateShopMethod(), getCallOptions()), request, responseObserver);
    }

    /**
     */
    public void getShopRating(cse.project.grpc.Empty request,
        io.grpc.stub.StreamObserver<cse.project.grpc.ShopRatingResponse> responseObserver) {
      asyncUnaryCall(
          getChannel().newCall(getGetShopRatingMethod(), getCallOptions()), request, responseObserver);
    }
  }

  /**
   */
  public static final class RatingServiceBlockingStub extends io.grpc.stub.AbstractStub<RatingServiceBlockingStub> {
    private RatingServiceBlockingStub(io.grpc.Channel channel) {
      super(channel);
    }

    private RatingServiceBlockingStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected RatingServiceBlockingStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new RatingServiceBlockingStub(channel, callOptions);
    }

    /**
     */
    public cse.project.grpc.ApiResponse rateProduct(cse.project.grpc.ProductRequest request) {
      return blockingUnaryCall(
          getChannel(), getRateProductMethod(), getCallOptions(), request);
    }

    /**
     */
    public cse.project.grpc.ProductRatingResponse getProductRating(cse.project.grpc.ProductRatingRequest request) {
      return blockingUnaryCall(
          getChannel(), getGetProductRatingMethod(), getCallOptions(), request);
    }

    /**
     */
    public cse.project.grpc.ApiResponse rateShop(cse.project.grpc.ShopRequest request) {
      return blockingUnaryCall(
          getChannel(), getRateShopMethod(), getCallOptions(), request);
    }

    /**
     */
    public cse.project.grpc.ShopRatingResponse getShopRating(cse.project.grpc.Empty request) {
      return blockingUnaryCall(
          getChannel(), getGetShopRatingMethod(), getCallOptions(), request);
    }
  }

  /**
   */
  public static final class RatingServiceFutureStub extends io.grpc.stub.AbstractStub<RatingServiceFutureStub> {
    private RatingServiceFutureStub(io.grpc.Channel channel) {
      super(channel);
    }

    private RatingServiceFutureStub(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      super(channel, callOptions);
    }

    @java.lang.Override
    protected RatingServiceFutureStub build(io.grpc.Channel channel,
        io.grpc.CallOptions callOptions) {
      return new RatingServiceFutureStub(channel, callOptions);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<cse.project.grpc.ApiResponse> rateProduct(
        cse.project.grpc.ProductRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRateProductMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<cse.project.grpc.ProductRatingResponse> getProductRating(
        cse.project.grpc.ProductRatingRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getGetProductRatingMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<cse.project.grpc.ApiResponse> rateShop(
        cse.project.grpc.ShopRequest request) {
      return futureUnaryCall(
          getChannel().newCall(getRateShopMethod(), getCallOptions()), request);
    }

    /**
     */
    public com.google.common.util.concurrent.ListenableFuture<cse.project.grpc.ShopRatingResponse> getShopRating(
        cse.project.grpc.Empty request) {
      return futureUnaryCall(
          getChannel().newCall(getGetShopRatingMethod(), getCallOptions()), request);
    }
  }

  private static final int METHODID_RATE_PRODUCT = 0;
  private static final int METHODID_GET_PRODUCT_RATING = 1;
  private static final int METHODID_RATE_SHOP = 2;
  private static final int METHODID_GET_SHOP_RATING = 3;

  private static final class MethodHandlers<Req, Resp> implements
      io.grpc.stub.ServerCalls.UnaryMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ServerStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.ClientStreamingMethod<Req, Resp>,
      io.grpc.stub.ServerCalls.BidiStreamingMethod<Req, Resp> {
    private final RatingServiceImplBase serviceImpl;
    private final int methodId;

    MethodHandlers(RatingServiceImplBase serviceImpl, int methodId) {
      this.serviceImpl = serviceImpl;
      this.methodId = methodId;
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public void invoke(Req request, io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        case METHODID_RATE_PRODUCT:
          serviceImpl.rateProduct((cse.project.grpc.ProductRequest) request,
              (io.grpc.stub.StreamObserver<cse.project.grpc.ApiResponse>) responseObserver);
          break;
        case METHODID_GET_PRODUCT_RATING:
          serviceImpl.getProductRating((cse.project.grpc.ProductRatingRequest) request,
              (io.grpc.stub.StreamObserver<cse.project.grpc.ProductRatingResponse>) responseObserver);
          break;
        case METHODID_RATE_SHOP:
          serviceImpl.rateShop((cse.project.grpc.ShopRequest) request,
              (io.grpc.stub.StreamObserver<cse.project.grpc.ApiResponse>) responseObserver);
          break;
        case METHODID_GET_SHOP_RATING:
          serviceImpl.getShopRating((cse.project.grpc.Empty) request,
              (io.grpc.stub.StreamObserver<cse.project.grpc.ShopRatingResponse>) responseObserver);
          break;
        default:
          throw new AssertionError();
      }
    }

    @java.lang.Override
    @java.lang.SuppressWarnings("unchecked")
    public io.grpc.stub.StreamObserver<Req> invoke(
        io.grpc.stub.StreamObserver<Resp> responseObserver) {
      switch (methodId) {
        default:
          throw new AssertionError();
      }
    }
  }

  private static abstract class RatingServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoFileDescriptorSupplier, io.grpc.protobuf.ProtoServiceDescriptorSupplier {
    RatingServiceBaseDescriptorSupplier() {}

    @java.lang.Override
    public com.google.protobuf.Descriptors.FileDescriptor getFileDescriptor() {
      return cse.project.grpc.RatingServiceOuterClass.getDescriptor();
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.ServiceDescriptor getServiceDescriptor() {
      return getFileDescriptor().findServiceByName("RatingService");
    }
  }

  private static final class RatingServiceFileDescriptorSupplier
      extends RatingServiceBaseDescriptorSupplier {
    RatingServiceFileDescriptorSupplier() {}
  }

  private static final class RatingServiceMethodDescriptorSupplier
      extends RatingServiceBaseDescriptorSupplier
      implements io.grpc.protobuf.ProtoMethodDescriptorSupplier {
    private final String methodName;

    RatingServiceMethodDescriptorSupplier(String methodName) {
      this.methodName = methodName;
    }

    @java.lang.Override
    public com.google.protobuf.Descriptors.MethodDescriptor getMethodDescriptor() {
      return getServiceDescriptor().findMethodByName(methodName);
    }
  }

  private static volatile io.grpc.ServiceDescriptor serviceDescriptor;

  public static io.grpc.ServiceDescriptor getServiceDescriptor() {
    io.grpc.ServiceDescriptor result = serviceDescriptor;
    if (result == null) {
      synchronized (RatingServiceGrpc.class) {
        result = serviceDescriptor;
        if (result == null) {
          serviceDescriptor = result = io.grpc.ServiceDescriptor.newBuilder(SERVICE_NAME)
              .setSchemaDescriptor(new RatingServiceFileDescriptorSupplier())
              .addMethod(getRateProductMethod())
              .addMethod(getGetProductRatingMethod())
              .addMethod(getRateShopMethod())
              .addMethod(getGetShopRatingMethod())
              .build();
        }
      }
    }
    return result;
  }
}
