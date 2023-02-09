//
// Autogenerated by Thrift Compiler (0.16.0)
//
// DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
//
"use strict";

var thrift = require('thrift');
var Thrift = thrift.Thrift;
var Q = thrift.Q;
var Int64 = require('node-int64');


var ttypes = require('./demo_types');
//HELPER FUNCTIONS AND STRUCTURES

var ProductCatalogService_ListProducts_args = function(args) {
};
ProductCatalogService_ListProducts_args.prototype = {};
ProductCatalogService_ListProducts_args.prototype.read = function(input) {
  input.readStructBegin();
  while (true) {
    var ret = input.readFieldBegin();
    var ftype = ret.ftype;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    input.skip(ftype);
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

ProductCatalogService_ListProducts_args.prototype.write = function(output) {
  output.writeStructBegin('ProductCatalogService_ListProducts_args');
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var ProductCatalogService_ListProducts_result = function(args) {
  this.success = null;
  if (args) {
    if (args.success !== undefined && args.success !== null) {
      this.success = Thrift.copyList(args.success, [null]);
    }
  }
};
ProductCatalogService_ListProducts_result.prototype = {};
ProductCatalogService_ListProducts_result.prototype.read = function(input) {
  input.readStructBegin();
  while (true) {
    var ret = input.readFieldBegin();
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid) {
      case 0:
      if (ftype == Thrift.Type.LIST) {
        this.success = [];
        var _rtmp326 = input.readListBegin();
        var _size25 = _rtmp326.size || 0;
        for (var _i27 = 0; _i27 < _size25; ++_i27) {
          var elem28 = null;
          elem28 = new ttypes.Product();
          elem28.read(input);
          this.success.push(elem28);
        }
        input.readListEnd();
      } else {
        input.skip(ftype);
      }
      break;
      case 0:
        input.skip(ftype);
        break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

ProductCatalogService_ListProducts_result.prototype.write = function(output) {
  output.writeStructBegin('ProductCatalogService_ListProducts_result');
  if (this.success !== null && this.success !== undefined) {
    output.writeFieldBegin('success', Thrift.Type.LIST, 0);
    output.writeListBegin(Thrift.Type.STRUCT, this.success.length);
    for (var iter29 in this.success) {
      if (this.success.hasOwnProperty(iter29)) {
        iter29 = this.success[iter29];
        iter29.write(output);
      }
    }
    output.writeListEnd();
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var ProductCatalogService_GetProduct_args = function(args) {
  this.product_id = null;
  if (args) {
    if (args.product_id !== undefined && args.product_id !== null) {
      this.product_id = args.product_id;
    }
  }
};
ProductCatalogService_GetProduct_args.prototype = {};
ProductCatalogService_GetProduct_args.prototype.read = function(input) {
  input.readStructBegin();
  while (true) {
    var ret = input.readFieldBegin();
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid) {
      case 1:
      if (ftype == Thrift.Type.STRING) {
        this.product_id = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 0:
        input.skip(ftype);
        break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

ProductCatalogService_GetProduct_args.prototype.write = function(output) {
  output.writeStructBegin('ProductCatalogService_GetProduct_args');
  if (this.product_id !== null && this.product_id !== undefined) {
    output.writeFieldBegin('product_id', Thrift.Type.STRING, 1);
    output.writeString(this.product_id);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var ProductCatalogService_GetProduct_result = function(args) {
  this.success = null;
  if (args) {
    if (args.success !== undefined && args.success !== null) {
      this.success = new ttypes.Product(args.success);
    }
  }
};
ProductCatalogService_GetProduct_result.prototype = {};
ProductCatalogService_GetProduct_result.prototype.read = function(input) {
  input.readStructBegin();
  while (true) {
    var ret = input.readFieldBegin();
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid) {
      case 0:
      if (ftype == Thrift.Type.STRUCT) {
        this.success = new ttypes.Product();
        this.success.read(input);
      } else {
        input.skip(ftype);
      }
      break;
      case 0:
        input.skip(ftype);
        break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

ProductCatalogService_GetProduct_result.prototype.write = function(output) {
  output.writeStructBegin('ProductCatalogService_GetProduct_result');
  if (this.success !== null && this.success !== undefined) {
    output.writeFieldBegin('success', Thrift.Type.STRUCT, 0);
    this.success.write(output);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var ProductCatalogService_SearchProducts_args = function(args) {
  this.query = null;
  if (args) {
    if (args.query !== undefined && args.query !== null) {
      this.query = args.query;
    }
  }
};
ProductCatalogService_SearchProducts_args.prototype = {};
ProductCatalogService_SearchProducts_args.prototype.read = function(input) {
  input.readStructBegin();
  while (true) {
    var ret = input.readFieldBegin();
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid) {
      case 1:
      if (ftype == Thrift.Type.STRING) {
        this.query = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 0:
        input.skip(ftype);
        break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

ProductCatalogService_SearchProducts_args.prototype.write = function(output) {
  output.writeStructBegin('ProductCatalogService_SearchProducts_args');
  if (this.query !== null && this.query !== undefined) {
    output.writeFieldBegin('query', Thrift.Type.STRING, 1);
    output.writeString(this.query);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var ProductCatalogService_SearchProducts_result = function(args) {
  this.success = null;
  if (args) {
    if (args.success !== undefined && args.success !== null) {
      this.success = Thrift.copyList(args.success, [null]);
    }
  }
};
ProductCatalogService_SearchProducts_result.prototype = {};
ProductCatalogService_SearchProducts_result.prototype.read = function(input) {
  input.readStructBegin();
  while (true) {
    var ret = input.readFieldBegin();
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid) {
      case 0:
      if (ftype == Thrift.Type.LIST) {
        this.success = [];
        var _rtmp331 = input.readListBegin();
        var _size30 = _rtmp331.size || 0;
        for (var _i32 = 0; _i32 < _size30; ++_i32) {
          var elem33 = null;
          elem33 = new ttypes.Product();
          elem33.read(input);
          this.success.push(elem33);
        }
        input.readListEnd();
      } else {
        input.skip(ftype);
      }
      break;
      case 0:
        input.skip(ftype);
        break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

ProductCatalogService_SearchProducts_result.prototype.write = function(output) {
  output.writeStructBegin('ProductCatalogService_SearchProducts_result');
  if (this.success !== null && this.success !== undefined) {
    output.writeFieldBegin('success', Thrift.Type.LIST, 0);
    output.writeListBegin(Thrift.Type.STRUCT, this.success.length);
    for (var iter34 in this.success) {
      if (this.success.hasOwnProperty(iter34)) {
        iter34 = this.success[iter34];
        iter34.write(output);
      }
    }
    output.writeListEnd();
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var ProductCatalogServiceClient = exports.Client = function(output, pClass) {
  this.output = output;
  this.pClass = pClass;
  this._seqid = 0;
  this._reqs = {};
};
ProductCatalogServiceClient.prototype = {};
ProductCatalogServiceClient.prototype.seqid = function() { return this._seqid; };
ProductCatalogServiceClient.prototype.new_seqid = function() { return this._seqid += 1; };

ProductCatalogServiceClient.prototype.ListProducts = function(callback) {
  this._seqid = this.new_seqid();
  if (callback === undefined) {
    var _defer = Q.defer();
    this._reqs[this.seqid()] = function(error, result) {
      if (error) {
        _defer.reject(error);
      } else {
        _defer.resolve(result);
      }
    };
    this.send_ListProducts();
    return _defer.promise;
  } else {
    this._reqs[this.seqid()] = callback;
    this.send_ListProducts();
  }
};

ProductCatalogServiceClient.prototype.send_ListProducts = function() {
  var output = new this.pClass(this.output);
  var args = new ProductCatalogService_ListProducts_args();
  try {
    output.writeMessageBegin('ListProducts', Thrift.MessageType.CALL, this.seqid());
    args.write(output);
    output.writeMessageEnd();
    return this.output.flush();
  }
  catch (e) {
    delete this._reqs[this.seqid()];
    if (typeof output.reset === 'function') {
      output.reset();
    }
    throw e;
  }
};

ProductCatalogServiceClient.prototype.recv_ListProducts = function(input,mtype,rseqid) {
  var callback = this._reqs[rseqid] || function() {};
  delete this._reqs[rseqid];
  if (mtype == Thrift.MessageType.EXCEPTION) {
    var x = new Thrift.TApplicationException();
    x.read(input);
    input.readMessageEnd();
    return callback(x);
  }
  var result = new ProductCatalogService_ListProducts_result();
  result.read(input);
  input.readMessageEnd();

  if (null !== result.success) {
    return callback(null, result.success);
  }
  return callback('ListProducts failed: unknown result');
};

ProductCatalogServiceClient.prototype.GetProduct = function(product_id, callback) {
  this._seqid = this.new_seqid();
  if (callback === undefined) {
    var _defer = Q.defer();
    this._reqs[this.seqid()] = function(error, result) {
      if (error) {
        _defer.reject(error);
      } else {
        _defer.resolve(result);
      }
    };
    this.send_GetProduct(product_id);
    return _defer.promise;
  } else {
    this._reqs[this.seqid()] = callback;
    this.send_GetProduct(product_id);
  }
};

ProductCatalogServiceClient.prototype.send_GetProduct = function(product_id) {
  var output = new this.pClass(this.output);
  var params = {
    product_id: product_id
  };
  var args = new ProductCatalogService_GetProduct_args(params);
  try {
    output.writeMessageBegin('GetProduct', Thrift.MessageType.CALL, this.seqid());
    args.write(output);
    output.writeMessageEnd();
    return this.output.flush();
  }
  catch (e) {
    delete this._reqs[this.seqid()];
    if (typeof output.reset === 'function') {
      output.reset();
    }
    throw e;
  }
};

ProductCatalogServiceClient.prototype.recv_GetProduct = function(input,mtype,rseqid) {
  var callback = this._reqs[rseqid] || function() {};
  delete this._reqs[rseqid];
  if (mtype == Thrift.MessageType.EXCEPTION) {
    var x = new Thrift.TApplicationException();
    x.read(input);
    input.readMessageEnd();
    return callback(x);
  }
  var result = new ProductCatalogService_GetProduct_result();
  result.read(input);
  input.readMessageEnd();

  if (null !== result.success) {
    return callback(null, result.success);
  }
  return callback('GetProduct failed: unknown result');
};

ProductCatalogServiceClient.prototype.SearchProducts = function(query, callback) {
  this._seqid = this.new_seqid();
  if (callback === undefined) {
    var _defer = Q.defer();
    this._reqs[this.seqid()] = function(error, result) {
      if (error) {
        _defer.reject(error);
      } else {
        _defer.resolve(result);
      }
    };
    this.send_SearchProducts(query);
    return _defer.promise;
  } else {
    this._reqs[this.seqid()] = callback;
    this.send_SearchProducts(query);
  }
};

ProductCatalogServiceClient.prototype.send_SearchProducts = function(query) {
  var output = new this.pClass(this.output);
  var params = {
    query: query
  };
  var args = new ProductCatalogService_SearchProducts_args(params);
  try {
    output.writeMessageBegin('SearchProducts', Thrift.MessageType.CALL, this.seqid());
    args.write(output);
    output.writeMessageEnd();
    return this.output.flush();
  }
  catch (e) {
    delete this._reqs[this.seqid()];
    if (typeof output.reset === 'function') {
      output.reset();
    }
    throw e;
  }
};

ProductCatalogServiceClient.prototype.recv_SearchProducts = function(input,mtype,rseqid) {
  var callback = this._reqs[rseqid] || function() {};
  delete this._reqs[rseqid];
  if (mtype == Thrift.MessageType.EXCEPTION) {
    var x = new Thrift.TApplicationException();
    x.read(input);
    input.readMessageEnd();
    return callback(x);
  }
  var result = new ProductCatalogService_SearchProducts_result();
  result.read(input);
  input.readMessageEnd();

  if (null !== result.success) {
    return callback(null, result.success);
  }
  return callback('SearchProducts failed: unknown result');
};
var ProductCatalogServiceProcessor = exports.Processor = function(handler) {
  this._handler = handler;
};
ProductCatalogServiceProcessor.prototype.process = function(input, output) {
  var r = input.readMessageBegin();
  if (this['process_' + r.fname]) {
    return this['process_' + r.fname].call(this, r.rseqid, input, output);
  } else {
    input.skip(Thrift.Type.STRUCT);
    input.readMessageEnd();
    var x = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN_METHOD, 'Unknown function ' + r.fname);
    output.writeMessageBegin(r.fname, Thrift.MessageType.EXCEPTION, r.rseqid);
    x.write(output);
    output.writeMessageEnd();
    output.flush();
  }
};
ProductCatalogServiceProcessor.prototype.process_ListProducts = function(seqid, input, output) {
  var args = new ProductCatalogService_ListProducts_args();
  args.read(input);
  input.readMessageEnd();
  if (this._handler.ListProducts.length === 0) {
    Q.fcall(this._handler.ListProducts.bind(this._handler)
    ).then(function(result) {
      var result_obj = new ProductCatalogService_ListProducts_result({success: result});
      output.writeMessageBegin("ListProducts", Thrift.MessageType.REPLY, seqid);
      result_obj.write(output);
      output.writeMessageEnd();
      output.flush();
    }).catch(function (err) {
      var result;
      result = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN, err.message);
      output.writeMessageBegin("ListProducts", Thrift.MessageType.EXCEPTION, seqid);
      result.write(output);
      output.writeMessageEnd();
      output.flush();
    });
  } else {
    this._handler.ListProducts(function (err, result) {
      var result_obj;
      if ((err === null || typeof err === 'undefined')) {
        result_obj = new ProductCatalogService_ListProducts_result((err !== null || typeof err === 'undefined') ? err : {success: result});
        output.writeMessageBegin("ListProducts", Thrift.MessageType.REPLY, seqid);
      } else {
        result_obj = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN, err.message);
        output.writeMessageBegin("ListProducts", Thrift.MessageType.EXCEPTION, seqid);
      }
      result_obj.write(output);
      output.writeMessageEnd();
      output.flush();
    });
  }
};
ProductCatalogServiceProcessor.prototype.process_GetProduct = function(seqid, input, output) {
  var args = new ProductCatalogService_GetProduct_args();
  args.read(input);
  input.readMessageEnd();
  if (this._handler.GetProduct.length === 1) {
    Q.fcall(this._handler.GetProduct.bind(this._handler),
      args.product_id
    ).then(function(result) {
      var result_obj = new ProductCatalogService_GetProduct_result({success: result});
      output.writeMessageBegin("GetProduct", Thrift.MessageType.REPLY, seqid);
      result_obj.write(output);
      output.writeMessageEnd();
      output.flush();
    }).catch(function (err) {
      var result;
      result = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN, err.message);
      output.writeMessageBegin("GetProduct", Thrift.MessageType.EXCEPTION, seqid);
      result.write(output);
      output.writeMessageEnd();
      output.flush();
    });
  } else {
    this._handler.GetProduct(args.product_id, function (err, result) {
      var result_obj;
      if ((err === null || typeof err === 'undefined')) {
        result_obj = new ProductCatalogService_GetProduct_result((err !== null || typeof err === 'undefined') ? err : {success: result});
        output.writeMessageBegin("GetProduct", Thrift.MessageType.REPLY, seqid);
      } else {
        result_obj = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN, err.message);
        output.writeMessageBegin("GetProduct", Thrift.MessageType.EXCEPTION, seqid);
      }
      result_obj.write(output);
      output.writeMessageEnd();
      output.flush();
    });
  }
};
ProductCatalogServiceProcessor.prototype.process_SearchProducts = function(seqid, input, output) {
  var args = new ProductCatalogService_SearchProducts_args();
  args.read(input);
  input.readMessageEnd();
  if (this._handler.SearchProducts.length === 1) {
    Q.fcall(this._handler.SearchProducts.bind(this._handler),
      args.query
    ).then(function(result) {
      var result_obj = new ProductCatalogService_SearchProducts_result({success: result});
      output.writeMessageBegin("SearchProducts", Thrift.MessageType.REPLY, seqid);
      result_obj.write(output);
      output.writeMessageEnd();
      output.flush();
    }).catch(function (err) {
      var result;
      result = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN, err.message);
      output.writeMessageBegin("SearchProducts", Thrift.MessageType.EXCEPTION, seqid);
      result.write(output);
      output.writeMessageEnd();
      output.flush();
    });
  } else {
    this._handler.SearchProducts(args.query, function (err, result) {
      var result_obj;
      if ((err === null || typeof err === 'undefined')) {
        result_obj = new ProductCatalogService_SearchProducts_result((err !== null || typeof err === 'undefined') ? err : {success: result});
        output.writeMessageBegin("SearchProducts", Thrift.MessageType.REPLY, seqid);
      } else {
        result_obj = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN, err.message);
        output.writeMessageBegin("SearchProducts", Thrift.MessageType.EXCEPTION, seqid);
      }
      result_obj.write(output);
      output.writeMessageEnd();
      output.flush();
    });
  }
};
