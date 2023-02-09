/*
 * Copyright Skyramp Authors 2022
 */
package main

import (
	"fmt"

	"github.com/apache/thrift/lib/go/thrift"
)

type ThriftProtocolType string

const (
	Binary     ThriftProtocolType = "binary"
	Json       ThriftProtocolType = "json"
	SimpleJson ThriftProtocolType = "simplejson"
	Compact    ThriftProtocolType = "compact"
)

type Option struct {
	HttpTransport bool
	HttpUrl       string
	Protocol      ThriftProtocolType
	Buffered      bool
}

func NewDefaultOption() *Option {
	return &Option{
		Protocol:      Binary,
		HttpTransport: true,
		Buffered:      true,
	}
}

var (
	protocolFactoryMap          = make(map[ThriftProtocolType]thrift.TProtocolFactory)
	bufferedTransportFactoryMap = make(map[bool]thrift.TTransportFactory)
)

func init() {
	protocolFactoryMap[Binary] = thrift.NewTBinaryProtocolFactoryConf(nil)
	protocolFactoryMap[Json] = thrift.NewTJSONProtocolFactory()
	protocolFactoryMap[SimpleJson] = thrift.NewTSimpleJSONProtocolFactoryConf(nil)
	protocolFactoryMap[Compact] = thrift.NewTCompactProtocolFactoryConf(nil)
	bufferedTransportFactoryMap[true] = thrift.NewTBufferedTransportFactory(8192)
	bufferedTransportFactoryMap[false] = thrift.NewTTransportFactory()
}

/*
*  Return a new ThriftClient
 */
func NewThriftClient(hostPort string, opt *Option) (client *thrift.TStandardClient, trans thrift.TTransport, err error) {
	protocolFactory := thrift.NewTBinaryProtocolFactoryConf(nil)

	trans, err = thrift.NewTHttpClient(fmt.Sprintf("http://%s%s", hostPort, opt.HttpUrl))
	if opt.Buffered {
		trans = thrift.NewTBufferedTransport(trans, 8192)
	}
	if err != nil {
		return nil, nil, err
	}
	iprot := protocolFactory.GetProtocol(trans)
	oprot := protocolFactory.GetProtocol(trans)
	client = thrift.NewTStandardClient(iprot, oprot)
	return
}
